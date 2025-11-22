from flask import Blueprint, jsonify, request
import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["hackathon"]
swipe_collection = db["packets"]

server = Blueprint("sniff", __name__)


@server.route("/api/packetSniff/postSniffs", methods=["POST"])
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


@server.route("/api/packetSniff/getSniffs", methods=["GET"])
def get_sniffs():
    sniffs = list(swipe_collection.find())
    for sniff in sniffs:
        sniff["_id"] = str(sniff["_id"]) if "_id" in sniff else None
    return jsonify({"status": "success", "data": sniffs})
