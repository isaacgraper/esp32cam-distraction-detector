# ESP32CAM Distraction Detector

Embedded system using ESP32-CAM and YOLOv3 Tiny to detect pedestrians who are distracted while using their smartphones. The goal is to provide a lightweight, accessible, and efficient real‑time detection solution.

## Setup

Start the server:
```python -m uvicorn server.main:app --host 0.0.0.0 --port 8000```

Start ESP32-CAM:
```cd esp32-cam-web-server/```

You need to double-click the .ino file, select the "AI Thinker ESP32-CAM" board and Upload the file insine the Arduino IDE.

You will see after the compilating, into Tools > Serial Monitor the HTTP POST method, if it's OK.

## Server

You can access: http://192.168.1.35:8000/stream to see the information ESP32-CAM is seeing and also, http://192.168.1.35:8000/dashboard to see the metrics.



