from flask import Blueprint, jsonify, render_template, request
import requests

client = Blueprint("swipes", __name__, url_prefix="/swipes")


@client.route("/", methods=["GET"])
def swipes_page():
    try:
        response = requests.get("http://localhost:6000/api/getSwipes")
        swipes = response.json() if response.status_code == 200 else []
        print(swipes)
    except Exception as e:
        swipes = []
        print(f"Error fetching swipes: {e}")

    return render_template("swipes.html", swipes=swipes)
