import urllib.parse

from flask import Flask, g, redirect, render_template, request
from flask_babel import Babel, _
from slugify import slugify

from databaseHandler import DatabaseHandler
from exchange import Exchange
from participant import Participant
from utils import get_pairing_with_probabilities

app = Flask(__name__)


def get_locale():
    return request.accept_languages.best_match(["de", "en"])


app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.config["BABEL_DEFAULT_LOCALE"] = "en"
babel = Babel(app, locale_selector=get_locale)


@app.context_processor
def inject_gettext():
    return {"_": _}


def get_db():
    if "db" not in g:
        g.db = DatabaseHandler()
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close_connection()


@app.route("/", methods=["GET"])
def start():
    return render_template("start.html")


@app.route("/", methods=["POST"])
def route_to_exchange():
    exchange_name = slugify(request.form["exchange_name"])
    exchange_name = urllib.parse.quote_plus(exchange_name)
    db = get_db()
    # if exchange exists
    if db.exchange_exists(exchange_name):
        return redirect(f"/{exchange_name}")
    # else create exchange
    return redirect(f"/{exchange_name}/create")


@app.route("/<exchange_name>/create", methods=["GET"])
def view_create_exchange(exchange_name):
    return render_template("create.html", exchangeName=exchange_name)


@app.route("/<exchange_name>/create", methods=["POST"])
def create_exchange(exchange_name):
    participants = [Participant("Alice"), Participant("Bob"), Participant("Carlos")]
    pairing = get_pairing_with_probabilities(participants)
    exchange = Exchange(exchange_name, participants, [], pairing)
    db = get_db()
    db.create_exchange(exchange, participants, [], pairing)
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
