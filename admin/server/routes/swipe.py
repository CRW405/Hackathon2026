"""Server routes for handling badge swipe events.

This module exposes two endpoints consumed by the client UI and the
badge-reader script:

- POST /api/trackSwipe/  -> expects JSON with keys `first`, `last`, `bid`
- GET  /api/getSwipes    -> returns stored swipe documents

Data is persisted into a local MongoDB database named `hackathon`.
"""

from flask import Blueprint, jsonify, request
import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["hackathon"]
swipe_collection = db["swipes"]

server = Blueprint("swipe", __name__)


@server.route("/api/trackSwipe/", methods=["POST"])
def on_swipe():
    data = request.json  # Get the JSON data from the request body

    first = data.get("first")
    last = data.get("last")
    bid = data.get("bid")

    insert = {
        "first": first,
        "last": last,
        "bid": bid,
        "timestamp": datetime.datetime.now(),
    }

    swipe_collection.insert_one(insert)

    return jsonify({"status": "success", "message": "Swipe recorded"}), 200


@server.route("/api/getSwipes", methods=["GET"])
def get_swipes():
    swipes = list(swipe_collection.find())
    for swipe in swipes:
        swipe["_id"] = str(swipe["_id"]) if "_id" in swipe else None
        # Ensure timestamp is serializable (ISO format)
        if "timestamp" in swipe and hasattr(swipe["timestamp"], "isoformat"):
            swipe["timestamp"] = swipe["timestamp"].isoformat()
    return jsonify({"status": "success", "data": swipes})
