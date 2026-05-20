import time
import serial

class MotionController:
    def __init__(self):
        self.cap = None
        self.serial_port = None

    def connect(self, port='/dev/ttyACM0', baud_rate=57600, timeout=1) -> None:
        """
        If serial_port is provided, use it (for testing).
        Otherwise create a real serial connection.
        """
        self.serial_port = serial.Serial(port, baud_rate, timeout=timeout)
        time.sleep(2)  # Allow time for Arduino to reset
               
    def _send_command(self, command):
        """Send a command to the Arduino and get the response"""
        self.serial_port.reset_input_buffer()
        self.serial_port.write(f"{command}\n".encode())
        time.sleep(0.1)
        
        # Try to read several lines to get the actual response
        for _ in range(5):  # Try reading up to 5 lines
            response = self.serial_port.readline().decode().strip()
            if response and not response.startswith(" "):  # Skip help text lines
                return response
        return "No valid response"

    def _set_velocity(self, fl, fr, rl, rr):
        """Set motor velocities"""
        command = f"m {fl} {fr} {rl} {rr}"
        return self._send_command(command)

    # ---------------------------------------------
    # Public methods to be exposed
    # ---------------------------------------------

    def close(self) -> None:
        """Close the serial connection"""
        self.serial_port.close()

    def stop(self) -> None:
        """Stop all motors"""
        self._set_velocity(0, 0, 0, 0)

    def set_wheel_speeds(self, left_speed, right_speed) -> None:
        """Set the left and right wheel speeds in mm/s"""
        self._set_velocity(left_speed, right_speed, left_speed, right_speed)

    def move_forward(self, speed=10.0) -> None:
        """Move robot forward at the specified speed"""
        self._set_velocity(speed, speed, speed, speed)
        
    def turn_right(self, speed=10.0) -> None:
        """Turn robot right at the specified speed"""
        self._set_velocity(speed, -speed, speed, -speed)
        
    def turn_left(self, speed=10.0) -> None:
        """Turn robot left at the specified speed"""
        self._set_velocity(-speed, speed, -speed, speed)
    
    def read_encoders(self) -> dict:
        """Read encoder values"""
        response = self._send_command("e")
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
    
    def get_position(self) -> tuple[float, float, float]:
        return (0.0, 0.0, 0.0)