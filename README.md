# Phase 1: Project Setup and Component Familiarization
## Step 1: Hardware Setup

### Gather Components:
- ESP32-CAM Module
- ESP32-CAM MB Micro USB Module (for easy flashing)
- Buzzer
- Micro USB cable
- Laptop for local processing

### ESP32-CAM Pinout Understanding:
- VCC → 5V
- GND → GND
- U0R → RX
- U0T → TX

### Connect ESP32-CAM to Your Laptop:
- Attach the ESP32-CAM to the MB module.
- Connect the MB module to your laptop via USB.
- Ensure the ESP32-CAM is recognized by your laptop.

## Step 2: Software Installation

### Install Python (if not already installed)
Download from python.org and install.

### Verify installation
```bash
python --version
```

### Set Up Python Virtual Environment
```bash
python -m venv watchover_env
source watchover_env/bin/activate 
 # On Windows, use watchover_env\Scripts\activate
```

### Install Required Libraries
```bash
pip install opencv-python ultralytics paho-mqtt flask
```

### Install Arduino IDE
Download from arduino.cc

### Install ESP32 board support
File → Preferences → Add Board Manager URL: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

Tools → Board → Boards Manager → Search ESP32 → Install

## Step 3: ESP32-CAM Testing

### Flash Basic Camera Web Server Sketch
Open Arduino IDE.

Load Example: File → Examples → ESP32 → Camera → CameraWebServer.

Configure your WiFi credentials in the code.

Select the correct board and COM port:

Tools → Board → AI Thinker ESP32-CAM

Tools → Port → Select the appropriate COM port

Click Upload.

### Access the Video Stream
Open Serial Monitor to get the ESP32-CAM IP address.

Enter the IP address in a browser to see the live feed.

## Next Step: Verify ESP32-CAM Stream Stability

Try this out, and once you’ve confirmed the camera is streaming properly, we’ll move on to building the local video processing system with YOLOv8!

# Phase 2: Local Video Processing with YOLOv8

## Step 4: Set Up YOLOv8 for Local Inference

### Download YOLOv8 Model
Create a folder for your project:
```bash
mkdir watchover
cd watchover
```

Download the YOLOv8 model (we’ll use a pretrained one for now):
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.info()
```

### Capture Video from ESP32-CAM
Create a Python script video_stream.py:
```python
import cv2

