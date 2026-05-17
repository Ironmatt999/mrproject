import math
import random
import time
import numpy as np


class PyRPlidarMeasurement:
    """
    Simulates the measurement object returned by pyrplidar.
    """

    def __init__(self, distance, angle, quality, start_flag):
        self.distance = distance
        self.angle = angle
        self.quality = quality
        self.start_flag = start_flag

    def __str__(self):
        return f"Measurement(distance={self.distance:.2f}, angle={self.angle:.2f}, quality={self.quality}, start_flag={self.start_flag})"


class PyRPlidar:
    """
    A simulator class that mimics the interface of pyrplidar's PyRPlidar.
    Generates simulated lidar data based on 2D raycasting within a defined room.
    """

    def __init__(self):
        self.connected = False
        self.motor_running = False
        self.scanning = False

        # Default simple rectangular room (-5000, -5000) to (5000, 5000) in mm
        self.room_segments = [
            ((-1000, -1000), (1000, -1000)),
            ((1000, -1000), (1000, 1000)),
            ((1000, 1000), (-1000, 1000)),
            ((-1000, 1000), (-1000, -1000)),
        ]

        # Robot's simulated pose
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.heading = 0.0  # in degrees

        # Sensor characteristics
        self.noise_std_dev = 5.0  # mm
        self.scan_rate = 5  # Hz (5 rotations per second)
        self.samples_per_rotation = 360  # 1 degree resolution
        self.max_distance = 3000.0

    def connect(self, port="COM1", baudrate=115200, timeout=3):
        print(f"Simulating connection to {port} at {baudrate} baud...")
        self.connected = True
        return True

    def disconnect(self):
        print("Simulating disconnection...")
        self.stop_motor()
        self.connected = False

    def set_motor_pwm(self, speed):
        if not self.connected:
            raise Exception("Lidar not connected")
        print("Simulating motor start...")
        self.motor_running = True

    def stop_motor(self):
        print("Simulating motor stop...")
        self.motor_running = False

    def set_room(self, segments):
        """
        Define the room as a list of line segments.
        Format: [((x1, y1), (x2, y2)), ...]
        """
        self.room_segments = segments

    def set_pose(self, x, y, heading):
        """Set robot pose in mm and degrees."""
        self.pos_x = x
        self.pos_y = y
        self.heading = heading

    def _ray_segment_intersection(self, ray_origin, ray_dir, segment):
        # Ray: origin + t * dir
        # Segment: p1 + u * (p2 - p1)
        p1, p2 = segment
        v1 = p1[0] - ray_origin[0]
        v2 = p1[1] - ray_origin[1]
        v3 = p2[0] - p1[0]
        v4 = p2[1] - p1[1]

        cross = ray_dir[0] * v4 - ray_dir[1] * v3
        if abs(cross) < 1e-6:  # Parallel lines
            return float("inf")

        t = (v1 * v4 - v2 * v3) / cross
        u = (v1 * ray_dir[1] - v2 * ray_dir[0]) / cross

        if t > 0 and 0 <= u <= 1:
            return t
        return float("inf")

    def start_scan(self, scan_type="normal"):
        """Mimics the pyrplidar start_scan method which returns a generator of measurements."""
        if not self.connected:
            raise Exception("Lidar not connected")
        if not self.motor_running:
            raise Exception("Motor is not running")

        print("Simulating scan start...")
        self.scanning = True
        return self._scan_generator()

    def stop(self):
        """Mimics the pyrplidar stop method."""
        print("Simulating scan stop...")
        self.scanning = False

    def _scan_generator(self):
        sleep_time = 1.0 / self.scan_rate / self.samples_per_rotation

        while self.connected and self.motor_running and self.scanning:
            # start_time = time.time()
            angle_step = 360.0 / self.samples_per_rotation

            for i in range(self.samples_per_rotation):
                if not self.scanning:
                    break
                
                # Generate standard normal noise
                noise = np.clip(
                    angle_step * np.abs(np.random.normal(0, 0.2, None)),
                    a_min=0,
                    a_max=1.5 * angle_step,
                )
                local_angle = float(i * angle_step + noise)
                global_angle = (self.heading + local_angle) % 360.0
                rad = math.radians(global_angle)
                ray_dir = (math.cos(rad), math.sin(rad))

                min_dist = float("inf")
                for segment in self.room_segments:
                    dist = self._ray_segment_intersection(
                        (self.pos_x, self.pos_y), ray_dir, segment
                    )
                    if dist < min_dist:
                        min_dist = dist

                dist_with_noise = 0.0
                if min_dist != float("inf"):
                    # Add noise
                    dist_with_noise = min_dist + random.gauss(0, self.noise_std_dev)
                    if (dist_with_noise < 0) or (dist_with_noise > self.max_distance):
                        dist_with_noise = 0

                quality = 15 if dist_with_noise > 0 else 0
                start_flag = True if i == 0 else False

                time.sleep(sleep_time)

                yield PyRPlidarMeasurement(
                    dist_with_noise, local_angle, quality, start_flag
                )

            # Simulate the time it takes for one rotation to mimic data arrival rate
            # elapsed = time.time() - start_time
            # if elapsed < sleep_time:
            #    time.sleep(sleep_time - elapsed)
            # time.sleep(sleep_time)
