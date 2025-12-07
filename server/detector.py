from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("models/yolov8n.pt")

ALLOWED = ["person", "cell phone"]

def detect_objects(jpeg_bytes):
    img_array = np.frombuffer(jpeg_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    results = model(frame, verbose=False)[0]

    person_detected = False
    phone_detected = False

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]

        # ignora TUDO exceto person e cell phone
        if label not in ALLOWED:
            continue

        if label == "person":
            person_detected = True

        if label == "cell phone":
            phone_detected = True

    return person_detected, phone_detected
