import glob
import logging
import os
from datetime import datetime
from typing import Any, List, Optional, Set

import yaml
from flask import Flask, flash, make_response, redirect, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response

from feb_stats.service.api import FebStatsServiceServicer
from feb_stats.service.handler import SimpleLeagueHandler
from feb_stats.service.server import feb_stats_pb2
from feb_stats.tools.export_boxscores import read_file

logger = logging.getLogger(__name__)

if os.environ.get("SERVER_ENVIRONMENT", "") == "PRODUCTION":
    config_filename = "feb_stats/web/config/production.yaml"
else:
    config_filename = "feb_stats/web/config/local.yaml"

with open(config_filename) as f:
    config = yaml.safe_load(f)

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = config.get("upload_folder", "uploads")
app.config["MAX_CONTENT_LENGTH"] = config.get("max_content_length", 16 * 1024 * 1024)
ports_config = config["ports"]
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index(name: Optional[str] = None) -> Any:
    return render_template("index.html", name=name)


def allowed_file_extension(
    filename: str, allowed_extensions: Optional[Set[str]] = None
) -> bool:
    allowed_extensions = allowed_extensions or {"html"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/upload", methods=["POST", "GET"])
def upload() -> Any:
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]
        if file and file.filename and allowed_file_extension(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            logger.info(f"Saving file to {filepath}.")
            file.save(filepath)
            return "OK"
    error = "Invalid /upload request."
    # the code below is executed if the request method was GET
    return render_template("index.html", error=error)


def read_boxscores() -> List[bytes]:
    return [
        read_file(filename)
        for filename in glob.glob(os.path.join(app.config["UPLOAD_FOLDER"], "*html"))
    ]


def remove_boxscores() -> None:
    for filename in glob.glob(os.path.join(app.config["UPLOAD_FOLDER"], "*html")):
        os.remove(filename)


@app.route("/analyze", methods=["POST"])
def analyze() -> Response:
    color_sheet = False
    if request.form.get("color-sheet"):
        color_sheet = True
    boxscores = read_boxscores()
    grpc_address = f"{ports_config.get('grpc_address', 'localhost')}:f{ports_config.get('grpc_port', '50001')}"
    grpc_request = feb_stats_pb2.GetFebStatsRequest(
        boxscores=boxscores,
        color_sheet=color_sheet,
    )
    service = FebStatsServiceServicer(SimpleLeagueHandler(address=grpc_address))
    grpc_response = service.GetFebStats(grpc_request, None)

    # Output the data sheet
    output_filename = datetime.now().strftime("%d/%m/%Y_%H:%M")
    response: Response = make_response(grpc_response.sheet)
    response.headers["Content-Type"] = "application/vnd.ms-excel"
    response.headers[
        "Content-disposition"
    ] = f"attachment; filename=estadisticas_{output_filename}.xlsx"
    response.headers["Content-Length"] = len(grpc_response.sheet)
    remove_boxscores()
    return response


if __name__ == "__main__":
    app.run()
