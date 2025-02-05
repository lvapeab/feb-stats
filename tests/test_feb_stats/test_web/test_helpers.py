import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from web.helpers.read_write import (
    get_boxscore_files,
    is_allowed_file_extension,
    read_boxscores_from_files,
    remove_boxscore_files,
)


class TestWebHelpers(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        settings.UPLOAD_FOLDER = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_is_allowed_file_extension(self):
        self.assertTrue(is_allowed_file_extension("test.html"))
        self.assertTrue(is_allowed_file_extension("test.htm"))
        self.assertFalse(is_allowed_file_extension("test.pdf"))
        self.assertFalse(is_allowed_file_extension("test"))

    def test_get_boxscore_files(self):
        test_files = ["test1.html", "test2.htm", "test3.pdf"]
        for file in test_files:
            path = Path(settings.UPLOAD_FOLDER) / file
            path.write_text("test content")

        files = get_boxscore_files()
        self.assertEqual(len(files), 2)
        self.assertTrue(all(str(file).endswith((".html", ".htm")) for file in files))

    @patch("web.helpers.read_write.read_file")
    def test_read_boxscores(self, mock_read_file):
        test_files = ["test1.html", "test2.htm"]
        for file in test_files:
            path = Path(settings.UPLOAD_FOLDER) / file
            path.write_text("test content")

        mock_read_file.return_value = b"test boxscore data"

        boxscores = read_boxscores_from_files()
        self.assertEqual(len(boxscores), 2)
        self.assertTrue(all(score == b"test boxscore data" for score in boxscores))
        self.assertEqual(mock_read_file.call_count, 2)

    def test_remove_boxscores(self):
        test_files = ["test1.html", "test2.htm", "test3.pdf"]
        for file in test_files:
            path = Path(settings.UPLOAD_FOLDER) / file
            path.write_text("test content")

        remove_boxscore_files()

        remaining_files = list(Path(settings.UPLOAD_FOLDER).glob("*"))
        self.assertEqual(len(remaining_files), 1)
        self.assertEqual(remaining_files[0].name, "test3.pdf")
