from flask import Flask, render_template, redirect, request
from slugify import slugify
import urllib.parse

app = Flask(__name__)


@app.route("/", methods=["GET"])
def start():
    return render_template("start.html")


@app.route("/", methods=["POST"])
def open_exchange():
    exchange_name = slugify(request.form["exchange_name"])
    exchange_name = urllib.parse.quote_plus(exchange_name)
    return redirect(f"/{exchange_name}")
