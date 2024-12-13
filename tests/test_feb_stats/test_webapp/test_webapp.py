import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO
from http import HTTPStatus

from feb_stats.web.webapp import app
from feb_stats.web.read_write import (
    is_allowed_file_extension,
    get_boxscore_files,
    read_boxscores_from_files,
    remove_boxscore_files,
)

import yaml


class TestFebStatsWebapp(unittest.TestCase):
    def setUp(self):
        app_dir = Path(app.root_path)

        with open(app_dir / "config/defaults.yaml") as f:
            self.defaults = yaml.safe_load(f)

        app.config["TESTING"] = True
        app.config["UPLOAD_FOLDER"] = "test_uploads"
        app.config["SECRET_KEY"] = "test_key"
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(app.config["UPLOAD_FOLDER"]):
            for file in Path(app.config["UPLOAD_FOLDER"]).glob("*"):
                os.remove(file)
            os.rmdir(app.config["UPLOAD_FOLDER"])

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b"html", response.data)

    def test_is_allowed_file_extension(self):
        self.assertTrue(is_allowed_file_extension("test.html"))
        self.assertTrue(is_allowed_file_extension("test.htm"))
        self.assertFalse(is_allowed_file_extension("test.pdf"))
        self.assertFalse(is_allowed_file_extension("test"))

    def test_upload_no_file(self):
        response = self.client.post("/upload")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_upload_invalid_extension(self):
        data = {"file": (BytesIO(b"test content"), "test.pdf")}
        response = self.client.post("/upload", data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_upload_valid_file(self):
        data = {"file": (BytesIO(b"test content"), "test.html")}
        response = self.client.post("/upload", data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, b"OK")

        uploaded_file = Path(app.config["UPLOAD_FOLDER"]) / "test.html"
        self.assertTrue(uploaded_file.exists())
        self.assertEqual(uploaded_file.read_bytes(), b"test content")

    def test_get_boxscore_files(self):
        test_files = ["test1.html", "test2.htm", "test3.pdf"]
        for file in test_files:
            path = Path(app.config["UPLOAD_FOLDER"]) / file
            path.write_text("test content")

        files = get_boxscore_files(app.config)
        self.assertEqual(len(files), 2)
        self.assertTrue(all(str(file).endswith((".html", ".htm")) for file in files))

    @patch("feb_stats.web.read_write.read_file")
    def test_read_boxscores(self, mock_read_file):
        test_files = ["test1.html", "test2.htm"]
        for file in test_files:
            path = Path(app.config["UPLOAD_FOLDER"]) / file
            path.write_text("test content")

        mock_read_file.return_value = b"test boxscore data"

        boxscores = read_boxscores_from_files(app.config)
        self.assertEqual(len(boxscores), 2)
        self.assertTrue(all(score == b"test boxscore data" for score in boxscores))
        self.assertEqual(mock_read_file.call_count, 2)

    def test_remove_boxscores(self):
        test_files = ["test1.html", "test2.htm", "test3.pdf"]
        for file in test_files:
            path = Path(app.config["UPLOAD_FOLDER"]) / file
            path.write_text("test content")

        remove_boxscore_files(app.config)

        remaining_files = list(Path(app.config["UPLOAD_FOLDER"]).glob("*"))
        self.assertEqual(len(remaining_files), 1)
        self.assertEqual(remaining_files[0].name, "test3.pdf")

    @patch("feb_stats.web.webapp.FebStatsServiceServicer")
    def test_analyze_endpoint_success(self, mock_service):
        test_file = Path(app.config["UPLOAD_FOLDER"]) / "test.html"
        test_file.write_text("test content")

        mock_response = MagicMock()
        mock_response.sheet = b"test excel data"
        mock_service.return_value.GetFebStats.return_value = mock_response

        response = self.client.post("/analyze", data={"color-sheet": "true"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data, b"test excel data")
        self.assertEqual(response.headers["Content-Type"], "application/vnd.ms-excel")
        self.assertIn("estadisticas_", response.headers["Content-disposition"])

    @patch("feb_stats.web.webapp.FebStatsServiceServicer")
    def test_analyze_endpoint_no_files(self, mock_service):
        response = self.client.post("/analyze")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @patch("feb_stats.web.webapp.FebStatsServiceServicer")
    def test_analyze_endpoint_error(self, mock_service):
        test_file = Path(app.config["UPLOAD_FOLDER"]) / "test.html"
        test_file.write_text("test content")

        mock_service.return_value.GetFebStats.side_effect = Exception("Test error")

        response = self.client.post("/analyze")
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertFalse(test_file.exists())
