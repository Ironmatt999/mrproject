from pyrplidar_sim import PyRPlidar

lidar = PyRPlidar()

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

lidar.set_pose(x=0, y=0, heading=0)

lidar.connect(port="COM3", baudrate=115200, timeout=3)
lidar.start_motor()

scan_generator = lidar.start_scan()

current_scans = []
recent_scans = []
prev_angle = None
ave_points_per_scan = 1000
scans_rotation=0
for measurement in scan_generator:
    print(f"{measurement.distance = }")
    print(f"{measurement.angle = }")
    current_scans.append((-measurement.angle, measurement.distance))
    if prev_angle is not None and (prev_angle > 270 and measurement.angle < 90):


    
        recent_scans = current_scans
        current_scans = []



lidar.stop()
lidar.stop_motor()
lidar.disconnect()