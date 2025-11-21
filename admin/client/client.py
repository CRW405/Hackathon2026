from flask import Flask, render_template, request, redirect, url_for, flash

client = Flask(__name__)


@client.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    client.run(debug=True, port=5000)