esp32_cam_url = 'http://<ESP32_CAM_IP>/stream'
cap = cv2.VideoCapture(esp32_cam_url)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('ESP32-CAM Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

Replace `<ESP32_CAM_IP>` with the IP address of your ESP32-CAM.

Run the script to verify the live video feed.

### Run YOLOv8 Inference on the Stream
Update the script to run object detection:
```python
from ultralytics import YOLO
import cv2

model = YOLO('yolov8n.pt')
esp32_cam_url = 'http://<ESP32_CAM_IP>/stream'
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
```

### Verify Object Detection
Run the script:
```bash
python video_stream.py
```

The live feed should now show boxes and labels for detected objects.

## Next Step: Train YOLOv8 for Fall/Fight Detection

Let me know when your ESP32-CAM stream works with YOLOv8 detections! Once that’s running, we’ll move on to customizing YOLOv8 to detect specific actions like falls and fights.

# Phase 3: Training YOLOv8 for Fall and Fight Detection

## Step 5: Collect and Label Custom Dataset

### Gather Dataset
Collect video clips or images showing falls, fights, and unsafe postures.

You can use public datasets like:
- UR Fall Detection Dataset
- Hockey Fight Dataset

### Split Dataset
Create folders:
```bash
mkdir dataset
cd dataset
mkdir images
cd images
mkdir train val
cd ..
mkdir labels
cd labels
mkdir train val
```

### Label Images with Roboflow or LabelImg
Install LabelImg:
```bash
pip install labelImg
labelImg
```

Annotate images with bounding boxes and save them in YOLO format (class_id x_center y_center width height).

### Create data.yaml
Define the dataset structure:
```yml
train: ./images/train/
val: ./images/val/

nc: 3
names: ['fall', 'fight', 'unsafe_posture']
```

## Step 6: Train the Model

### Train YOLOv8
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.train(data='data.yaml', epochs=50, batch=8)
```

### Monitor Training
YOLOv8 will log the training process and output metrics like accuracy and loss.

### Test the Model
Once training completes, run the model on test videos to verify detection accuracy:
```python
results = model.predict(source='test_video.mp4', show=True)
```

## Next Step: Real-Time Threat Detection & Alerts

Once your model can accurately detect falls and fights, we’ll set up real-time alerts using MQTT, HTTP, and the buzzer! Let me know when your training is done.

# Phase 4: Real-Time Threat Detection & Alerts

## Step 7: Set Up MQTT Communication

### Install MQTT Library (if not already)
```bash
pip install paho-mqtt
```

### Set Up MQTT Broker (Local or Cloud)
For local testing, you can use Mosquitto.

Start the broker:
```bash
mosquitto
```

### Create an MQTT Publisher for Threat Alerts
mqtt_alert.py:
```python
import paho.mqtt.client as mqtt

broker_address = "localhost"
topic = "watchover/alerts"

def send_alert(message):
    client = mqtt.Client()
    client.connect(broker_address, 1883, 60)
    client.publish(topic, message)
    client.disconnect()
```

## Step 8: Integrate Alerts with YOLOv8

### Update the Video Stream Script
```python
from ultralytics import YOLO
import cv2
from mqtt_alert import send_alert

model = YOLO('yolov8n.pt')  # Use your trained model
esp32_cam_url = 'http://<ESP32_CAM_IP>/stream'
cap = cv2.VideoCapture(esp32_cam_url)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    annotated_frame = results[0].plot()

    # Check for detected threats
    for result in results[0].boxes:
        class_id = int(result.cls[0])
        confidence = result.conf[0]

        if confidence > 0.5:
            label = model.names[class_id]
            if label in ['fall', 'fight', 'unsafe_posture']:
                send_alert(f'Threat detected: {label}')

    cv2.imshow('YOLOv8 Detection', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Step 9: Trigger Notifications

### Handle MQTT Messages on ESP32-CAM
In Arduino IDE, add the PubSubClient library.

Example code to receive alerts and trigger a buzzer:
```cpp
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";
const char* mqtt_server = "192.168.1.100";

WiFiClient espClient;
PubSubClient client(espClient);

const int buzzerPin = 5;

void setup() {
    pinMode(buzzerPin, OUTPUT);
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
    client.connect("ESP32_CAM");
    client.subscribe("watchover/alerts");
}

void callback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println("Alert: " + message);

    // Trigger buzzer on threat detection
    if (message.indexOf("Threat detected") >= 0) {
        digitalWrite(buzzerPin, HIGH);
        delay(1000);
        digitalWrite(buzzerPin, LOW);
    }
}

void loop() {
    client.loop();
}
```























Send Email Alerts (Optional)
==========================

Use Python’s smtplib for email notifications.
Add this to mqtt_alert.py:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, body):
    sender_email = "your_email@gmail.com"
    receiver_email = "receiver_email@gmail.com"
    password = "your_email_password"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
```

Next Step: Test the Full System
------------------------------

Run Everything:

*   Start the MQTT broker.
*   Flash the ESP32-CAM with the MQTT subscriber code.
*   Run the YOLOv8 detection script.
*   Verify the System:

    *   Trigger fall or fight actions in front of the ESP32-CAM.
    *   Confirm you get:
        *   Real-time detection
        *   MQTT alert messages
        *   Buzzer response
        *   Email notifications (if set up)

Once this works smoothly, we’ll move to optimizing the system and adding a web interface to monitor everything remotely!

Let me know when you’ve tested this or if you run into any issues!




# UI/UX

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WatchOver Web Interface</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>WatchOver - Live Surveillance Interface</h1>
    </header>

    <main>
        <section class="stream">
            <h2>Live Camera Feed</h2>
            <img id="cameraFeed" src="http://<ESP32_CAM_IP>/stream" alt="Live Camera Feed">
        </section>

        <section class="controls">
            <h2>Controls</h2>
            <button onclick="toggleAlarm()">Toggle Alarm</button>
        </section>

        <section class="logs">
            <h2>Detection Logs</h2>
            <div id="logContainer"></div>
        </section>
    </main>

    <script src="script.js"></script>
</body>
</html>

<!-- styles.css -->
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
        margin: 0;
        padding: 0;
        text-align: center;
    }
    header {
        background-color: #007bff;
        color: #fff;
        padding: 1rem 0;
    }
    .stream img {
        width: 90%;
        max-width: 800px;
        border: 2px solid #007bff;
        border-radius: 8px;
    }
    .controls {
        margin: 20px 0;
    }
    button {
        padding: 10px 20px;
        font-size: 18px;
        background-color: #ff4d4d;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    button:hover {
        background-color: #ff1a1a;
    }
    .logs {
        background: #fff;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        margin: 20px;
    }
</style>

<!-- script.js -->
<script>
    function toggleAlarm() {
        fetch('/toggle-alarm', { method: 'POST' })
            .then(response => response.json())
            .then(data => alert(data.message))
            .catch(error => console.error('Error:', error));
    }

    function fetchLogs() {
        fetch('/logs')
            .then(response => response.json())
            .then(data => {
                const logContainer = document.getElementById('logContainer');
                logContainer.innerHTML = data.logs.map(log => `<p>${log}</p>`).join('');
            });
    }

    setInterval(fetchLogs, 3000);
</script>
```


# Next, let’s connect the interface to the backend! We’ll set up a Python Flask server to handle the live video stream, alarm toggling, and logging. 🚀

## Step 1: Set Up Flask Backend
Create the Flask Project Folder:

```bash
mkdir watchover-web
cd watchover-web
```

Create the Required Files:

```bash
touch app.py
mkdir static templates
cd static
touch styles.css script.js
cd ..
cd templates
touch index.html
```

Move Your HTML, CSS, and JS Files:

Place your HTML content into `templates/index.html`.
Place your CSS content into `static/styles.css`.
Place your JavaScript content into `static/script.js`.

## Step 2: Build the Flask Server (app.py)
```python
from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

alarm_status = False
logs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle-alarm', methods=['POST'])
def toggle_alarm():
    global alarm_status
    alarm_status = not alarm_status
    status = "activated" if alarm_status else "deactivated"
    logs.append(f"{datetime.datetime.now()}: Alarm {status}")
    return jsonify({"message": f"Alarm {status}!"})

@app.route('/logs')
def get_logs():
    return jsonify({"logs": logs[-10:]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Step 3: Organize Your Project Structure
```cpp
watchover-web/
├── static/
│   ├── styles.css
│   └── script.js
├── templates/
│   └── index.html
├── app.py
└── requirements.txt
```

Add dependencies to `requirements.txt`:

```nginx
flask
```

Install them:

```bash
pip install -r requirements.txt
```

## Step 4: Run the Server
```bash
python app.py
```

Access the interface at:

```arduino
http://localhost:5000
```

## Step 5: Test the Interface
Live Feed: Make sure the ESP32-CAM is streaming.
Alarm Toggle: Click the button to toggle the alarm.
Logs: Check the log section for updates every 3 seconds.
Try running this setup and let me know if you face any issues or want enhancements! 🚀

## Step 6: Connect ESP32-CAM to the Web Interface
Flash the ESP32-CAM with Arduino IDE:
Upload a simple stream sketch:

```cpp
#include "esp_camera.h"
#include <WiFi.h>

const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

void startCameraServer();

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("WiFi connected");
    startCameraServer();
}

