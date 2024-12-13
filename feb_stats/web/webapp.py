import secrets
import logging
import os
from datetime import datetime
from typing import Any
from pathlib import Path
import yaml
from flask import Flask, flash, make_response, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response

from feb_stats.service.api import FebStatsServiceServicer
from feb_stats.service.handler import SimpleLeagueHandler
from feb_stats.service.server import feb_stats_pb2
from feb_stats.web.read_write import (
    remove_boxscore_files,
    read_boxscores_from_files,
    is_allowed_file_extension,
    read_boxscores_from_calendar_url,
)

logger = logging.getLogger(__name__)


curr_dir = Path(__file__).parent

# TODO(Alvaro): Create prod/staging/test/local configs
config_filename = str(curr_dir / "config/local.yaml")


with open(config_filename) as f:
    config = yaml.safe_load(f)

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = config.get("upload_folder", "uploads")
app.config["ALLOWED_FILE_EXTENSIONS"] = config.get("allowed_file_extensions", ["html", "htm"])
app.config["MAX_CONTENT_LENGTH"] = config.get("max_content_length", 16 * 1024 * 1024)
app.config["PREDEFINED_URLS"] = config.get("predefined_urls", dict())
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))

ports_config = config["ports"]
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def analyze_boxscores(boxscores: list[bytes], do_color_sheet: bool) -> Response:
    try:
        grpc_address = f"{ports_config.get('grpc_address', 'localhost')}:f{ports_config.get('grpc_port', '50001')}"
        grpc_request = feb_stats_pb2.GetFebStatsRequest(
            boxscores=boxscores,
            color_sheet=do_color_sheet,
        )
        service = FebStatsServiceServicer(SimpleLeagueHandler(address=grpc_address))
        grpc_response = service.GetFebStats(grpc_request, None)

        # Output the data sheet
        output_filename = datetime.now().strftime("%d/%m/%Y_%H:%M")
        response: Response = make_response(grpc_response.sheet)
        response.headers["Content-Type"] = "application/vnd.ms-excel"
        response.headers["Content-disposition"] = f"attachment; filename=estadisticas_{output_filename}.xlsx"
        response.headers["Content-Length"] = str(len(grpc_response.sheet))
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        flash(f"Error al procesar los archivos: {str(e)}", "error")
        return redirect(url_for("index", _anchor="data"))


@app.route("/")
def index(name: str | None = None) -> Any:
    predefined_urls = app.config["PREDEFINED_URLS"]

    return render_template(
        "index.html",
        name=name,
        predefined_urls=predefined_urls,
    )


@app.route("/upload", methods=["POST", "GET"])
def upload() -> Any:
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]
        if file and file.filename and is_allowed_file_extension(file.filename, app.config):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            logger.info(f"Saving file to {filepath}.")
            file.save(filepath)
            return "OK"
    error = "Invalid /upload request."
    # the code below is executed if the request method was GET
    return render_template("index.html", error=error)


@app.route("/analyze", methods=["POST"])
def analyze() -> Response:
    try:
        do_color_sheet = False
        if request.form.get("color-sheet"):
            do_color_sheet = True
        boxscores = read_boxscores_from_files(app.config)
        if not boxscores:
            flash("No se han encontrado actas para analizar", "error")
            return redirect(url_for("index", _anchor="data"))
        return analyze_boxscores(boxscores, do_color_sheet)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        flash(f"Error al procesar los archivos: {str(e)}", "error")
        return redirect(url_for("index", _anchor="data"))
    finally:
        remove_boxscore_files(app.config)


@app.route("/analyze_url", methods=["POST"])
def analyze_url() -> Response:
    try:
        do_color_sheet = False
        if request.form.get("color-sheet-url"):
            do_color_sheet = True
        url = request.form.get("custom_url")
        if not url:
            selected_league = request.form.get("predefined_url")
            url = app.config["PREDEFINED_URLS"].get(selected_league)
        if not url:
            flash("No se ha proporcionado ninguna URL para analizar", "error")
            return redirect(url_for("index", _anchor="url-analysis"))

        boxscores = read_boxscores_from_calendar_url(url)
        if not boxscores:
            flash(f"No se han encontrado actas para analizar en la url: {url}", "error")
            return redirect(url_for("index", _anchor="url-analysis"))
        return analyze_boxscores(boxscores, do_color_sheet)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        flash(f"Error al procesar los archivos: {str(e)}", "error")
        return redirect(url_for("index", _anchor="url-analysis"))


if __name__ == "__main__":
    app.run()
