import cv2

def list_cameras():
    index = 0
    available_cameras = []
    for index in range(10):  # Check the first 10 indices for connected cameras
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Use DSHOW backend for better performance on Windows
            #cap = cv2.VideoCapture(index, cv2.CAP_MSMF)  # Use MSMF backend for better performance on Windows
            if cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                else:
                    available_cameras.append(index)
            cap.release()
        except:
            pass
    return available_cameras

print(f"Available Camera Indices: {list_cameras()}")
