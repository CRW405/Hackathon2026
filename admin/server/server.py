"""Small Flask backend for the admin demo.

Run this module to start the backend service which accepts swipe and
packet-sniff events and stores them in MongoDB.

Example:
    python admin/server/server.py
"""

from flask import Flask, jsonify

from routes.swipe import server as swipe_routes
from routes.packet import server as packet_routes

server = Flask(__name__)

server.register_blueprint(swipe_routes)
server.register_blueprint(packet_routes)


if __name__ == "__main__":
    server.run(debug=True, port=6000)
