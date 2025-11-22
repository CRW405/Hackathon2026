import cv2
from ultralytics import YOLO


def main():
    # 1. Load the YOLOv8 model
    # 'yolov8n.pt' is the "nano" version. It's the fastest and lightest,
    # making it ideal for real-time CPU tracking.
    print("Loading AI Model...")
    model = YOLO("yolov8n.pt")

    # 2. Initialize the Webcam
    # '0' is usually the default webcam. Change to '1' if you have an external one.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting Tracking... Press 'q' to exit.")

    while True:
        # Read a frame from the webcam
        success, frame = cap.read()

        if not success:
            print("Failed to read frame from webcam.")
            break

        # 3. Run YOLOv8 Tracking
        # persist=True: Tells the AI that this frame is related to the previous one,
        #               allowing it to keep the same ID for the same person.
        # classes=0: Filter specifically for class '0', which is 'person' in the COCO dataset.
        # conf=0.5: Only detect if 50% confident.

        # results = model.track(frame, persist=True, classes=0, conf=0.5, verbose=False)
        results = model.track(frame, persist=True, conf=0.5, verbose=False)

        # 4. Visualize the results
        # .plot() draws the bounding boxes and ID numbers automatically
        annotated_frame = results[0].plot()

        # Display the frame
        cv2.imshow("YOLOv8 AI Person Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

