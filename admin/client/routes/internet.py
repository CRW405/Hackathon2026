from flask import Blueprint, jsonify

client = Blueprint("internet", __name__, url_prefix="/internet")


@client.route("/", methods=["GET"])
def internet_page():
    return jsonify({"message": "This is the internet page."})
