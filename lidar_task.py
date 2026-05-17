import numpy as np
import pygame
import time

from mrlib.lidar_interface import LidarInterface
#from motion_interface import MotionInterface


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


# Height and width of screen
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
MIN_DISTANCE = 50     # mm (5 cm)
MAX_DISTANCE = 3000   # mm (300 cm)
SCALE = (WIDTH // 2) / MAX_DISTANCE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

def polar_to_cartesian(distance_mm, angle_deg):
        angle_rad = np.deg2rad(angle_deg)
        r = distance_mm * SCALE
        x = CENTER[0] + np.int64(r * np.cos(angle_rad))
        y = CENTER[1] - np.int64(r * np.sin(angle_rad))
        return x, y


def scan_worker(target_frame_rate = 5):

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Lidar")
    # clock = pygame.time.Clock()
    running = True

    font_small = pygame.font.SysFont(None, 20)
    # font_title = pygame.font.SysFont(None, 28, bold=True)

    lidar = LidarInterface(lidarc_service_req_url, lidarc_service_cmd_url)
    lidar.connect(port="/dev/ttyUSB0", baudrate=115200, timeout=3)
    lidar.set_motor_pwm(600)
    time.sleep(0.5)


    # Frame processing
    frame_interval = 1.0 / target_frame_rate
    next_frame = time.perf_counter() + frame_interval

    # FPS tracking
    frame_count = 0
    fps_start_time = time.perf_counter()
    current_fps = 0

    # Infinite while loop to continuously detect color
    while True:
        # Calculate how much time is left until the next frame
        sleep_time = next_frame - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
        # Set time of the next frame
        next_frame += frame_interval


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        scan_set = lidar.get_scan()
        if len(scan_set) > 0:
            xs, ys = polar_to_cartesian(scan_set[:,0], scan_set[:,1])
            N = len(xs)
        else:
            N = 0

        # First fill screen as black
        screen.fill(BLACK)

        # Draw range circles
        for r in range(500, MAX_DISTANCE + 1, 500):
            pygame.draw.circle(screen, DARK_GREEN, CENTER, int(r * SCALE), 1)
            label = font_small.render(f"{r//10} cm", True, WHITE)
            screen.blit(label, (CENTER[0] + int(r * SCALE) - 25, CENTER[1]))

        # Draw points
        for i in range(N):
            dist = scan_set[i,0]
            if dist <= 1000:
                color = RED
            elif dist <= 2000:
                color = YELLOW
            else:
                color = GREEN
            pygame.draw.circle(screen, color, (xs[i], ys[i]), 2)

        # pygame y is flipped
        pygame.display.flip()

        # Calculate actual FPS
        frame_count += 1
        elapsed_time = time.perf_counter() - fps_start_time
        if elapsed_time >= 1.0:  # Update FPS every 1 second
            current_fps = frame_count / elapsed_time
            frame_count = 0
            fps_start_time = time.perf_counter()

        if not running:
            break


    # except KeyboardInterrupt:
    #     print("\nStopped")
    # finally:
    #     lidar.stop()
    #     lidar.set_motor_pwm(0)
    #     lidar.disconnect()
    #     pygame.quit()


if __name__ == "__main__":
    scan_worker()