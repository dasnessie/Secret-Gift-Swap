from flask import Flask, render_template, redirect, request
from slugify import slugify
import urllib.parse
from utils import get_pairing_with_probabilities

app = Flask(__name__)


@app.route("/", methods=["GET"])
def start():
    return render_template("start.html")


@app.route("/", methods=["POST"])
def route_to_exchange():
    exchange_name = slugify(request.form["exchange_name"])
    exchange_name = urllib.parse.quote_plus(exchange_name)
    # if exchange exists
    if False:
        return redirect(f"/{exchange_name}")
    # else create exchange
    return redirect(f"/{exchange_name}/create")


@app.route("/<exchange_name>/create", methods=["GET"])
def view_create_exchange(exchange_name):
    return render_template("create.html", exchangeName=exchange_name)


@app.route("/<exchange_name>/create", methods=["POST"])
def create_exchange(exchange_name):
    pairing = get_pairing_with_probabilities(participants=["Alice", "Bob", "Carlos"])
    # Put the data in the database
    return redirect(f"/{exchange_name}")


@app.route("/<exchange_name>")
def view_exchange(exchange_name):
    return render_template("exchange-overview.html", exchangeName=exchange_name)


@app.route("/<exchange_name>/results/<participant_name>")
def view_exchange_participant_result(exchange_name, participant_name):
    # Ask user to confirm their name
    return render_template(
        "exchange-user-result.html",
        exchangeName=exchange_name,
        participantName=participant_name,
    )
