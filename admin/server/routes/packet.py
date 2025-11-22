"""Server routes for receiving and returning network sniff events.

Endpoints:
- POST /api/packetSniff/postSniffs  -> accepts JSON with username, website, ip_address, source_ip, hostname
- GET  /api/packetSniff/getSniffs   -> returns stored sniff documents

Data is stored in MongoDB in the `packets` collection.
"""

from flask import Blueprint, jsonify, request
import datetime
import os
from pathlib import Path
from pymongo import MongoClient

# Load .env if present
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(env_path)
except Exception:
    pass

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB", "hackathon")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
swipe_collection = db["packets"]

server = Blueprint("sniff", __name__)


@server.route("/api/packet/post", methods=["POST"])
def receive_sniff_data():
    data = request.json  # Get the JSON data from the request body

    # Now you have all the data:
    username = data.get("username")
    website = data.get("website")
    ip_address = data.get("ip_address")
    source_ip = data.get("source_ip")
    hostname = data.get("hostname")

    insert = {
        "username": username,
        "hostname": hostname,
        "website": website,
        "ip_address": ip_address,
        "source_ip": source_ip,
        "timestamp": datetime.datetime.now(),
    }

    swipe_collection.insert_one(insert)

    return jsonify({"status": "success", "message": "Data received"}), 200


@server.route("/api/packet/get", methods=["GET"])
def get_sniffs():
    sniffs = list(swipe_collection.find())
    for sniff in sniffs:
        sniff["_id"] = str(sniff["_id"]) if "_id" in sniff else None
        # Ensure timestamp is serializable (ISO format)
        if "timestamp" in sniff and hasattr(sniff["timestamp"], "isoformat"):
            sniff["timestamp"] = sniff["timestamp"].isoformat()
    return jsonify({"status": "success", "data": sniffs})
