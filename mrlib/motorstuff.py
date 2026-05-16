import time
import numpy as np

from types import SimpleNamespace


class RobotState(SimpleNamespace):
    def __init__(self):
        # Position and heading of the robot
        self.x=np.float64(0.0), # mm
        self.y=np.float64(0.0), # mm
        self.theta=np.float64(0.0), # radians, 0 is facing along x-axis, positive is counterclockwise looking down on the robot
        # Velocities in the robot's frame and wheel speeds
        self.vr=np.float64(0.0), # right wheel speed, mm/s
        self.vl=np.float64(0.0), # left wheel speed, mm/s
        self.vs=np.float64(0.0), # linear velocity, mm/s
        self.wheelbase=np.float64(300), # distance between wheels, mm
        # Velocities in world frame, mm/s and radians/s
        self.vx=np.float64(0.0), # mm/s
        self.vy=np.float64(0.0), # mm/s
        self.vtheta=np.float64(0.0) # radians/s
        self.time=np.float64(0.0) # seconds

    def update_position(self):
        t = time.time()
        dt = t - self.time
        self.time = t
        vs = np.average(self.vr, self.vl)
        vx = vs * np.cos(self.theta)
        vy = vs * np.sin(self.theta)
        vtheta = (self.vr - self.vl) / self.wheelbase
        self.x += vx * dt
        self.y += vy * dt
        self.theta += vtheta * dt

    def set_wheel_speeds(self, left_speed, right_speed):
        self.vl = np.float64(left_speed)
        self.vr = np.float64(right_speed)

        