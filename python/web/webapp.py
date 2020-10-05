import os
import glob
import yaml

from datetime import datetime
import grpc

from flask_sqlalchemy import SQLAlchemy

from flask import (
    Flask,
    url_for,
    render_template,
    make_response,
    request,
    flash,
    redirect,
)
from werkzeug.utils import secure_filename

from python.service.api import FebStatsServiceServicer
from python.service.handler import SimpleLeagueHandler
from python.service.codegen.feb_stats_pb2 import GetFebStatsRequest

if os.environ.get("SERVER_ENVIRONMENT", "") == "PRODUCTION":
    config_filename = "config/production.yaml"
else:
    config_filename = "config/local.yaml"

with open(config_filename) as f:
    config = yaml.safe_load(f)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = config.get("upload_folder", "uploads")
app.config["MAX_CONTENT_LENGTH"] = config.get("max_content_length", 16 * 1024 * 1024)

db_config = config["database"]
db_auth = (
    f'{db_config["username"]}:{db_config["password"]}@{db_config["hostname"]}'
    if db_config["username"]
    else ""  #  os.path.dirname(os.path.realpath(__file__))
)

SQLALCHEMY_DATABASE_URI = f"{db_config['engine']}://{db_auth}/{db_config['db_name']}"

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.app = app
from python.web.db import Team


@app.route("/")
def index(name=None):
    url_for("static", filename="main.css")
    return render_template("index.hbs", name=name)


def allowed_file_extension(filename, allowed_extensions=None):
    allowed_extensions = allowed_extensions or {"html"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/upload", methods=["POST", "GET"])
def upload() -> str:
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]

        if file and allowed_file_extension(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return "OK"
    error = "Invalid username/password"
    # the code below is executed if the request method was GET
    return render_template("login.html", error=error)


def read_file(file):
    with open(file, mode="rb") as f:
        read_f = f.read()
    return read_f


class ContextStub:
    def invocation_metadata(self):
        return [("tenant", "test")]


@app.route("/analyze", methods=["POST", "GET"])
def analyze():
    boxscores = [
        read_file(filename)
        for filename in glob.glob(os.path.join(app.config["UPLOAD_FOLDER"], "*html"))
    ]
    with grpc.insecure_channel("localhost:50001") as channel:
        grpc_request = GetFebStatsRequest(boxscores=boxscores,)
        service = FebStatsServiceServicer(
            SimpleLeagueHandler(address="localhost:50001")
        )
        grpc_response = service.GetFebStats(grpc_request, ContextStub())

        # Commit e.g. Teams in the database
        for team in grpc_response.teams:
            t = Team(str(team))
            db.session.add(t)
        db.session.commit()

        # Output the data sheet
        output_filename = datetime.now().strftime("%d/%m/%Y_%H:%M")
        response = make_response(grpc_response.sheet)
        response.headers["Content-Type"] = "application/vnd.ms-excel"
        response.headers[
            "Content-disposition"
        ] = f"attachment; filename=estadisticas_{output_filename}.xlsx"
        response.headers["Content-Length"] = len(grpc_response.sheet)

    return response
