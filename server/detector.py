from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("models/yolov8n.pt")

def detect_objects(jpeg_bytes):
    # converte JPEG pra imagem
    img_array = np.frombuffer(jpeg_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    results = model(frame, verbose=False)[0]

    person_detected = False
    phone_detected = False

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]

        if label == "person":
            person_detected = True

        # YOLOv8 padrão reconhece "cell phone"
        if label in ["cell phone", "phone", "mobile"]:
            phone_detected = True

    return person_detected, phone_detected
