import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("models/yolov8n.pt")

latest_frame = None
distraction_count = 0
distraction_flag = False


def update_frame(jpeg_bytes):
    global latest_frame
    latest_frame = jpeg_bytes


def box_inside(parent, child):
    (px1, py1, px2, py2) = parent
    (cx1, cy1, cx2, cy2) = child
    return cx1 >= px1 and cy1 >= py1 and cx2 <= px2 and cy2 <= py2


def detect_distraction(results):
    persons = []
    phones = []

    for box in results.boxes:
        cls = int(box.cls[0])
        name = model.names[cls]
        coords = list(map(int, box.xyxy[0]))

        if name == "person":
            persons.append(coords)
        elif name in ["cell phone", "mobile phone", "phone"]:
            phones.append(coords)

    for p in persons:
        for c in phones:
            if box_inside(p, c):
                return True
    return False


def generate_stream():
    global latest_frame, distraction_flag, distraction_count

    last_state = False

    while True:
        if latest_frame is None:
            continue

        img_array = np.frombuffer(latest_frame, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        results = model(frame, verbose=False)[0]

        # ---- DISTRACTION ----
        current_state = detect_distraction(results)

        if current_state and not last_state:
            distraction_count += 1

        distraction_flag = current_state
        last_state = current_state

        # ---- DRAW ----
        for box in results.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            if label not in ["person", "cell phone", "mobile phone", "phone"]:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 255, 0) if label == "person" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        text = f"Distraction: {distraction_flag} | Count: {distraction_count}"
        cv2.putText(frame, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpeg.tobytes() +
            b"\r\n"
        )


def get_distraction_data():
    global distraction_flag, distraction_count
    return distraction_flag, distraction_count
