import urllib.parse
from sqlite3 import IntegrityError

from flask import (
    Flask,
    Response,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
)
from flask_babel import Babel, _
from flask_babel_js import BabelJS
from slugify import slugify

from constraint import Constraint
from databaseHandler import DatabaseHandler
from exchange import Exchange
from participant import (
    Participant,
)
from utils import get_pairing_with_probabilities

app = Flask(__name__)


def get_locale():
    return request.accept_languages.best_match(["de", "en"])


app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.config["BABEL_DEFAULT_LOCALE"] = "en"
babel = Babel(app, locale_selector=get_locale)
babel_js = BabelJS(app)

app.jinja_env.globals.update(zip=zip)  # Let me use zip in jinja
app.jinja_env.filters["quote_plus"] = lambda u: urllib.parse.quote_plus(u)


@app.context_processor
def inject_gettext():
    return {"_": _}


def get_db():
    if "db" not in g:
        g.db = DatabaseHandler()
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close_connection()


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


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
        return redirect(f"/{exchange_name}/")
    # else create exchange
    return redirect(f"/{exchange_name}/create/")


@app.route("/check_name")
def check_name():
    name = request.args.get("name", "").strip()
    db = get_db()
    return jsonify({"nameAvailable": not db.exchange_exists(name)})


@app.route("/data-disclaimer/", methods=["GET"])
def data_disclaimer():
    return render_template("data-disclaimer.html")


@app.route("/<exchange_name>/create/", methods=["GET"])
def view_create_exchange(exchange_name, errorMessage=None, formData=None):
    db = get_db()
    if db.exchange_exists(exchange_name):
        return redirect(f"/{exchange_name}/")
    response = make_response(
        render_template(
            "create.html",
            exchangeName=exchange_name,
            errorMessage=errorMessage,
            existingFormData=formData,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def create_exchange(exchange_name, form):
    participant_names = [p for p in form.getlist("participant") if p]
    if len(participant_names) != len(set(participant_names)):
        return Response(status=422)
    participants = [Participant(participant) for participant in participant_names]
    name_id_mapping = {p.names[p.active_name]: p.uuid for p in participants}
    constraint_givers = form.getlist("giver")[1:]
    constraint_giftees = form.getlist("giftee")[1:]
    constraint_probabilities = form.getlist("probability-level")[1:]
    constraints = []
    try:
        for giver, giftee, probability in zip(
            constraint_givers,
            constraint_giftees,
            constraint_probabilities,
        ):
            if giver and giftee and probability:
                constraints.append(
                    Constraint(
                        name_id_mapping[giver],
                        name_id_mapping[giftee],
                        probability,
                    ),
                )
    except KeyError:
        return Response(status=422)
    try:
        pairing = get_pairing_with_probabilities(participants, constraints)
    except ValueError:
        return view_create_exchange(
            exchange_name,
            errorMessage=_(
                "Could not create a valid exchange with this data. "
                "Try removing some constraints "
                "or adding some participants to fix this.",
            ),
            formData=form,
        )
    exchange = Exchange(exchange_name, participants, constraints, pairing)
    db = get_db()
    try:
        db.create_exchange(exchange, participants, constraints, pairing)
    except IntegrityError as e:
        if db.exchange_exists(exchange_name):
            return render_template("rename-exchange.html", form_data=form)
        raise e
    return redirect(f"/{exchange_name}/")


@app.route("/<exchange_name>/create/", methods=["POST"])
def route_create_exchange(exchange_name):
    return create_exchange(exchange_name, request.form)


@app.route("/rename_exchange/", methods=["POST"])
def route_create_renamed_exchange():
    exchange_name = request.form.getlist("exchange_name")[0]
    return create_exchange(exchange_name, request.form)


@app.route("/<exchange_name>/")
def view_exchange(exchange_name):
    db = get_db()
    if not db.exchange_exists(exchange_name):
        return redirect(f"/{exchange_name}/create/")
    exchange = db.get_exchange(exchange_name)
    return render_template(
        "exchange-overview.html",
        exchangeName=exchange_name,
        participants=exchange.participants,
    )


@app.route(
    "/<exchange_name>/results/<path:participant_name>/",
)  # <path:… makes sure we can handle participant names containing slashes
def view_exchange_participant_result(exchange_name, participant_name):
    participant_name = urllib.parse.unquote_plus(participant_name)
    db = get_db()
    try:
        giftee = db.get_giftee_for_giver(exchange_name, participant_name)
    except ValueError as e:
        return not_found(e)
    return render_template(
        "exchange-user-result.html",
        exchangeName=exchange_name,
        participantName=participant_name,
        gifteeName=giftee.get_name(),
    )
