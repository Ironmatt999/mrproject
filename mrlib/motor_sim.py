import time
import numpy as np

from types import SimpleNamespace


class RobotState(SimpleNamespace):
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Position and heading of the robot
        self.x = 0.0 # mm
        self.y = 0.0 # mm
        self.theta = 0.0 # radians, 0 is facing along x-axis, positive is counterclockwise looking down on the robot
        # Velocities in the robot's frame and wheel speeds
        self.vr = 0.0 # right wheel speed, mm/s
        self.vl = 0.0 # left wheel speed, mm/s
        self.vs = 0.0 # linear velocity, mm/s
        self.wheelbase = 300.0 # distance between wheels, mm
        # Velocities in world frame, mm/s and radians/s
        self.vx= 0.0 # mm/s
        self.vy= 0.0 # mm/s
        self.vtheta= 0.0 # radians/s
        self.time= time.time() # seconds

    def update_position(self):
        t = time.time()
        dt = t - self.time
        self.time = t
        vs =  0.5 * (self.vr + self.vl)
        vx = vs * np.cos(self.theta)
        vy = vs * np.sin(self.theta)
        vtheta = (self.vr - self.vl) / self.wheelbase
        self.x += vx * dt
        self.y += vy * dt
        self.theta += vtheta * dt

    def set_wheel_speeds(self, left_speed, right_speed):
        self.vl = left_speed
        self.vr = right_speed

        