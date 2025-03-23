from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Train model
model.train(data='data.yaml', epochs=50, batch=8)

# results = model.predict(source='test_video.mp4', show=True)
# results.show()
# results.save()  # or .show(), .crop(), .pandas(), etc.