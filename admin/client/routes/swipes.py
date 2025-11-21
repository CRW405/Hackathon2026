from flask import Blueprint, jsonify

client = Blueprint("swipes", __name__, url_prefix="/swipes")


@client.route("/", methods=["GET"])
def swipes_page():
    return jsonify({"message": "This is the swipes page."})
