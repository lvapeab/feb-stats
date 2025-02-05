import tempfile
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse


class TestFebStatsWebapp(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.client = Client()
        settings.UPLOAD_FOLDER = self.temp_dir.name

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_index_route(self) -> None:
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "web/index.html")

    def test_upload_no_file(self) -> None:
        response = self.client.post(reverse("upload"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_upload_invalid_extension(self) -> None:
        data = {"file": (BytesIO(b"test content"), "test.pdf")}
        response = self.client.post(reverse("upload"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_upload_valid_file(self) -> None:
        data = {"file": (BytesIO(b"test content"), "test.html")}
        response = self.client.post(reverse("upload"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.content, b"OK")

        uploaded_file = Path(settings.UPLOAD_FOLDER) / "test.html"
        self.assertTrue(uploaded_file.exists())
        self.assertEqual(uploaded_file.read_bytes(), b"test content")

    @patch("web.views.FebStatsServiceServicer")
    def test_analyze_endpoint_success(self, mock_service: MagicMock) -> None:
        test_file = Path(settings.UPLOAD_FOLDER) / "test.html"
        test_file.write_text("test content")

        mock_response = MagicMock()
        mock_response.sheet = b"test excel data"
        mock_service.return_value.GetFebStats.return_value = mock_response

        response = self.client.post(reverse("analyze"), data={"color-sheet": "true"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.content, b"test excel data")
        self.assertEqual(response["Content-Type"], "application/vnd.ms-excel")
        self.assertIn("estadisticas_", response["Content-Disposition"])

    @patch("web.views.FebStatsServiceServicer")
    def test_analyze_endpoint_no_files(self, mock_service: MagicMock) -> None:
        response = self.client.post(reverse("analyze"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @patch("web.views.FebStatsServiceServicer")
    def test_analyze_endpoint_error(self, mock_service: MagicMock) -> None:
        test_file = Path(settings.UPLOAD_FOLDER) / "test.html"
        test_file.write_text("test content")

        mock_service.return_value.GetFebStats.side_effect = Exception("Test error")

        response = self.client.post(reverse("analyze"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertFalse(test_file.exists())
