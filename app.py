import os
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
    session,
)
from flask_babel import Babel, _
from flask_babel_js import BabelJS

from constraint import Constraint
from databaseHandler import DatabaseHandler
from exchange import Exchange
from participant import (
    Participant,
)
from utils import get_pairing_with_probabilities, slugify

app = Flask(__name__)

app.secret_key = os.urandom(32)


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
def start(error_msg: str = None):
    return render_template("start.html", errorMessage=error_msg)


@app.route("/", methods=["POST"])
def route_to_exchange():
    exchange_name = request.form["exchange_name"]
    exchange_slug = slugify(exchange_name)
    if not exchange_slug:
        return start(
            error_msg=_(
                "Something went wrong with your exchange name. "
                "Please try again with a different name.",
            ),
        )
    db = get_db()
    # if exchange exists
    if db.exchange_exists(exchange_slug):
        return redirect(f"/{exchange_slug}/")
    # else create exchange
    session["exchange_name"] = exchange_name
    return redirect(f"/{exchange_slug}/create/")


@app.route("/check_exchange_name/")
def check_exchange_name():
    name = request.args.get("name", "").strip()
    slug = slugify(name)
    if not slug:
        return jsonify({"nameAvailable": False})
    db = get_db()
    return jsonify({"nameAvailable": not db.exchange_exists(slug)})


@app.route("/check_participant_name/")
def check_participant_name():
    exchange_slug = request.args.get("exchangeslug", "")
    new_name = request.args.get("newname", "").strip()
    old_name = request.args.get("oldname", "").strip()
    db = get_db()
    return jsonify(
        {
            "nameAvailable": db.participant_name_available(
                exchange_slug,
                old_name,
                new_name,
            ),
        },
    )


@app.route("/data-disclaimer/", methods=["GET"])
def data_disclaimer():
    return render_template("data-disclaimer.html")


@app.route("/<exchange_slug>/create/", methods=["GET"])
def view_create_exchange(exchange_slug, error_message=None, form_data=None):
    if not slugify(exchange_slug):
        return redirect("/")
    exchange_name = session.pop("exchange_name", None)
    if not exchange_name:
        if exchange_slug.islower():
            exchange_name = exchange_slug.title()
        else:
            exchange_name = exchange_slug
    if exchange_slug != slugify(exchange_slug):
        exchange_slug = slugify(exchange_slug)
    db = get_db()
    if db.exchange_exists(exchange_slug):
        return redirect(f"/{exchange_slug}/")
    response = make_response(
        render_template(
            "create.html",
            exchangeSlug=exchange_slug,
            exchangeName=exchange_name,
            errorMessage=error_message,
            existingFormData=form_data,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def create_exchange(exchange_slug, form, exchange_name: str = None):
    if not exchange_name:
        exchange_name = form.getlist("exchangeName")[0]
    participant_names = [p for p in form.getlist("participant") if p]
    if len(participant_names) != len(set(participant_names)):
        return Response(status=422)
    for name in participant_names:
        if name[0] == "/":
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
            exchange_slug,
            error_message=_(
                "Could not create a valid exchange with this data. "
                "Try removing some constraints "
                "or adding some participants to fix this.",
            ),
            form_data=form,
        )
    exchange = Exchange(exchange_name, participants, constraints, pairing)
    db = get_db()
    try:
        db.create_exchange(exchange, participants, constraints, pairing)
    except IntegrityError as e:
        if db.exchange_exists(exchange_slug):
            return render_template("rename-exchange.html", form_data=form)
        raise e
    return redirect(f"/{exchange_slug}/")


@app.route("/<exchange_slug>/create/", methods=["POST"])
def route_create_exchange(exchange_slug):
    return create_exchange(exchange_slug, request.form)


@app.route("/rename_exchange/", methods=["POST"])
def route_create_renamed_exchange():
    exchange_name = request.form.getlist("exchange_name")[0]
    exchange_slug = slugify(exchange_name)
    if not exchange_slug:
        return render_template("rename-exchange.html", form_data=request.form)
    return create_exchange(exchange_slug, request.form, exchange_name)


@app.route("/<exchange_slug>/")
def view_exchange(exchange_slug):
    db = get_db()
    if not db.exchange_exists(exchange_slug):
        return redirect(f"/{exchange_slug}/create/")
    exchange = db.get_exchange(exchange_slug)
    return render_template(
        "exchange-overview.html",
        exchangeSlug=exchange_slug,
        exchangeName=db.get_exchange_name(exchange_slug),
        participants=exchange.participants,
    )


@app.route(
    "/<exchange_slug>/results/<path:participant_name>",
    methods=["GET"],
)  # <path:… makes sure we can handle participant names containing slashes
def view_exchange_participant_result(exchange_slug, participant_name):
    participant_name = urllib.parse.unquote_plus(participant_name)
    db = get_db()
    try:
        active_name = db.get_active_name(exchange_slug, participant_name)
        if participant_name != active_name:
            return redirect(f"/{exchange_slug}/results/{active_name}")
    except ValueError as e:
        return not_found(e)
    try:
        giftee = db.get_giftee_for_giver(exchange_slug, participant_name)
        giver = db.get_giver_for_giftee(exchange_slug, participant_name)
    except ValueError as e:
        return not_found(e)
    return render_template(
        "exchange-user-result.html",
        exchangeSlug=exchange_slug,
        exchangeName=db.get_exchange_name(exchange_slug),
        participantName=participant_name,
        gifteeName=giftee.get_name(),
        giverName=giver.get_name(),
    )


@app.route(
    "/<exchange_slug>/results/<path:old_participant_name>",
    methods=["POST"],
)  # <path:… makes sure we can handle participant names containing slashes
def rename_participant(exchange_slug, old_participant_name):
    new_participant_name = request.form.getlist("participant_name")[0]
    if new_participant_name[0] == "/":
        return Response(status=422)
    old_participant_name = urllib.parse.unquote_plus(old_participant_name)
    db = get_db()
    db.change_participant_name(
        exchange_slug,
        old_participant_name,
        new_participant_name,
    )
    return redirect(f"/{exchange_slug}/results/{new_participant_name}")
