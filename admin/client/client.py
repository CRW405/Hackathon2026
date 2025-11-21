from flask import Flask, render_template, request, redirect, url_for, flash
from routes.internet import client as internet_routes
from routes.swipes import client as swipes_routes

client = Flask(__name__)


@client.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


client.register_blueprint(internet_routes)
client.register_blueprint(swipes_routes)


if __name__ == "__main__":
    client.run(debug=True, port=5000)
