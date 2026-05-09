import pickle
import inspect
from typing import get_type_hints

import zmq

class RemoteClientBase:
    """
    Generic base class for remote RPC clients.
    It dynamically inspects its subclass for public methods and replaces 
    them with network calls based on their return type hints.
    
    example urls:

    These IP addresses refers to the machine you are currently using.
    It belongs to the 127.0.0.0/8 reserved block and allows services to communicate with
    each other on the same machine without using the physical network interface card (NIC).
    req_url="tcp://127.0.0.1:5555"
    cmd_url="tcp://127.0.0.1:5556"

    There IP addresses is the address of the host machine.
    req_url="tcp://xxx.xxx.xxx.xxx:5555"
    cmd_url="tcp://xxx.xxx.xxx.xxx:5556"
    """
    def __init__(self, req_url, cmd_url, timeout=2000):
        self.req_url = req_url
        self.context = zmq.Context()

        self.socket_req = self.context.socket(zmq.REQ)
        self.socket_req.connect(self.req_url)
        self.socket_req.setsockopt(zmq.RCVTIMEO, timeout)
        self.socket_req.setsockopt(zmq.SNDTIMEO, timeout)

        self.socket_push = self.context.socket(zmq.PUSH)
        self.socket_push.connect(cmd_url)
        self.socket_push.setsockopt(zmq.IMMEDIATE, 1)

        self._bind_stub_methods()

    def _bind_stub_methods(self):
        """
        Dynamically replaces subclass stub methods with network calls.
        Routes to PUSH if return type hint is `None`, else routes to REQ/REP.
        """
        # Get methods defined in the base class so we don't accidentally override them
        base_methods = dir(RemoteClientBase)

        for name, method in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            # Skip private methods and built-in base methods (like shutdown)
            if name.startswith('_') or name in base_methods:
                continue
            
            try:
                hints = get_type_hints(method)
                is_cmd = ('return' in hints and hints['return'] is type(None))
            except Exception:
                is_cmd = False

            # Bind the proxy method to the instance, overriding the stub
            setattr(self, name, self._create_dispatcher(name, is_cmd))

    def _create_dispatcher(self, func_name, is_cmd):
        """Creates a closure that calls the correct network method."""
        def dispatcher(*args, **kwargs):
            if is_cmd:
                return self._send_cmd(func_name, *args, **kwargs)
            else:
                return self._remote_call(func_name, *args, **kwargs)
        return dispatcher

    def shutdown(self):
        self.socket_req.close()
        self.socket_push.close()
        self.context.term()

    def _encode(self, func_name, args, kwargs):
        return pickle.dumps((func_name, args, kwargs))
    
    def _decode(self, message):
        return pickle.loads(message)

    def _remote_call(self, func_name, *args, **kwargs):
        try:
            self.socket_req.send(self._encode(func_name, args, kwargs))
            response = self._decode(self.socket_req.recv())
            if response.get("ok"):
                return response.get("result")
            else:
                raise RuntimeError(response.get("error", "Unknown error"))
        except zmq.error.Again:
            self.socket_req.close()
            self.socket_req = self.context.socket(zmq.REQ)
            self.socket_req.connect(self.req_url)
            raise TimeoutError(f"No response for '{func_name}'")

    def _send_cmd(self, func_name, *args, **kwargs):
        try:
            self.socket_push.send(self._encode(func_name, args, kwargs))
        except zmq.error.Again:
            raise RuntimeError("Command receiver not connected")