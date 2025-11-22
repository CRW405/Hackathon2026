"""Admin client Flask application.

This module exposes `create_app()` which builds and returns a Flask
application configured with the UI blueprints. The app fetches data
from the backend server (default: http://localhost:6000) and renders
templates found in `templates/`.

Contract:
- Inputs: query parameters provided to routes (/ , /swipes, /internet)
- Outputs: rendered templates with `data` or `swipes` / `sniffs` in
    the template context.
"""

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

        from flask import request
        # utils.py lives in the same package folder
        try:
            from utils import filter_items
        except Exception:
            # best-effort import; if running as package adjust import path
            from .utils import filter_items  # type: ignore


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

        # Apply filters from query parameters (GET)
        username = request.args.get("username")
        badge_id = request.args.get("bid")
        website = request.args.get("website")

        # Combine date+time inputs into ISO datetimes if provided. Fall back to
        # legacy `start`/`end` parameters when date inputs are not present.
        sd = request.args.get("start_date")
        st = request.args.get("start_time")
        if sd:
            # if time omitted, treat start as beginning of the day
            start = f"{sd}T{st}" if st else f"{sd}T00:00:00"
        else:
            start = request.args.get("start")

        ed = request.args.get("end_date")
        et = request.args.get("end_time")
        if ed:
            # if time omitted, treat end as inclusive end of the day
            end = f"{ed}T{et}" if et else f"{ed}T23:59:59"
        else:
            end = request.args.get("end")

        if any([username, badge_id, website, start, end]):
            try:
                app.logger.info("Applying filters: username=%s bid=%s website=%s start=%s end=%s", username, badge_id, website, start, end)
                before_count = len(merged_data) if isinstance(merged_data, list) else 0
                sample_ts = [m.get("timestamp") for m in (merged_data[:5] if isinstance(merged_data, list) else [])]
                app.logger.debug("Sample timestamps before filter: %s", sample_ts)

                merged_data = filter_items(
                    merged_data,
                    username=username,
                    badge_id=badge_id,
                    website=website,
                    start=start,
                    end=end,
                )

                after_count = len(merged_data) if isinstance(merged_data, list) else 0
                app.logger.info("Filter applied: before=%s after=%s", before_count, after_count)
            except Exception:
                app.logger.exception("Error applying filters")

        return render_template("index.html", data=merged_data)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
