import cv2
import numpy as np
from ultralytics import YOLO
from io import BytesIO

model = YOLO("models/yolov8n.pt")

latest_frame = None

def update_frame(jpeg_bytes):
    global latest_frame
    latest_frame = jpeg_bytes

def generate_stream():
    global latest_frame
    while True:
        if latest_frame is None:
            continue

        img_array = np.frombuffer(latest_frame, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        results = model(frame, verbose=False)[0]

        # desenha bounding boxes
        for box in results.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            color = (0, 255, 0) if label == "person" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # converte de volta para JPEG
        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        frame_bytes = jpeg.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )
