import numpy as np

from mrlib.remote_client import RemoteClientBase

class CameraInterface(RemoteClientBase):
    """
    Stub interface for the CameraController.
    Inherits from RemoteClientBase to automate ZeroMQ communication.
    """

    # Common methods
    def ping(self) -> str:
        """Ping interface to verify working"""
        ...

    def log(self, msg: str) -> None:
        """Send msg to log. i.e. print"""
        ...

    # ---------------------------------------------
    # Custom methods
    # ---------------------------------------------

    def connect(self, camera_index: int = 0) -> None:
        """Command: Connect to the camera."""
        ...

    def set_resolution(self, width: int, height: int) -> None:
        """Command: Set resolution."""
        ...

    def set_framerate(self, fps: int) -> None:
        """Command: Set framerate."""
        ...

    def get_jpeg_image(self) -> np.ndarray:
        """RPC: Get the latest JPEG-encoded frame."""
        ...

    def get_raw_image(self) -> np.ndarray:
        """RPC: Get the latest raw frame."""
        ...

    def release(self) -> None:
        """Command: Release the camera."""
        ...