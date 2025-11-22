from flask import Flask, jsonify

from routes.swipe import server as swipe_routes
from routes.packet import server as packet_routes

server = Flask(__name__)

server.register_blueprint(swipe_routes)
server.register_blueprint(packet_routes)

if __name__ == "__main__":
    server.run(debug=True, port=6000)
