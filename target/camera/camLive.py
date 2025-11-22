"""Lightweight FastAPI-based camera server running a YOLOv8 tracker.

This module runs a background tracker thread that analyzes camera frames
and exposes a small HTTP API to stream the annotated video and provide
JSON tracking data. It is intended as a demo and may require GPU or
native OpenCV support to perform well.

Usage:
    python camera/camLive.py

Warning: This accesses the webcam and performs face/person detection. Use
this only where you have permission to capture video.
"""

import cv2
import threading
import time
import requests
from ultralytics import YOLO
import os

"""Lightweight camera uploader that captures frames and POSTs them to the
backend server.

This script captures frames from a local camera, encodes them to JPEG, and
POSTs them to the admin backend at /api/cameras/post/<camera_id>.
"""

import cv2
import threading
import time
import requests
from ultralytics import YOLO
import os

# --- CONFIGURATION ---
CAMERA_ID = os.getlogin()  # Unique ID for this camera
# The backend admin server listens on port 6000 by default
SERVER_URL = "http://localhost:6000/api/cameras/post/" + CAMERA_ID
CAM_INDEX = 0  # Camera device index


def run_camera():
    print("Loading YOLO Model...")
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    while True:
        success, frame = cap.read()
        if not success:
            continue

        results = model.track(frame, persist=True, classes=0, verbose=False)
        annotated = results[0].plot()

        # Encode to JPEG
        flag, encoded = cv2.imencode(".jpg", annotated)
        if not flag:
            continue

        frame_bytes = encoded.tobytes()

        # POST frame to backend server
        try:
            requests.post(
                SERVER_URL,
                files={"frame": ("frame.jpg", frame_bytes, "image/jpeg")},
                timeout=0.1,
            )
        except requests.exceptions.RequestException:
            # Don't crash if server is temporarily unreachable
            pass

        time.sleep(0.03)  # ~30 FPS


if __name__ == "__main__":
    run_camera()
