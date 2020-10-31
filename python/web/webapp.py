import os
import glob
import yaml

from datetime import datetime
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
from typing import List
from python.service.api import FebStatsServiceServicer
from python.service.handler import SimpleLeagueHandler
from python.service.server import feb_stats_pb2

if os.environ.get("SERVER_ENVIRONMENT", "") == "PRODUCTION":
    config_filename = "python/web/config/production.yaml"
else:
    config_filename = "python/web/config/local.yaml"

with open(config_filename) as f:
    config = yaml.safe_load(f)

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = config.get("upload_folder", "uploads")
app.config["MAX_CONTENT_LENGTH"] = config.get("max_content_length", 16 * 1024 * 1024)
ports_config = config["ports"]


@app.route("/")
def index(name=None):
    # url_for("static", filename="python/web/static/main.css")
    return render_template("index.html", name=name)


def allowed_file_extension(filename, allowed_extensions=None):
    allowed_extensions = allowed_extensions or {"html"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def read_file(file):
    with open(file, mode="rb") as f:
        read_f = f.read()
    return read_f


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
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            print(f"Saving file to {filepath}")
            file.save(filepath)
            return "OK"
    error = "Invalid /upload request."
    # the code below is executed if the request method was GET
    return render_template("index.html", error=error)


def read_file(file):
    with open(file, mode="rb") as f:
        read_f = f.read()
    return read_f


def read_boxscores() -> List[bytes]:
    return [
        read_file(filename)
        for filename in glob.glob(os.path.join(app.config["UPLOAD_FOLDER"], "*html"))
    ]


def remove_boxscores() -> None:
    for filename in glob.glob(os.path.join(app.config["UPLOAD_FOLDER"], "*html")):
        os.remove(filename)


@app.route("/analyze", methods=["POST"])
def analyze():
    boxscores = read_boxscores()
    grpc_address = f"{ports_config.get('grpc_address', 'localhost')}:f{ports_config.get('grpc_port', '50001')}"
    grpc_request = feb_stats_pb2.GetFebStatsRequest(boxscores=boxscores,)
    service = FebStatsServiceServicer(SimpleLeagueHandler(address=grpc_address))
    grpc_response = service.GetFebStats(grpc_request, None)

    # Output the data sheet
    output_filename = datetime.now().strftime("%d/%m/%Y_%H:%M")
    response = make_response(grpc_response.sheet)
    response.headers["Content-Type"] = "application/vnd.ms-excel"
    response.headers[
        "Content-disposition"
    ] = f"attachment; filename=estadisticas_{output_filename}.xlsx"
    response.headers["Content-Length"] = len(grpc_response.sheet)
    # remove_boxscores()
    return response


if __name__ == "__main__":
    app.run()
