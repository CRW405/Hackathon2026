"""Utility helpers used by the admin client UI.

This module provides tolerant datetime parsing and a small filtering
helper used by the client to filter swipe/sniff event lists by
username, badge id, website and time ranges.

Functions are written to accept flexible timestamp formats: epoch
seconds (int/float or numeric strings), ISO8601 strings (including
trailing 'Z'), and native datetime objects.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse a datetime-ish value into a timezone-aware datetime or naive datetime.

    Handles:
    - numeric epoch seconds (int/float or numeric strings)
    - ISO strings, including those ending with 'Z' (treated as +00:00)
    - returns None if parsing fails
    """
    if value is None:
        return None

    # If it's already a datetime, return it
    if isinstance(value, datetime):
        return value

    # Try numeric epoch
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        vs = str(value).strip()
        if vs == "":
            return None
        # numeric string
        if vs.replace('.', '', 1).isdigit():
            return datetime.fromtimestamp(float(vs), tz=timezone.utc)
    except Exception:
        pass

    # Try ISO parse; handle trailing Z
    try:
        s = str(value)
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _to_naive_utc(dt: datetime) -> datetime:
    """Normalize datetime to naive UTC for safe comparisons."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def within_time_range(item_ts: Any, start: Optional[str], end: Optional[str]) -> bool:
    if not start and not end:
        return True
    if not item_ts:
        return False

    ts = _parse_datetime(item_ts)
    if ts is None:
        return False

    start_dt = _parse_datetime(start) if start else None
    end_dt = _parse_datetime(end) if end else None

    # Normalize to naive UTC for comparison
    try:
        ts_n = _to_naive_utc(ts)
        start_n = _to_naive_utc(start_dt) if start_dt else None
        end_n = _to_naive_utc(end_dt) if end_dt else None
    except Exception:
        return False

    if start_n and ts_n < start_n:
        return False
    if end_n and ts_n > end_n:
        return False
    return True


def filter_items(
    items: Iterable[Dict[str, Any]],
    *,
    username: Optional[str] = None,
    badge_id: Optional[str] = None,
    website: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    username = username.lower() if username else None
    badge_id = badge_id.lower() if badge_id else None
    website = website.lower() if website else None

    for it in items:
        if not isinstance(it, dict):
            continue

        # username filter
        if username:
            uname = str(it.get("username") or it.get("first") or "").lower()
            if username not in uname:
                continue

        # badge id filter
        if badge_id:
            bid = str(it.get("bid") or "").lower()
            if badge_id not in bid:
                continue

        # website filter
        if website:
            w = str(it.get("website") or "").lower()
            if website not in w:
                continue

        # time range filter
        if not within_time_range(it.get("timestamp"), start, end):
            continue

        out.append(it)

    return out
