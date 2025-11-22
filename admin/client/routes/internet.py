from flask import Blueprint, jsonify, render_template, request
import requests

client = Blueprint("internet", __name__, url_prefix="/internet")


@client.route("/", methods=["GET"])
def internet_page():
    try:
        response = requests.get("http://localhost:6000/api/packetSniff/getSniffs")
        sniffs = response.json().get("data", []) if response.status_code == 200 else []
        print(sniffs)
    except Exception as e:
        sniffs = []
        print(f"Error fetching swipes: {e}")

    return render_template("internet.html", sniffs=sniffs)
