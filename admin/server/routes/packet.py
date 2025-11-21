from flask import Blueprint, jsonify

server = Blueprint("packet", __name__)


@server.route("/api/trackPacket/<BID>/<timestamp>/<domain>", methods=["POST"])
def on_packet(BID, timestamp, domain):
    return jsonify({"status": "packet tracked"})
