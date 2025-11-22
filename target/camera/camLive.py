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
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from ultralytics import YOLO
import json
import time

# --- Global Variables to Share Data Between Threads ---
# These hold the latest data from the camera thread so the API can read it.
output_frame = None
current_tracking_data = []
lock = threading.Lock()

# Initialize FastAPI
app = FastAPI()


def run_tracker():
    """
    Background thread that continuously reads from the camera,
    runs the AI, and updates the global variables.
    """
    global output_frame, current_tracking_data

    # Load Model
    print("Loading AI Model...")
    model = YOLO("yolov8n.pt")

    # Open Camera (Change index to 0 or 1 as needed)
    cap = cv2.VideoCapture(3)

    if not cap.isOpened():
        cap = cv2.VideoCapture(0)  # Fallback to 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run YOLO Tracking
        results = model.track(frame, persist=True, classes=0, verbose=False)

        # Parse Results for JSON API
        # We extract just the info we need: ID, Confidence, and Bounding Box
        frame_data = []

        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            boxes = results[0].boxes.xyxy.cpu().numpy()  # x1, y1, x2, y2

            for i, person_id in enumerate(ids):
                x1, y1, x2, y2 = boxes[i]
                # Create a clean dictionary for this person
                person_info = {
                    "id": int(person_id),
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "center": [float(x1 + (x2 - x1) / 2), float(y1 + (y2 - y1) / 2)],
                }
                frame_data.append(person_info)

        # Draw the visual boxes on the frame
        annotated_frame = results[0].plot()

        # Update Global State (Thread-Safe)
        with lock:
            current_tracking_data = frame_data
            # Encode the frame to JPEG for streaming
            (flag, encodedImage) = cv2.imencode(".jpg", annotated_frame)
            if flag:
                output_frame = encodedImage.tobytes()

        # Slight sleep to prevent CPU hogging
        time.sleep(0.01)

    cap.release()


def generate_video():
    """Generator function for the video stream"""
    global output_frame
    while True:
        with lock:
            if output_frame is None:
                continue
            # Get the latest frame bytes
            frame_bytes = output_frame

        # Yield the frame in MJPEG format
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")


# --- API Endpoints ---


@app.get("/")
def index():
    return {
        "message": "AI Tracker Running. Go to /video_feed for video or /tracking_data for JSON."
    }


@app.get("/tracking_data")
def get_data():
    """Returns the current locations of all people in the frame as JSON."""
    with lock:
        return {"count": len(current_tracking_data), "people": current_tracking_data}


@app.get("/video_feed")
def video_feed():
    """Returns the visual video stream."""
    return StreamingResponse(
        generate_video(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    # Start the AI loop in a separate background thread
    t = threading.Thread(target=run_tracker)
    t.daemon = True  # Ensures thread dies when main program dies
    t.start()

    # Start the API Server
    # Listen on all interfaces (0.0.0.0) on port 8000
    print("Starting Server at http://localhost:6000")
    uvicorn.run(app, host="0.0.0.0", port=7000)

