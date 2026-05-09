
import time

import numpy as np
import cv2

from camera_interface import CameraInterface
#from motion_interface import MotionInterface


# Local host only
# motors_service_req_url="tcp://127.0.0.1:5555"
# motors_service_cmd_url="tcp://127.0.0.1:5556"
# camera_service_req_url="tcp://127.0.0.1:5557"
# camera_service_cmd_url="tcp://127.0.0.1:5558"
# lidarc_service_req_url="tcp://127.0.0.1:5559"
# lidarc_service_cmd_url="tcp://127.0.0.1:5560"

# Public
motors_service_req_url="tcp://66.71.111.249:5555"
motors_service_cmd_url="tcp://66.71.111.249:5556"
camera_service_req_url="tcp://66.71.111.249:5557"
camera_service_cmd_url="tcp://66.71.111.249:5558"
lidarc_service_req_url="tcp://66.71.111.249:5559"
lidarc_service_cmd_url="tcp://66.71.111.249:5560"

#def camera_processing(target_frame_rate, webcam: CameraInterface, rob_motion: MotionInterface | None = None):
def camera_processing(target_frame_rate, webcam: CameraInterface):
    # C
    rob_motion = None

    webcam.connect(0)
    webcam.set_resolution(1280, 720)
    # webcam.set_framerate(30)
    _ = webcam.get_raw_image()

    # Direct code
    # # Webcam variable will hold the USB camera device
    # webcam = cv2.VideoCapture(0) # 0 means first camera found

    # # The OpenCV set function allows us to define the resolution of the camera input
    # # Set to 640x480
    # webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # # the set function also allows us to define a camera frame rate
    # # some hardware does not support this function, comment the line below if it causes issues
    # # webcam.set(cv2.CAP_PROP_FPS, 30)

    # # Grab first frame to setup image pipeline
    # # '_' variable is a boolean to check if frame was detected (ignored), actual frame goes into imageFrame
    # _, imageFrame = webcam.read()

    # Variable to track the last command sent to avoid spamming the motion controller
    last_command = None

    # establish the ranges for red in our color detection
    # red_mask variable will hold a black and white image with pixels that fall within the color range set as white
    red_lower1 = np.array([0, 100, 100], np.uint8)
    red_upper1 = np.array([10, 255, 255], np.uint8)
    red_lower2 = np.array([160, 100, 100], np.uint8)
    red_upper2 = np.array([179, 255, 255], np.uint8)

    # Establish the ranges for yellow in our color detection
    # yellow_mask variable will hold a black and white image with pixels that fall within the color range set as white
    yellow_lower = np.array([15, 100, 50], np.uint8)
    yellow_upper = np.array([42, 255, 255], np.uint8)

    # establish the ranges for green in our color detection
    # green_mask variable will hold a black and white image with pixels that fall within the color range set as white
    green_lower = np.array([53, 25, 25], np.uint8)
    green_upper = np.array([87, 255, 255], np.uint8)

    # establish the ranges for blue in our color detection
    # blue_mask variable will hold a black and white image with pixels that fall within the color range set as white
    blue_lower = np.array([95, 100, 0], np.uint8)
    blue_upper = np.array([158, 255, 255], np.uint8)

    # this "kernel" variable is a 5x5 array filled with 1 in every position
    # when the cv2.dilate function is called it fix small issues in the color detection regions through smoothing
    dilate_kernel = np.ones((5, 5), "uint8")


    # Frame processing
    frame_interval = 1.0 / target_frame_rate
    next_frame = time.perf_counter() + frame_interval

    # Infinite while loop to continuously detect color
    while True:
        # Calculate how much time is left until the next frame
        sleep_time = next_frame - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
        # Set time of the next frame
        next_frame += frame_interval

        # ---------- Image processing ------------------------

        # '_' variable is a boolean to check if frame was detected (ignored), actual frame goes into imageFrame
        # _, imageFrame = webcam.read()
        imageFrame = webcam.get_raw_image()

        # hsvFrame will hold the frame but converted from BGR color space to HSV color space for more accuracy
        # HSV space can set a specific brightness in case we maybe want to detect LEDs (traffic lights) in the future
        hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

        # red color detection
        red_mask1 = cv2.inRange(hsvFrame, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsvFrame, red_lower2, red_upper2)
        red_mask = red_mask1 + red_mask2

        # Yellow color detection
        yellow_mask = cv2.inRange(hsvFrame, yellow_lower, yellow_upper)

        # Green color detection
        green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)

        # Blue color detection
        blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

        # Apply dilation to all masks
        red_mask = cv2.dilate(red_mask, dilate_kernel)
        yellow_mask = cv2.dilate(yellow_mask, dilate_kernel)
        green_mask = cv2.dilate(green_mask, dilate_kernel)
        blue_mask = cv2.dilate(blue_mask, dilate_kernel)

        # Dictionary to store color information
        colors = {
            'red': {'mask': red_mask, 'bgr': (0, 0, 255), 'total_area': 0, 'largest_contour': None},
            'yellow': {'mask': yellow_mask, 'bgr': (0, 255, 255), 'total_area': 0, 'largest_contour': None},
            'green': {'mask': green_mask, 'bgr': (0, 255, 0), 'total_area': 0, 'largest_contour': None},
            'blue': {'mask': blue_mask, 'bgr': (255, 0, 0), 'total_area': 0, 'largest_contour': None}
        }

        # Calculate total area for each color and find largest contour
        for color_name, color_data in colors.items():
            contours, hierarchy = cv2.findContours(color_data['mask'], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            largest_area = 0
            largest_contour = None
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Only consider significant areas
                    color_data['total_area'] += area
                    if area > largest_area:
                        largest_area = area
                        largest_contour = contour
            
            color_data['largest_contour'] = largest_contour

        # Find the color with the largest total area
        dominant_color = None
        max_area = 0
        
        for color_name, color_data in colors.items():
            if color_data['total_area'] > max_area:
                max_area = color_data['total_area']
                dominant_color = color_name

        # Display only the dominant color if it exists
        if dominant_color and colors[dominant_color]['largest_contour'] is not None:
            contour = colors[dominant_color]['largest_contour']
            x, y, w, h = cv2.boundingRect(contour)
            color_bgr = colors[dominant_color]['bgr']
            
            # Draw bounding box
            imageFrame = cv2.rectangle(imageFrame, (x, y), (x + w, y + h), color_bgr, 2)
            
            # Add text label
            label = f"{dominant_color.capitalize()} Detected"
            cv2.putText(imageFrame, label, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, color_bgr)

        # Read and display encoder information on the video feed
        if rob_motion is not None:
            try:
                rob_motion.ping()
                encoders = rob_motion.read_encoders()
                if "error" not in encoders:
                    # Create a semi-transparent overlay for the encoder table
                    overlay = imageFrame.copy()
                    cv2.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.7, imageFrame, 0.3, 0, imageFrame)
                    
                    # Add encoder information text
                    cv2.putText(imageFrame, "Encoder Counts:", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(imageFrame, f"Front Left:  {encoders['FL']:6d}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imageFrame, f"Front Right: {encoders['FR']:6d}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imageFrame, f"Rear Left:   {encoders['RL']:6d}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imageFrame, f"Rear Right:  {encoders['RR']:6d}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                else:
                    # Display error message if encoder reading fails
                    cv2.putText(imageFrame, "Encoder Error", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            except Exception as e:
                cv2.putText(imageFrame, f"Encoder Offline {e}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Store the dominant color in a variable for other purposes
        # This variable will be None if no significant color is detected
        detected_color = dominant_color
        
        # Control robot based on detected color
        if rob_motion is not None:
            try:
                if detected_color == 'red':
                    if last_command != 'red':
                        rob_motion.stop()
                        print("RED detected - Commanded STOPPED")
                elif detected_color == 'green':
                    rob_motion.move_forward()
                    if last_command != 'green':
                        print("GREEN detected - Commanded moving FORWARD")
                elif detected_color == 'yellow':
                    rob_motion.turn_left()  # Counterclockwise
                    if last_command != 'yellow':
                        print("YELLOW detected - Commanded spinning COUNTERCLOCKWISE")
                elif detected_color == 'blue':
                    rob_motion.turn_right()  # Clockwise
                    if last_command != 'blue':
                        print("BLUE detected - Commanded spinning CLOCKWISE")
                elif detected_color is None:
                    if last_command is not None:
                        rob_motion.stop()
                        print("No color detected - Commanded STOPPED")
                
                last_command = detected_color
                
            except Exception as e:
                print(f"Error sending command to rob_motion: {e}")

        cv2.imshow("RGB Color Detection on Webcam 0", imageFrame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if rob_motion is not None:
                rob_motion.stop()
                rob_motion.close()
            webcam.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    # Run just camera processing
    # camera_processing(target_frame_rate=30)
    rob_motion = None

    webcam = CameraInterface(camera_service_req_url, camera_service_cmd_url)

    webcam.ping()

    camera_processing(target_frame_rate=30, webcam=webcam)


