import numpy as np
import cv2

class CameraController:
    """
    Handles hardware-level interactions with a webcam using OpenCV.
    """
    def __init__(self):
        self.cap = None

    def connect(self, camera_index: int = 0) -> None:
        """Open the connection to the specified camera index."""
        if self.cap is not None:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"[ERROR] Could not open camera {camera_index}")
        else:
            print(f"[INFO] Camera {camera_index} connected.")

    def set_resolution(self, width: int, height: int) -> None:
        """Set the camera resolution."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            print(f"[INFO] Resolution set to {width}x{height}")

    def set_framerate(self, fps: int) -> None:
        """Set the camera framerate."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            print(f"[INFO] Framerate set to {fps}")

    def get_jpeg_image(self) -> np.ndarray:
        """
        Grabs the latest frame and returns it as a JPEG buffer
        Returns an empty buffer if the frame cannot be read.

        Convert back with:
        nparr = np.frombuffer(buffer, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        """
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Encode as JPEG to reduce ZeroMQ bandwidth
                _, buffer = cv2.imencode('.jpg', frame)
                return buffer
        return np.array([])

    def get_raw_image(self) -> np.ndarray:
        """
        Grabs the latest frame and returns it.
        Returns an empty array if the frame cannot be read.
        """
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return np.array([])

    def release(self) -> None:
        """Release the camera hardware."""
        if self.cap:
            self.cap.release()
            self.cap = None
            print("[INFO] Released camera hardware.")