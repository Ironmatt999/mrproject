from pyrplidar_sim import PyRPlidar

lidar = PyRPlidar()

# Define a 3m x 4m room in millimeters
lidar.set_room(
    [
        ((-1500, 2000), (1500, 1500)),
        ((1500, 1500), (1600, -500)),
        ((1600, -500), (-1300, -500)),
        ((-1300, -800), (-2000, -500)),
        ((-2000, -500), (-1800, 200)),
        ((-1800, 700), (-2000, 800)),
        ((-2000, 800), (-1500, 2000)),
    ]
)


# Position the robot
lidar.set_pose(x=0, y=0, heading=0)

lidar.connect(port="COM3", baudrate=256000, timeout=3)
lidar.start_motor()

# Getting the generator
scan_generator = lidar.start_scan()

# Processing the measurements
for measurement in scan_generator:
    print(f"{measurement.distance = }")
    print(f"{measurement.angle = }")

lidar.stop()
lidar.stop_motor()
lidar.disconnect()
