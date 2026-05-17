import threading
import time
from mrlib.camera_controller import CameraController
from mrlib.lidar_controller_fake import LidarController
from mrlib.motion_controller_fake import MotionController
from mrlib.remote_service import RemoteService


# Local host only i.e. all code is running on your computer
motors_service_req_url="tcp://127.0.0.1:5555"
motors_service_cmd_url="tcp://127.0.0.1:5556"
camera_service_req_url="tcp://127.0.0.1:5557"
camera_service_cmd_url="tcp://127.0.0.1:5558"
lidarc_service_req_url="tcp://127.0.0.1:5559"
lidarc_service_cmd_url="tcp://127.0.0.1:5560"

# For public access
# motors_service_req_url="tcp://0.0.0.0:5555"
# motors_service_cmd_url="tcp://0.0.0.0:5556"
# camera_service_req_url="tcp://0.0.0.0:5557"
# camera_service_cmd_url="tcp://0.0.0.0:5558"
# lidarc_service_req_url="tcp://0.0.0.0:5559"
# lidarc_service_cmd_url="tcp://0.0.0.0:5560"

def main(start_motors: bool = False, start_camera: bool = False, start_lidar: bool = False):
    services = []
    threads = []

    # 1. Initialize Motion service
    if start_motors:
        motors = MotionController()
        motor_service = RemoteService(
            target_instance=motors,
            req_url=motors_service_req_url,
            cmd_url=motors_service_cmd_url
        )
        services.append(motor_service)

    # 2. Initialize Camera service
    if start_camera:
        camera = CameraController()
        camera_service = RemoteService(
            target_instance=camera,
            req_url=camera_service_req_url,
            cmd_url=camera_service_cmd_url
        )
        services.append(camera_service)

    # 3. Initialize Lidar service
    if start_lidar:
        lidar = LidarController()
        lidar_service = RemoteService(
            target_instance=lidar,
            req_url=lidarc_service_req_url,
            cmd_url=lidarc_service_cmd_url
        )
        services.append(lidar_service)

    # 4. Start all services in separate threads
    for service in services:
        # We use daemon=True so the program can exit even if threads are stuck,
        # but we will still attempt a graceful shutdown first.
        t = threading.Thread(target=service.run, daemon=True)
        t.start()
        threads.append(t)
        print(f"[SYSTEM] Started service for {type(service.target).__name__}")

    # 5. Keep the main thread alive and handle shutdown
    print(f"\n {len(services)} services are running. Press Ctrl+C to stop everything.")
    try:
        while True:
            time.sleep(1) # Keep main thread from consuming CPU
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutdown initiated by user...")
        
        # Tell all services to stop their internal while loops
        for service in services:
            service.running = False 
        
        # Give threads a moment to finish their last poll and run _cleanup()
        for t in threads:
            t.join(timeout=2.0)
            
        print("[SYSTEM] All services stopped safely.")

if __name__ == "__main__":
    main(start_motors=True, start_camera=True, start_lidar=True)
