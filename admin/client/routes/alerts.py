from flask import Blueprint, render_template, request
import logging
from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException
import os
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path)
except Exception:
    pass


client = Blueprint("alerts", __name__, url_prefix="/alerts")


@client.route("/", methods=["GET"])
def alerts_page():
    # Pass backend URL to template so client-side JS can post to correct host
    from flask import current_app

    backend = current_app.config.get("BACKEND", os.environ.get("SERVER", "http://localhost:6000"))
    return render_template("alerts.html", backend=backend)


@client.route("/api/alerts/post", methods=["POST"])
def post_alert():
    """Post an alert to the backend server."""
    backend_url = os.environ.get("SERVER", "http://localhost:6000") + "/api/alerts/post"
    data = request.json
    try:
        response = requests.post(backend_url, json=data)
        response.raise_for_status()
        return response.json(), response.status_code
    except RequestException as e:
        logging.error(f"Error posting alert: {e}")
        return {"status": "error", "message": str(e)}, 500