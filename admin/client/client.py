from flask import Flask, render_template
import logging
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException
from routes.internet import client as internet_routes
from routes.swipes import client as swipes_routes


def create_app() -> Flask:
    app = Flask(__name__)

    # Setup logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # Register blueprints
    app.register_blueprint(internet_routes)
    app.register_blueprint(swipes_routes)

    @app.route("/", methods=["GET", "POST"])
    def index():
        """Homepage that aggregates swipes and network sniffs.

        Returns a combined list sorted by timestamp (newest first).
        """

        def fetch_data(url: str) -> Dict[str, Any] | List[Any]:
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                app.logger.error("Failed to fetch data from %s: %s", url, str(e))
                return []

        # Fetch swipe data
        swipes_response = fetch_data("http://localhost:6000/api/getSwipes")
        swipes = swipes_response.get("data", []) if isinstance(swipes_response, dict) else []

        # Fetch sniff data
        sniffs_response = fetch_data(
            "http://localhost:6000/api/packetSniff/getSniffs"
        )
        sniffs = sniffs_response.get("data", []) if isinstance(sniffs_response, dict) else []

        # Combine and sort swipes and sniffs data
        merged_data: List[Dict[str, Any]] = []
        try:
            merged_data = [
                {"type": "swipe", **swipe}
                for swipe in swipes
                if isinstance(swipe, dict) and "timestamp" in swipe
            ]
            merged_data += [
                {"type": "sniff", **sniff}
                for sniff in sniffs
                if isinstance(sniff, dict) and "timestamp" in sniff
            ]
            merged_data.sort(key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            app.logger.error("Error merging and sorting data: %s", str(e))
            merged_data = []

        return render_template("index.html", data=merged_data)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
