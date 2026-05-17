import numpy as np
import time

from mrlib.motion_interface import MotionInterface

# Local host only
motors_service_req_url="tcp://127.0.0.1:5555"
motors_service_cmd_url="tcp://127.0.0.1:5556"
camera_service_req_url="tcp://127.0.0.1:5557"
camera_service_cmd_url="tcp://127.0.0.1:5558"
lidarc_service_req_url="tcp://127.0.0.1:5559"
lidarc_service_cmd_url="tcp://127.0.0.1:5560"

# Public
# motors_service_req_url="tcp://192.168.86.33:5555"
# motors_service_cmd_url="tcp://192.168.86.33:5556"
# camera_service_req_url="tcp://192.168.86.33:5557"
# camera_service_cmd_url="tcp://192.168.86.33:5558"
# lidarc_service_req_url="tcp://192.168.86.33:5559"
# lidarc_service_cmd_url="tcp://192.168.86.33:5560"


if __name__ == "__main__":
    # Run just camera processing
    # camera_processing(target_frame_rate=30)

    rob_motion = MotionInterface(motors_service_req_url, motors_service_cmd_url)
    rob_motion.connect()

    x, y, theta = rob_motion.getposition()
    print(f" {x = }, {y = }, {theta = }")
    
    rob_motion.set_wheel_speeds(1, 1)
    
    for i in range(5):
        time.sleep(1)
        x, y, theta = rob_motion.getposition()
        print(f" {x = }, {y = }, {theta = }")


    rob_motion.set_wheel_speeds(1, 1)
    for i in range(5):
        time.sleep(1)
        x, y, theta = rob_motion.getposition()
        print(f" {x = }, {y = }, {theta = }")

    rob_motion.set_wheel_speeds(2, 2)
    for i in range(5):
        time.sleep(1)
        x, y, theta = rob_motion.getposition()
        print(f" {x = }, {y = }, {theta = }")

    rob_motion.set_wheel_speeds(50, 100)
    time.sleep(1)
    rob_motion.set_wheel_speeds(100, -100)
    time.sleep(1)
    rob_motion.stop()
    x, y, theta = rob_motion.getposition()
    print(f" {x = }, {y = }, {theta = }")