from flask import Blueprint, jsonify
import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["hackathon"]
swipe_collection = db["swipes"]

server = Blueprint("swipe", __name__)


@server.route("/api/trackSwipe/<card_info>", methods=["POST"])
def on_swipe(card_info):
    # INPUT: "LAST, FIRS BID"
    now = datetime.datetime.now()
    info = card_info.split(",")
    insert = {
        "last": info[0].strip(),
        "first": info[1].strip(),
        "bid": info[2].strip(),
        "timestamp": now,
    }
    swipe_collection.insert_one(insert)
    insert["_id"] = str(insert["_id"]) if "_id" in insert else None
    return jsonify({"status": "success", "data": insert})


@server.route("/api/getSwipes", methods=["GET"])
def get_swipes():
    swipes = list(swipe_collection.find())
    for swipe in swipes:
        swipe["_id"] = str(swipe["_id"]) if "_id" in swipe else None
    return jsonify({"status": "success", "data": swipes})
