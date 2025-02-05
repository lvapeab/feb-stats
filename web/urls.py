from django.urls import path

from web.views import AnalyzeUrlView, AnalyzeView, IndexView, UploadView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("upload/", UploadView.as_view(), name="upload"),
    path("analyze/", AnalyzeView.as_view(), name="analyze"),
    path("analyze_url/", AnalyzeUrlView.as_view(), name="analyze_url"),
]
