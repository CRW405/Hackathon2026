
"""Routes for the admin client 'internet' (network sniff) UI.

This blueprint fetches recent packet sniff / website host events from the
backend and renders `internet.html`. Query parameters may be used to
filter by username, website, or time-range.
"""

from flask import Blueprint, render_template, request
import logging
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException


client = Blueprint("internet", __name__, url_prefix="/internet")
logger = logging.getLogger("client.internet")


@client.route("/", methods=["GET"])
def internet_page():
    """Render the internet page showing recent network sniff activities.

    Supports optional query-string filters: username, website, start, end.
    """
    sniffs: List[Dict[str, Any]] = []
    try:
        response = requests.get(
            "http://localhost:6000/api/packet/get", timeout=5
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

    # Apply optional filters from query params
    username: Optional[str] = request.args.get("username")
    website: Optional[str] = request.args.get("website")

    # Combine date + time inputs if present, otherwise accept legacy params.
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

    if any([username, website, start, end]):
        try:
            try:
                from utils import filter_items
            except Exception:
                from .utils import filter_items  # type: ignore
            logger.info("Applying filters to sniffs: username=%s website=%s start=%s end=%s", username, website, start, end)
            before_count = len(sniffs) if isinstance(sniffs, list) else 0
            # show sample timestamps for debugging
            sample_ts = [s.get("timestamp") for s in (sniffs[:5] if isinstance(sniffs, list) else [])]
            logger.debug("Sample timestamps before filter: %s", sample_ts)

            sniffs = filter_items(
                sniffs, username=username, website=website, start=start, end=end
            )

            after_count = len(sniffs) if isinstance(sniffs, list) else 0
            logger.info("Filter applied: before=%s after=%s", before_count, after_count)
        except Exception:
            logger.exception("Error applying filters to sniffs")

    return render_template("internet.html", sniffs=sniffs)
