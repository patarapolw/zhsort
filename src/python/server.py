from flask import Flask, redirect
from flask_cors import CORS
from pathlib import Path

from .api import api

app = Flask(__name__, static_folder=str(Path(__file__).joinpath("../../../public").resolve()), static_url_path="")
CORS(app)

app.register_blueprint(api)


@app.route("/")
def r_index():
    return redirect("/index.html")
