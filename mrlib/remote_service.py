import pickle
import traceback
import inspect
from typing import get_type_hints

import zmq

class RemoteService:
    """
    RemoteService hosts any target class instance and exposes its functionality
    over ZeroMQ using two channels based on method return type hints:

    1. REQ/REP (RPC)  -> Methods returning a value or unhinted (blocking)
    2. PULL (commands) -> Methods returning `None` (fire-and-forget)
    
    example urls:

    These IP addresses refers to the machine you are currently using.
    It belongs to the 127.0.0.0/8 reserved block and allows services to communicate with
    each other on the same machine without using the physical network interface card (NIC).
    req_url="tcp://127.0.0.1:5555"
    cmd_url="tcp://127.0.0.1:5556"

    There IP addresses acts as a placeholder or wildcard.
    When a web server or application binds to 0.0.0.0, it listens for traffic on
    all available interfaces to allow traffic from your local machine and from outside.
    req_url="tcp://0.0.0.0:5555"
    cmd_url="tcp://0.0.0.0:5556"
    """

    def __init__(self, target_instance, req_url, cmd_url):
        self.target = target_instance
        self.context = zmq.Context()

        # RPC socket (for calls expecting a response)
        self.socket_rep = self.context.socket(zmq.REP)
        self.socket_rep.bind(req_url)

        # Command socket (fire-and-forget)
        self.socket_pull = self.context.socket(zmq.PULL)
        self.socket_pull.bind(cmd_url)

        # Poller allows us to listen to both sockets
        self.poller = zmq.Poller()
        self.poller.register(self.socket_rep, zmq.POLLIN)
        self.poller.register(self.socket_pull, zmq.POLLIN)

        # Default dispatch tables
        self.rpc_methods = {
            "ping": self._ping,
        }

        self.cmd_methods = {
            "log": self._log,
        }

        # Dynamically register methods from the target instance
        self._register_target_methods()

        self.running = True

    def _register_target_methods(self):
        """Introspects the target instance to build dispatch tables."""
        for name, method in inspect.getmembers(self.target, predicate=inspect.ismethod):
            # Ignore private and special methods
            if name.startswith('_'):
                continue
            
            try:
                hints = get_type_hints(method)
            except Exception:
                hints = {}

            # Route based on return type hint
            if 'return' in hints and hints['return'] is type(None):
                self.cmd_methods[name] = method
                print(f"[INIT] Registered CMD (PULL): {name}")
            else:
                self.rpc_methods[name] = method
                print(f"[INIT] Registered RPC (REQ/REP): {name}")

    # --------------------------
    # Utility
    # --------------------------

    def _encode(self, obj):
        return pickle.dumps(obj)

    def _decode(self, message):
        return pickle.loads(message)

    # --------------------------
    # Built-in methods
    # --------------------------

    def _ping(self):
        return "pong"

    def _log(self, msg):
        print(f"[LOG] {msg}")

    # --------------------------
    # Core loop
    # --------------------------

    def run(self):
        print("RemoteWorker started")
        while self.running:
            events = dict(self.poller.poll(timeout=100))

            # ---- Handle RPC (REQ/REP) ----
            if self.socket_rep in events:
                message = self.socket_rep.recv()
                response = self._handle_rpc(message)
                self.socket_rep.send(self._encode(response))

            # ---- Handle Commands (PULL) ----
            if self.socket_pull in events:
                message = self.socket_pull.recv()
                self._handle_cmd(message)

        self._cleanup()

    # --------------------------
    # Handlers
    # --------------------------

    def _handle_rpc(self, message):
        try:
            func_name, args, kwargs = self._decode(message)

            if func_name not in self.rpc_methods:
                return {"ok": False, "error": f"Unknown RPC: {func_name}"}

            result = self.rpc_methods[func_name](*args, **kwargs)
            return {"ok": True, "result": result}

        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _handle_cmd(self, message):
        try:
            func_name, args, kwargs = self._decode(message)

            if func_name not in self.cmd_methods:
                print(f"[WARN] Unknown command: {func_name}")
                return

            self.cmd_methods[func_name](*args, **kwargs)

        except Exception:
            print("[ERROR] Command execution failed:")
            print(traceback.format_exc())

    # --------------------------
    # Shutdown
    # --------------------------

    def _cleanup(self):
        print("Shutting down RemoteWorker...")
        # Check if the target has its own cleanup mechanism
        if hasattr(self.target, 'close') and callable(self.target.close):
            try:
                self.target.close()
            except Exception as e:
                print(f"[WARN] Error closing target: {e}")

        self.socket_rep.close()
        self.socket_pull.close()
        self.context.term()