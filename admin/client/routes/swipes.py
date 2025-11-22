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


client = Blueprint("swipes", __name__, url_prefix="/swipes")
logger = logging.getLogger("client.swipes")


@client.route("/", methods=["GET"])
def swipes_page():
    """Render the swipes page with recent badge swipe events.

    Supports optional query-string filters: username, bid, start, end.
    """
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

    # Filters
    username: Optional[str] = request.args.get("username")
    bid: Optional[str] = request.args.get("bid")

    sd = request.args.get("start_date")
    st = request.args.get("start_time")
    if sd:
        start = f"{sd}T{st}" if st else f"{sd}T00:00:00"
    else:
        start = request.args.get("start")

    ed = request.args.get("end_date")
    et = request.args.get("end_time")
    if ed:
        end = f"{ed}T{et}" if et else f"{ed}T23:59:59"
    else:
        end = request.args.get("end")

    if any([username, bid, start, end]):
        try:
            try:
                from utils import filter_items
            except Exception:
                from .utils import filter_items  # type: ignore

            logger.info("Applying filters to swipes: username=%s bid=%s start=%s end=%s", username, bid, start, end)
            before_count = len(swipes) if isinstance(swipes, list) else 0
            sample_ts = [s.get("timestamp") for s in (swipes[:5] if isinstance(swipes, list) else [])]
            logger.debug("Sample timestamps before filter: %s", sample_ts)

            swipes = filter_items(swipes, username=username, badge_id=bid, start=start, end=end)

            after_count = len(swipes) if isinstance(swipes, list) else 0
            logger.info("Filter applied: before=%s after=%s", before_count, after_count)
        except Exception:
            logger.exception("Error applying filters to swipes")

    return render_template("swipes.html", swipes=swipes)
