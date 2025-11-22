from flask import Flask, render_template
import logging

import requests
from requests.exceptions import RequestException
from routes.internet import client as internet_routes
from routes.swipes import client as swipes_routes

# Initialize Flask app
client = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client_app")


@client.route("/", methods=["GET", "POST"])
def index():
    def fetch_data(url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {str(e)}")
            return []

    # Fetch swipe data
    swipes_response = fetch_data("http://localhost:6000/api/getSwipes")
    swipes = (
        swipes_response.get("data", []) if isinstance(swipes_response, dict) else []
    )

    # Fetch sniff data
    sniffs_response = fetch_data("http://localhost:6000/api/packetSniff/getSniffs")
    sniffs = (
        sniffs_response.get("data", []) if isinstance(sniffs_response, dict) else []
    )

    # Combine and sort swipes and sniffs data
    try:
        merged_data = [
            {"type": "swipe", **swipe}
            for swipe in swipes
            if isinstance(swipe, dict) and "timestamp" in swipe
        ] + [
            {"type": "sniff", **sniff}
            for sniff in sniffs
            if isinstance(sniff, dict) and "timestamp" in sniff
        ]
        merged_data.sort(key=lambda x: x["timestamp"])
    except Exception as e:
        logger.error(f"Error merging and sorting data: {str(e)}")
        merged_data = []

    # Pass the combined, sorted data to the template
    merged_data = merged_data[::-1]  # Reverse for descending order
    return render_template("index.html", data=merged_data)


client.register_blueprint(internet_routes)
client.register_blueprint(swipes_routes)


if __name__ == "__main__":
    client.run(debug=True, port=5000)