void loop() {
    delay(10000);
}
```

Get the ESP32-CAM IP Address:
Open the Arduino IDE serial monitor. After connecting, it will show the IP address — replace `<ESP32_CAM_IP>` in the HTML code with that address.

## Step 7: Test the Live Feed & Alarm
Start the Flask server:

```bash
python app.py
```

Open the web interface:
Go to `http://localhost:5000`.

Check the camera feed:
The live stream from the ESP32-CAM should show up.

Test the alarm:
Click the Toggle Alarm button — check the logs to see the status update.

## Step 8: Add Fall/Threat Detection with YOLOv8 (Next Phase)
We’ve built the core interface! Next, we’ll:

Add YOLOv8 for real-time threat detection.
Integrate MQTT for hardware alerts (buzzer).
Display detection results on the interface.
Want me to guide you through adding object detection and making this a complete safety system? Let me know! 🚀

## Step 9: Set Up YOLOv8 on Your Laptop
Create a Python Virtual Environment:

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

Install Required Packages:

```bash
pip install ultralytics opencv-python flask paho-mqtt
```

Test YOLOv8 Installation:
In Python, run:

```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.info()
```

If no errors, you’re good to go!

## Step 10: Connect the ESP32-CAM Stream to YOLOv8
Update your `app.py` backend to process the live video stream!

```python
import cv2
from ultralytics import YOLO
from flask import Response, Flask, render_template
import threading

app = Flask(__name__)

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# ESP32-CAM Stream URL
ESP32_STREAM_URL = 'http://<ESP32_CAM_IP>/stream'

def generate_frames():
    cap = cv2.VideoCapture(ESP32_STREAM_URL)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run YOLOv8 detection
        results = model(frame)

        for r in results:
            frame = r.plot()

        # Encode the frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield frame to stream
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Step 11: Update the HTML for Live Detection
In your HTML:

```html
<img id="cameraFeed" src="/video_feed" alt="Live Detection Feed">
```

Now your interface will show the live stream with YOLOv8 object detection!

## Step 12: Add Threat Detection & Alerts
We’ll set up threat categories (like falls, fights, unsafe postures) and send alerts! Want me to guide you through that part next? Let me know! 🚀



