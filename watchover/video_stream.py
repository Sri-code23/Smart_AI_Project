# import cv2

# esp32_cam_url = 'http://192.168.1.8/capture'  # Adjust as needed
# cap = cv2.VideoCapture(esp32_cam_url)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#     cv2.imshow('ESP32-CAM Stream', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

# # Replace <ESP32_CAM_IP> with the IP address of your ESP32-CAM.





################### Yolo ########################

from ultralytics import YOLO
import cv2

model = YOLO('yolov8n.pt')
esp32_cam_url = 'http://192.168.1.3/capture'
cap = cv2.VideoCapture(esp32_cam_url)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    annotated_frame = results[0].plot()

    cv2.imshow('YOLOv8 Detection', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()










############# displays the video stream from the ESP32-CAM in a window #############
# import cv2
# import numpy as np
# import requests

# esp32_cam_url = 'http://192.168.1.8/capture'  # Adjust as needed

# while True:
#     try:
#         # Request the image from the ESP32-CAM
#         response = requests.get(esp32_cam_url)
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             # Convert the response content to a NumPy array
#             nparr = np.frombuffer(response.content, np.uint8)
#             # Decode the image
#             frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
#             # Display the image
#             cv2.imshow('ESP32-CAM Stream', frame)
#         else:
#             print(f"Failed to capture image: {response.status_code}")

#     except Exception as e:
#         print(f"An error occurred: {e}")

#     # Break the loop if 'q' is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cv2.destroyAllWindows()




