from mrlib.remote_client import RemoteClientBase

class MotionInterface(RemoteClientBase):
    """
    Remote interface for the MotionController.
    Methods returning `None` are sent as fire-and-forget commands (PUSH).
    Methods returning a value are sent as blocking RPC calls (REQ).
    """

    # Common methods
    def ping(self) -> str:
        """Ping interface to verify working"""
        ...

    def log(self, msg: str) -> None:
        """Send msg to log i.e. print"""
        ...

    # ---------------------------------------------
    # Custom methods
    # ---------------------------------------------

    def connect(self, port='/dev/ttyACM0', baud_rate=57600, timeout=1):
        """
        If serial_port is provided, use it (for testing).
        Otherwise create a real serial connection.
        """
        ...
        
    def set_wheel_speeds(self, left_speed, right_speed) -> None:
        """Set speed"""
        ...

    def read_encoders(self) -> dict:
        ...

    def close(self) -> None:
        """Close the serial connection"""
        ...

    def stop(self) -> None:
        """Stop all motors"""
        ...

    def move_forward(self, speed: float = 10.0) -> None:
        """Move robot forward at the specified speed"""
        ...

    def turn_right(self, speed: float = 10.0) -> None:
        """Turn robot right at the specified speed"""
        ...

    def turn_left(self, speed: float = 10.0) -> None:
        """Turn robot left at the specified speed"""
        ...
    
    def get_position(self) -> tuple[float,float,float]:
        """Get position"""
        ...