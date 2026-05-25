import threading
import time
import numpy as np
from pyrplidar import PyRPlidar

class LidarController:
    """
    Manages LiDAR hardware and provides thread-safe access to the latest scan data.
    """
    
    def __init__(self):
        self.lidar = PyRPlidar()
        self.running = False
        self.motor_started = False
        self.worker_thread = None
        self._data_lock = threading.Lock()
        self.latest_scan_set = np.array([])

    def connect(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: int = 3) -> None:
        """Connect to the LiDAR sensor and start the background data thread."""
        self.lidar.connect(port=port, baudrate=baudrate, timeout=timeout)
        self.running = True
        self.motor_started = False
        print(f"[INFO] LiDAR connected on {port}")

    def _lidar_worker(self):
        """Background thread to continuously grab scans from the sensor."""
        Max_points_per_set = 3000
        a_scan_set = np.empty((Max_points_per_set, 2))  # To store the latest scan as an array of (angle, distance) pairs
        n = 0
        prior_running_angle = 0
        running_angle = 0
        scan_generator = self.lidar.start_scan()
        while not self.motor_started:
            time.sleep(0.2)

        for scan in scan_generator():
            if not self.running:
                break
            # Get from the scan point
            dist = scan.distance
            angle = scan.angle

            if n < Max_points_per_set:
                a_scan_set[n,0] = dist
                a_scan_set[n,1] = angle
                # Update count
                n += 1
            # Calculate new running angle
            running_angle = 0.9 * prior_running_angle + 0.1 * angle
            # Check if complete set
            if prior_running_angle > 180 and running_angle < 180:
                # # Update the latest scan in a thread-safe manner
                with self._data_lock:
                    self.latest_scan_set = a_scan_set[:n,:]
                # Make new object
                a_scan_set = np.empty((Max_points_per_set, 2)) 
                # Reset count
                n = 0

            #Update running angle
            prior_running_angle = running_angle

    def set_motor_pwm(self, pwm: int) -> None:
        """Set the motor speed (typically 600 for standard rotation)."""
        self.lidar.set_motor_pwm(pwm)
        time.sleep(0.2)
        self.motor_started = True
        print(f"[INFO] LiDAR motor PWM set to {pwm}")
        time.sleep(2)  # Give the motor a moment to start before we begin scanning
        self.worker_thread = threading.Thread(target=self._lidar_worker, daemon=True)
        self.worker_thread.start()


    def get_scan(self) -> np.ndarray:
        """
        RPC Method: Returns the most recent scan data.
        Returns an empty np.ndarray if no data is available.
        """
        with self._data_lock:
            return self.latest_scan_set

    def close(self) -> None:
        """Stop the motor and disconnect the sensor."""
        self.running = False
        if self.lidar:
            self.lidar.stop()
            self.lidar.set_motor_pwm(0)
            self.lidar.disconnect()
        print("[INFO] LiDAR connection closed.")

    def set_room(self, segments):
        """
        Define the room as a list of line segments.
        Format: [((x1, y1), (x2, y2)), ...]
        """
        # self.lidar.set_room(segments)
        pass