from flask import Flask, jsonify

from routes.swipe import server as swipe_routes
from routes.packet import server as packet_routes

server = Flask(__name__)


@server.route("/api/placeholder", methods=["GET"])
def placeholder_api():
    return jsonify({"message": "This is a placeholder API endpoint."})


if __name__ == "__main__":
    server.run(debug=True, port=6000)
