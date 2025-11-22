from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from routes.internet import client as internet_routes
from routes.swipes import client as swipes_routes

client = Flask(__name__)


@client.route("/", methods=["GET", "POST"])
def index():
    # Fetch swipe data from the server
    try:
        response = requests.get("http://localhost:6000/api/getSwipes")
        swipes = response.json() if response.status_code == 200 else []
        print(swipes)
    except Exception as e:
        swipes = []
        print(f"Error fetching swipes: {e}")

    return render_template("index.html", swipes=swipes)


client.register_blueprint(internet_routes)
client.register_blueprint(swipes_routes)


if __name__ == "__main__":
    client.run(debug=True, port=5000)
