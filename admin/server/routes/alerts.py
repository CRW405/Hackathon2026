from flask import Blueprint, jsonify, request
import datetime
import os
from pathlib import Path
from pymongo import MongoClient

# Load .env if present
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)
except Exception:
    pass

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB", "hackathon")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
alert_collection = db["alerts"]

server = Blueprint("alerts", __name__)


@server.route("/api/alerts/post", methods=["POST"])
def alert_post():
    data = request.json  # Get the JSON data from the request body
    alert_type = data.get("type")
    keyword = data.get("keyword")

    insert = {
        "type": alert_type,
        "keyword": keyword,
        "timestamp": datetime.datetime.now(),
    }
    alert_collection.insert_one(insert)
    return jsonify({"status": "success", "message": "Alert recorded"}), 200


# Alias for older client code that used the singular 'alert' path
@server.route("/api/alert/post", methods=["POST"])
def alert_post_alias():
    return alert_post()

@server.route("/api/alerts/get/<alert_type>", methods=["GET"])
def get_alerts(alert_type):
    # Accept alert_type either from the URL parameter or query string
    q_alert_type = request.args.get("alert_type")
    if not alert_type and not q_alert_type:
        return jsonify({"status": "error", "message": "alert_type is required"}), 400

    use_type = alert_type or q_alert_type

    alerts = list(alert_collection.find({"type": use_type}))

    for alert in alerts:
        alert["_id"] = str(alert["_id"]) if "_id" in alert else None
        # Ensure timestamp is serializable (ISO format)
        if "timestamp" in alert and hasattr(alert["timestamp"], "isoformat"):
            alert["timestamp"] = alert["timestamp"].isoformat()

    return jsonify({"status": "success", "alerts": alerts}), 200
