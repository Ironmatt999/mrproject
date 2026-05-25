import serial
import time

class RobotController:
    def __init__(self, port='/dev/ttyACM0', baud_rate=57600, timeout=1):
        """Initialize the robot controller with serial connection parameters"""
        self.serial_port = serial.Serial(port, baud_rate, timeout=timeout)
        time.sleep(2)  # Allow time for Arduino to reset and initialize
        
    def close(self):
        """Close the serial connection"""
        self.serial_port.close()
        
    def send_command(self, command):
        """Send a command to the Arduino and get the response"""
        self.serial_port.reset_input_buffer()
        self.serial_port.write(f"{command}\n".encode())
        time.sleep(0.1)
        
        # Try to read several lines to get the actual response
        for _ in range(5):  # Try reading up to 5 lines
            response = self.serial_port.readline().decode().strip()
            if response and not response.startswith(" "):  # Skip help text lines which often start with space
                return response
        
        return "No valid response"
        
    def set_velocity(self, fl, fr, rl, rr):
        """Set motor velocities"""
        command = f"m {fl} {fr} {rl} {rr}"
        return self.send_command(command)
        
    def stop(self):
        """Stop all motors"""
        return self.set_velocity(0, 0, 0, 0)
        
    def move_forward(self, speed=10.0):
        """Move robot forward at the specified speed"""
        return self.set_velocity(speed, speed, speed, speed)
        
    def turn_right(self, speed=10.0):
        """Turn robot right at the specified speed"""
        return self.set_velocity(speed, -speed, speed, -speed)
        
    def turn_left(self, speed=10.0):
        """Turn robot left at the specified speed"""
        return self.set_velocity(-speed, speed, -speed, speed)
    
    def read_encoders(self):
        """Read encoder values"""
        response = self.send_command("e")
        if response:
            try:
                values = list(map(int, response.split()))
                return {
                    "FL": values[0],
                    "FR": values[1],
                    "RL": values[2],
                    "RR": values[3]
                }
            except (ValueError, IndexError):
                return {"error": response}
        return {"error": "No response"}

##################################################
####  PART 3 : Robot Connection        ###########
##################################################


# Initialize robot controller
try:
    robot = RobotController()
    print("Connected to robot")
except Exception as e:
    print(f"Error connecting to robot: {e}")
    robot = None

robot.stop()
time.sleep(1)
robot.move_forward()
time.sleep(2)
robot.stop()
robot.close()
