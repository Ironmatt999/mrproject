import numpy as np
from mrlib.remote_client import RemoteClientBase

class LidarInterface(RemoteClientBase):
    """
    Stub interface for the LidarController.
    Methods with '-> None' are fire-and-forget (PUSH).
    Methods with '-> dict' are blocking RPC calls (REQ).
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

    def connect(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: int = 3) -> None:
        """Command: Initialize connection and background thread."""
        ...

    def set_motor_pwm(self, pwm: int) -> None:
        """Command: Adjust motor speed."""
        ...

    def get_scan(self) -> np.ndarray:
        """RPC: Retrieve the latest measurement np.ndarray."""
        ...

    def close(self) -> None:
        """Command: Stop hardware and disconnect."""
        ...
    
    def set_room(self, segments) -> None:
        """
        Define the room as a list of line segments.
        Format: [((x1, y1), (x2, y2)), ...]
        """
        ...