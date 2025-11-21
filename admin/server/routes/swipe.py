from flask import Blueprint, jsonify

server = Blueprint("swipe", __name__)


@server.route("/api/trackSwipe/<BID>", methods=["POST"])
def on_swipe():
    return jsonify({"status": "swipe tracked"})


@server.route("/api/getSwipes", methods=["POST"])
def get_swipes():
    return jsonify({"swipes": []})
