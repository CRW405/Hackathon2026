import cv2
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from ultralytics import YOLO
import json
import time

# --- Global Variables to Share Data Between Threads ---
output_frame = None
current_tracking_data = []
lock = threading.Lock()

# --- NEW: Persistence Maps for Naming ---
# 1. Stores which numeric ID corresponds to a known name (e.g., {1: "John Doe"})
ID_TO_NAME_MAP = {1: "John Doe"} 
# 2. A simulated list of known names to assign
KNOWN_NAMES_LIST = ["John Doe", "Sarah Connor", "Admin User"]
# 3. Tracks which name has been assigned to an ID
ASSIGNED_NAMES = set()


# Initialize FastAPI
app = FastAPI()

def simulate_recognition(person_id):
    """
    [PLACEHOLDER] This function simulates a call to a face recognition library
    (e.g., dlib, face_recognition) to identify a person based on their cropped face.
    
    In a real application, you would:
    1. Crop the face from the frame using the bbox.
    2. Encode the face.
    3. Compare the encoding against a database of known face encodings.
    """
    global ASSIGNED_NAMES
    
    # We assign the name based on the ID's order of appearance
    # This is a temporary way to demonstrate persistence.
    if len(ASSIGNED_NAMES) < len(KNOWN_NAMES_LIST):
        # Find the first unassigned name
        name_to_assign = next((name for name in KNOWN_NAMES_LIST if name not in ASSIGNED_NAMES), None)
        if name_to_assign:
            ASSIGNED_NAMES.add(name_to_assign)
            return name_to_assign
    
    return f"Guest {person_id}"


def run_tracker():
    """
    Background thread that continuously reads from the camera,
    runs the AI, and updates the global variables.
    """
    global output_frame, current_tracking_data, ID_TO_NAME_MAP

    # Load Model
    print("Loading AI Model...")
    model = YOLO('yolov8n.pt')

    # Open Camera (Change index to 0 or 1 as needed)
    cap = cv2.VideoCapture(3) 
    
    if not cap.isOpened():
        cap = cv2.VideoCapture(0) # Fallback to 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run YOLO Tracking
        # Note: YOLO's tracking IDs are persistent but arbitrary (e.g., starts at 1, then 2, etc.)
        results = model.track(frame, persist=True, classes=0, verbose=False)


        # create local view
        # annotated_frame = results[0].plot()
        # cv2.imshow("YOLOv8 AI Person Tracking", annotated_frame)
        
        frame_data = []
        
        # Check if tracking results are available
        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            boxes = results[0].boxes.xyxy.cpu().numpy() # x1, y1, x2, y2
            
            for i, person_id in enumerate(ids):
                # --- NEW RECOGNITION LOGIC ---
                name = ""
                
                # 1. Check if this ID has been named already
                if person_id in ID_TO_NAME_MAP:
                    name = ID_TO_NAME_MAP[person_id]
                else:
                    # 2. If new ID, simulate face recognition
                    resolved_name = simulate_recognition(person_id)
                    ID_TO_NAME_MAP[person_id] = resolved_name
                    name = resolved_name
                
                # --- END RECOGNITION LOGIC ---

                x1, y1, x2, y2 = boxes[i]
                person_info = {
                    "id": int(person_id),
                    "name": name,  # NEW: Includes the resolved name
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "center": [float(x1 + (x2-x1)/2), float(y1 + (y2-y1)/2)]
                }
                frame_data.append(person_info)

        # Draw the visual boxes on the frame
        # The .plot() function automatically uses the 'name' field if provided in results.
        # Since we are manually managing the names, we'll ensure the name is visible on the plot.
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
    cv2.destroyAllWindows()

def generate_video():
    """Generator function for the video stream"""
    global output_frame
    while True:
        with lock:
            if output_frame is None:
                continue
            frame_bytes = output_frame

        # Yield the frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- API Endpoints ---

@app.get("/")
def index():
    return {"message": "AI Tracker Running. Go to /video_feed for video or /tracking_data for JSON."}

@app.get("/tracking_data")
def get_data():
    """Returns the current locations of all people in the frame as JSON."""
    with lock:
        return {"count": len(current_tracking_data), "people": current_tracking_data}

@app.get("/video_feed")
def video_feed():
    """Returns the visual video stream."""
    return StreamingResponse(generate_video(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    # run local 
    # run_tracker()

    # Start the AI loop in a separate background thread
    t = threading.Thread(target=run_tracker)
    t.daemon = True # Ensures thread dies when main program dies
    t.start()

    # Start the API Server
    print("Starting Server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)