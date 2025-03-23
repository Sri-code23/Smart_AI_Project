# from ultralytics import YOLO
# model = YOLO('yolov8n.pt')
# model.info()
# output : YOLOv8n summary: 129 layers, 3,157,200 parameters, 0 gradients, 8.9 GFLOPs


from ultralytics import YOLO
import cv2
import numpy as np
import requests

# Load the YOLO model
model = YOLO('yolov8n.pt')
esp32_cam_url = 'http://192.168.1.8/capture'  # Adjust as needed

while True:
    try:
        # Request the image from the ESP32-CAM
        response = requests.get(esp32_cam_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Convert the response content to a NumPy array
            nparr = np.frombuffer(response.content, np.uint8)
            # Decode the image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Perform object detection
            results = model(frame)
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow('YOLOv8 Detection', annotated_frame)
        else:
            print(f"Failed to capture image: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()