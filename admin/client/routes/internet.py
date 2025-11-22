
from flask import Blueprint, render_template
import logging
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException


client = Blueprint("internet", __name__, url_prefix="/internet")
logger = logging.getLogger("client.internet")


@client.route("/", methods=["GET"])
def internet_page():
    """Render the internet page showing recent network sniff activities.

    The function calls the backend packet sniffing API with a short timeout,
    logs errors, and ensures the template always receives a list.
    """
    sniffs: List[Dict[str, Any]] = []
    try:
        response = requests.get(
            "http://localhost:6000/api/packetSniff/getSniffs", timeout=5
        )
        if response.ok:
            try:
                payload = response.json()
                sniffs = payload.get("data", []) if isinstance(payload, dict) else []
            except ValueError:
                logger.warning("packetSniff endpoint returned non-JSON response")
        else:
            logger.warning(
                "packetSniff endpoint returned status %s", response.status_code
            )
    except RequestException:
        logger.exception("Error fetching sniffs from backend")

    return render_template("internet.html", sniffs=sniffs)
