import cv2
from ultralytics import YOLO

def main():
    print("Loading AI Model...")
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(3)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)  # Fallback to 0

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting Tracking... Press 'q' to exit.")

    person_names = {
        
    }

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to read frame from webcam.")
            break

        results = model.track(frame, persist=True, classes=0, conf=0.5)

        if len(results) > 0:
            for result in results:
                for i, box in enumerate(result.boxes):
                    id = int(box.id)  # Get detection ID
                    if id in person_names:  # Check if a name exists for this ID
                        name = person_names[id]
                        bbox = box.xyxy[0]  # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, bbox)  # Convert to integers
                        # Draw the bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.imshow("YOLOv8 AI Person Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
