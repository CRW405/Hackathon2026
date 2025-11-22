"""Routes for the admin client 'swipes' UI.

This blueprint fetches swipe events from the backend server and
renders `swipes.html`. It supports optional query-parameter filters
for username, badge id, and start/end timestamps.
"""

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
    env_path = Path(__file__).resolve().parents[1] / '.env'
    load_dotenv(env_path)
except Exception:
    pass


client = Blueprint("swipes", __name__, url_prefix="/swipes")
logger = logging.getLogger("client.swipes")


@client.route("/", methods=["GET"])
def swipes_page():
    """Render the swipes page with recent badge swipe events.

    Supports optional query-string filters: username, bid, start, end.
    """
    swipes: List[Dict[str, Any]] = []
    try:
        backend = os.environ.get("SERVER", "http://localhost:6000")
        response = requests.get(f"{backend}/api/swipe/get", timeout=5)
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

    # Filters: only username and badge id (date/time filtering removed)
    username: Optional[str] = request.args.get("username")
    bid: Optional[str] = request.args.get("bid")

    if any([username, bid]):
        try:
            try:
                from utils import filter_items
            except Exception:
                from .utils import filter_items  # type: ignore
            before_count = len(swipes) if isinstance(swipes, list) else 0
            sample_ts = [s.get("timestamp") for s in (swipes[:5] if isinstance(swipes, list) else [])]
            logger.info("Applying filters to swipes: username=%s bid=%s before=%s", username, bid, before_count)
            logger.debug("Sample timestamps before filter: %s", sample_ts)

            swipes = filter_items(swipes, username=username, badge_id=bid)

            after_count = len(swipes) if isinstance(swipes, list) else 0
            logger.info("Filter applied: before=%s after=%s", before_count, after_count)
        except Exception:
            logger.exception("Error applying filters to swipes")

    return render_template("swipes.html", swipes=swipes)
