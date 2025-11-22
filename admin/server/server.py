"""Small Flask backend for the admin demo.

Run this module to start the backend service which accepts swipe and
packet-sniff events and stores them in MongoDB.

Example:
    python admin/server/server.py
"""

from flask import Flask, jsonify
from flask_cors import CORS

from routes.swipe import server as swipe_routes
from routes.packet import server as packet_routes
from routes.camera import server as camera_routes

server = Flask(__name__)
# Allow cross-origin requests from the client running on port 5000
CORS(server, origins=["http://localhost:5000", "http://127.0.0.1:5000"])

server.register_blueprint(swipe_routes)
server.register_blueprint(packet_routes)
server.register_blueprint(camera_routes)


if __name__ == "__main__":
    server.run(debug=True, port=6000)
