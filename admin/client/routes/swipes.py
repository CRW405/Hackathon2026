from flask import Blueprint, render_template
import logging
from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException


client = Blueprint("swipes", __name__, url_prefix="/swipes")
logger = logging.getLogger("client.swipes")


@client.route("/", methods=["GET"])
def swipes_page():
    """Render the swipes page with recent badge swipe events."""
    swipes: List[Dict[str, Any]] = []
    try:
        response = requests.get("http://localhost:6000/api/getSwipes", timeout=5)
        if response.ok:
            try:
                payload = response.json()
                swipes = payload.get("data", []) if isinstance(payload, dict) else []
            except ValueError:
                logger.warning("getSwipes endpoint returned non-JSON response")
        else:
            logger.warning("getSwipes endpoint returned status %s", response.status_code)
        swipes = swipes[::-1]
    except RequestException:
        logger.exception("Error fetching swipes from backend")

    return render_template("swipes.html", swipes=swipes)
