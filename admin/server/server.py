"""Small Flask backend for the admin demo.

Run this module to start the backend service which accepts swipe and
packet-sniff events and stores them in MongoDB.

Example:
    python admin/server/server.py
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
from pathlib import Path

from routes.swipe import server as swipe_routes
from routes.packet import server as packet_routes
from routes.camera import server as camera_routes
from routes.alerts import server as alerts_routes

# Load .env if present
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[1] / '.env'
    load_dotenv(env_path)
except Exception:
    pass

server = Flask(__name__)

# CORS origins: allow the CLIENT env var (or default to http://localhost:3000)
client_origin = os.environ.get("CLIENT", "http://localhost:3000")
# Allow the client dev server and local client app on 5000
CORS(server, origins=[client_origin, "http://127.0.0.1:5000", "http://localhost:5000"])

server.register_blueprint(swipe_routes)
server.register_blueprint(packet_routes)
server.register_blueprint(camera_routes)
server.register_blueprint(alerts_routes)


if __name__ == "__main__":
    backend_port = int(os.environ.get("SERVER_PORT", "6000"))
    server.run(debug=True, port=backend_port)
