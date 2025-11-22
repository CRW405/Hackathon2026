from flask import Blueprint, jsonify, render_template, request
import requests

client = Blueprint("swipes", __name__, url_prefix="/swipes")


@client.route("/", methods=["GET"])
def swipes_page():
    try:
        response = requests.get("http://localhost:6000/api/getSwipes")
        swipes = response.json().get("data", []) if response.status_code == 200 else []
        swipes = swipes[::-1]
        print(swipes)
    except Exception as e:
        swipes = []
        print(f"Error fetching swipes: {e}")

        swipes = swipes[::-1]

    return render_template("swipes.html", swipes=swipes)
