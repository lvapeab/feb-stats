from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.http import HttpRequest, HttpResponse

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from werkzeug.utils import secure_filename

from core.scrapers.actions import read_boxscores_from_calendar_url
from service.api import FebStatsServiceServicer
from service.handler import SimpleLeagueHandler
from service.server import feb_stats_pb2
from web.helpers.read_write import (
    is_allowed_file_extension,
    read_boxscores_from_files,
    remove_boxscore_files,
)


class IndexView(View):
    def get(self, request: HttpRequest, name: str | None = None) -> HttpResponse:
        context = {
            "name": name,
            "predefined_urls": settings.DEFAULTS["calendar_selectors"],
        }
        return render(request, "web/index.html", context)


class UploadView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        if "file" not in request.FILES:
            messages.error(request, "No file part")
            return redirect("upload")
        uploaded_files = request.FILES.getlist("file")
        uploaded_file: UploadedFile | None = uploaded_files[0] if uploaded_files else None
        if uploaded_file is not None and uploaded_file.name and is_allowed_file_extension(uploaded_file.name):
            filename = secure_filename(uploaded_file.name)
            filepath = Path(settings.UPLOAD_FOLDER) / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            return HttpResponse("OK")

        messages.error(request, "Invalid upload request")
        return render(
            request,
            "web/index.html",
            {"predefined_urls": settings.DEFAULTS["calendar_selectors"]},
        )

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(
            request,
            "web/index.html",
            {"predefined_urls": settings.DEFAULTS["calendar_selectors"]},
        )


class AnalyzeView(View):
    def analyze_boxscores(self, boxscores: list[bytes], do_color_sheet: bool) -> HttpResponse:
        grpc_address = f"{settings.PORTS['grpc_address']}:{settings.PORTS['grpc_port']}"
        grpc_request = feb_stats_pb2.GetFebStatsRequest(
            boxscores=boxscores,
            color_sheet=do_color_sheet,
        )
        service = FebStatsServiceServicer(SimpleLeagueHandler(address=grpc_address))
        grpc_response = service.GetFebStats(grpc_request, None)

        output_filename = datetime.now().strftime("%d_%m_%Y_%H_%M")
        response = HttpResponse(
            content=grpc_response.sheet,
            content_type="application/vnd.ms-excel",
        )
        response["Content-Disposition"] = f"attachment; filename=estadisticas_{output_filename}.xlsx"
        response["Content-Length"] = len(grpc_response.sheet)
        return response

    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            do_color_sheet = bool(request.POST.get("color-sheet"))
            boxscores = read_boxscores_from_files()

            if not boxscores:
                messages.error(request, "No se han encontrado actas para analizar")
                return redirect(f"{reverse('index')}#data")

            return self.analyze_boxscores(boxscores, do_color_sheet)

        except Exception as error:
            messages.error(request, f"Error al procesar los archivos: {str(error)}")
            return redirect(f"{reverse('index')}#data")
        finally:
            remove_boxscore_files()


class AnalyzeUrlView(View):
    def post(self, request: HttpRequest) -> HttpResponse:
        try:
            do_color_sheet = bool(request.POST.get("color-sheet-url"))
            calendar_url = request.POST.get("custom_url")
            season_id = None
            group_id = None

            if not calendar_url:
                league_id = request.POST.get("league_id")
                if league_id:
                    league_data = settings.DEFAULTS["calendar_selectors"][league_id]
                    calendar_url = league_data["calendar_url"]
                    season_id = request.POST.get("season_id")
                    group_id = request.POST.get("group_id")

            if not calendar_url:
                messages.error(request, "No se ha proporcionado ninguna URL para analizar")
                return redirect(f"{reverse('index')}#url-analysis")

            boxscores = read_boxscores_from_calendar_url(
                calendar_url,
                season=season_id,
                group_id=group_id,
            )
            if not boxscores:
                messages.error(
                    request,
                    f"No se han encontrado actas para analizar para la url: "
                    f"{calendar_url} - Temporada {season_id} - Grupo: {group_id}",
                )
                return redirect(f"{reverse('index')}#url-analysis")

            analyzer = AnalyzeView()
            return analyzer.analyze_boxscores(boxscores, do_color_sheet)

        except Exception as error:
            messages.error(request, f"Error al procesar los archivos: {str(error)}")
            return redirect(f"{reverse('index')}#url-analysis")
