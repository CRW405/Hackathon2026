from flask import Blueprint, jsonify, request, Response
import time
import threading

server = Blueprint("camera", __name__)

# Thread-safe registry storing latest frames for each camera_id
# Start empty; cameras will register themselves by posting frames.
camera_registry: dict[str, bytes] = {}
lock = threading.Lock()


@server.route("/api/cameras/post/<camera_id>", methods=["POST"])
def post_frame(camera_id):
    """Cameras POST frames here.

    Example:
        requests.post("http://localhost:6000/api/cameras/post/cam1", files={"frame": (...)})
    """
    file = request.files.get("frame")
    if file is None:
        return jsonify({"error": "no frame received"}), 400

    frame_bytes = file.read()
    with lock:
        camera_registry[camera_id] = frame_bytes

    return jsonify({"status": "ok"})


def generate_stream(camera_id: str):
    """Provides MJPEG stream to clients."""
    while True:
        with lock:
            frame = camera_registry.get(camera_id, None)

        if frame:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

        time.sleep(0.03)  # ~30 FPS


@server.route("/api/cameras/stream/<camera_id>", methods=["GET"])
def stream_camera(camera_id):
    """Clients access: /api/cameras/stream/<camera_id>"""
    return Response(
        generate_stream(camera_id), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@server.route("/api/cameras/list", methods=["GET"])
def list_cameras():
    """Returns list of currently active cameras."""
    with lock:
        cams = list(camera_registry.keys())
    return jsonify({"cameras": cams})
