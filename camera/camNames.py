import cv2
from flask import Blueprint, jsonify, request
from ultralytics import YOLO
from pymongo import MongoClient
import os
import threading
import time
import requests

# client = MongoClient("mongodb://localhost:27017/")
# db = client["hackathon"]
# swipe_collection = db["swipes"]

# server = Blueprint("swipe", __name__)
# @server.route("/api/getSwipes", methods=["GET"])




CAMERA_ID = os.getlogin()

try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).resolve().parents[2] / '.env'
except Exception:
    pass

SERVER_BASE = os.environ.get("SERVER", "http://localhost:6000")
SERVER_URL = f"{SERVER_BASE}/api/cameras/post/{CAMERA_ID}"
CAM_INDEX = 0

def run_camera():
    print("Loading AI Model...")
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(3)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)  # Fallback to 0

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # swipe[0] = "unknown"
    try: 
        swipes = list(swipe_collection.find())

        person_names = {index + 1: entry['first'] for index, entry in enumerate(swipes) if 'first' in entry}

        print (person_names)
    except:
        person_names = {
            1: "unknown",
            2: "unknown",
            3: "unknown",
        }

    print("Starting Tracking... Press 'q' to exit.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to read frame from webcam.")
            break

        results = model.track(frame, persist=True, classes=0, conf=0.5)
        id = 100

        if len(results) > 0:
            for result in results:
                for i, box in enumerate(result.boxes):
                    try:
                        id = int(box.id)  # Get detection ID
                    except:
                        id = 100 
                    if id in person_names:  # Check if a name exists for this ID
                        name = person_names[id]
                        bbox = box.xyxy[0]  # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, bbox)  # Convert to integers
                        # Draw the bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    else:
                        name = "unkown person"
                        bbox = box.xyxy[0]  # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, bbox)  # Convert to integers
                        # Draw the bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


        # annotated = results[0].plot()

        # cv2.imshow("YOLOv8 AI Person Tracking", frame)

        flag, encoded = cv2.imencode(".JPG", frame)
        if not flag:
            continue
        frame_bytes = encoded.tobytes()

        try: 
            requests.post(
                SERVER_URL,
                files={"frame": ("frame.jpg", frame_bytes, "image/jpeg")},
                timeout=0.1
            )
        except requests.exceptions.RequestException:
            pass

        time.sleep(0.03)

        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

        # cap.release()
        # cv2.destroyAllWindows()

if __name__ == "__main__":
    run_camera()
