import time
import platform

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
        
        current_os = platform.system()
        if current_os == "Windows":
            print("Running on Windows")
            # FOR WINDOWS, using DSHOW backend can improve performance and compatibility with certain cameras
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        elif current_os == "Linux":
            print("Running on Linux")
            # For Linux, using V4L2 backend can improve performance and compatibility with certain cameras
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2) # , cv2.CAP_VFW
        elif current_os == "Darwin":
            print("Running on macOS")
            # For Linux, using V4L2 backend can improve performance and compatibility with certain cameras
            self.cap = cv2.VideoCapture(camera_index) # ???

        if not self.cap.isOpened():
            print(f"[ERROR] Could not open camera {camera_index}")
        else:
            print(f"[INFO] Camera {camera_index} connected.")

    def set_resolution(self, width: int, height: int) -> None:
        """Set the camera resolution."""
        if self.cap:
            # TODO: If broke comment out next line!
            # self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            time.sleep(0.05)  # Allow time for the camera to adjust settings
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            print(f"[INFO] Resolution set to {width}x{height}")
            time.sleep(0.05)  # Allow time for the camera to adjust settings
            # Get and print the actual resolution to confirm
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"[INFO] Actual resolution is {actual_width}x{actual_height}")




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