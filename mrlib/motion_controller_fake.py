import time
import threading
from mrlib.motor_sim import RobotState

class MotionController:
    def __init__(self):
        self.cap = None
        self.connected = True
        self.motor = RobotState()
        self.worker_thread = threading.Thread(target=self._worker_thread, daemon=True)
        self.worker_thread.start()

    def _worker_thread(self):
        """Background thread to continuously update the robot's position"""
        while self.connected:
            self.motor.update_position()
            time.sleep(0.1)

    def connect(self, port='/dev/ttyACM0', baudrate=57600, timeout=3, serial_port=None):
        print(f"Simulating connection to {port} at {baudrate} baud...")
        self.motor.reset()
        return True
    
    # ---------------------------------------------
    # Public methods to be exposed
    # ---------------------------------------------

    def close(self) -> None:
        """Close the serial connection"""
        pass
        
    def stop(self) -> None:
        """Stop all motors"""
        self.motor.set_wheel_speeds(0, 0)
    
    def set_wheel_speeds(self, left_speed, right_speed) -> None:
        """Set the left and right wheel speeds in mm/s"""
        self.motor.set_wheel_speeds(left_speed, right_speed)

    def move_forward(self, speed=10.0) -> None:
        """Move robot forward at the specified speed"""
        self.motor.set_wheel_speeds(speed, speed)
        
    def turn_right(self, speed=10.0) -> None:
        """Turn robot right at the specified speed"""
        self.motor.set_wheel_speeds(speed, -speed)
        
    def turn_left(self, speed=10.0) -> None:
        """Turn robot left at the specified speed"""
        self.motor.set_wheel_speeds(-speed, speed)
    
    def get_position(self) -> tuple[float,float,float]:
        """Get position"""
        return (self.motor.x, self.motor.y, self.motor.theta * 180 / 3.14159)
    
    # def read_encoders(self) -> dict:
    #     """Read encoder values"""
    #     response = self._send_command("e")
    #     if response:
    #         try:
    #             values = list(map(int, response.split()))
    #             return {
    #                 "FL": values[0],
    #                 "FR": values[1],
    #                 "RL": values[2],
    #                 "RR": values[3]
    #             }
    #         except (ValueError, IndexError):
    #             return {"error": response}
    #     return {"error": "No response"}