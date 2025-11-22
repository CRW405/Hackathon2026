from flask import Blueprint, render_template, Response, stream_with_context
import requests

client = Blueprint("camera", __name__, template_folder="templates")

# Backend server base URL (admin backend)
BACKEND = "http://localhost:6000"


@client.route("/camera")
def camera_page():
    return render_template("camera.html")


@client.route('/api/cameras/list')
def proxy_list():
    """Proxy /api/cameras/list to the backend so the UI can use same-origin fetches."""
    resp = requests.get(f"{BACKEND}/api/cameras/list", timeout=3)
    return Response(resp.content, status=resp.status_code, mimetype=resp.headers.get('Content-Type', 'application/json'))


@client.route('/api/cameras/stream/<camera_id>')
def proxy_stream(camera_id):
    """Stream MJPEG from backend and relay it to the client (same-origin).

    Uses requests to stream the response and yields bytes to the browser.
    """
    upstream = requests.get(f"{BACKEND}/api/cameras/stream/{camera_id}", stream=True, timeout=5)

    @stream_with_context
    def generate():
        for chunk in upstream.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

    return Response(generate(), mimetype=upstream.headers.get('Content-Type', 'multipart/x-mixed-replace; boundary=frame'))
