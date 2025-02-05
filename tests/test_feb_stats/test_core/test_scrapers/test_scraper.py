from unittest.mock import Mock, patch

import requests
from django.test import TestCase

from core.scrapers.boxscore_scraper import BoxscoreScraper


class TestBoxscoreScraper(TestCase):
    def test_context_manager(self):
        with patch("requests.Session") as mock_session:
            mock_instance = mock_session.return_value
            with BoxscoreScraper() as scraper:
                self.assertEqual(scraper.session, mock_instance)
            mock_instance.close.assert_called_once()

    def test_get_boxscore_urls_basic(self):
        with patch("requests.Session") as mock_session:
            mock_response = Mock()
            mock_response.text = """
                <select id="_ctl0_MainContentPlaceHolderMaster_gruposDropDownList">
                    <option value="1" selected>Group 1</option>
                </select>
                <td class="resultado"><a href="/game1"></a></td>
                <td class="resultado"><a href="/game2"></a></td>
            """
            mock_session.return_value.get.return_value = mock_response

            scraper = BoxscoreScraper()
            urls = scraper.get_boxscore_urls("http://example.com/calendar")

            self.assertEqual(urls, ["/game1", "/game2"])
            mock_session.return_value.get.assert_called_once_with("http://example.com/calendar")

    def test_get_boxscore_urls_with_group_change(self):
        with patch("requests.Session") as mock_session:
            initial_response = Mock()
            initial_response.raise_for_status = Mock()
            initial_response.text = """
                <select id="_ctl0_MainContentPlaceHolderMaster_gruposDropDownList">
                    <option value="1" selected>Group 1</option>
                </select>
                <input name="__VIEWSTATE" value="viewstate123" />
                <input name="__VIEWSTATEGENERATOR" value="generator123" />
                <input name="__EVENTVALIDATION" value="validation123" />
                <input name="_ctl0:token" value="token123" />
            """

            post_response = Mock()
            post_response.raise_for_status = Mock()
            post_response.text = """
                <td class="resultado"><a href="/game1"></a></td>
                <td class="resultado"><a href="/game2"></a></td>
            """

            mock_session.return_value.get.return_value = initial_response
            mock_session.return_value.post.return_value = post_response
            scraper = BoxscoreScraper()
            urls = scraper.get_boxscore_urls(
                calendar_url="http://example.com/calendar",
                season="2024",
                group_id="2",
            )

            mock_session.return_value.post.assert_called_once_with(
                "http://example.com/calendar",
                data={
                    "__EVENTTARGET": "_ctl0$MainContentPlaceHolderMaster$temporadasDropDownList",
                    "__EVENTARGUMENT": "",
                    "__VIEWSTATE": "viewstate123",
                    "__VIEWSTATEGENERATOR": "generator123",
                    "__EVENTVALIDATION": "validation123",
                    "_ctl0:MainContentPlaceHolderMaster:temporadasDropDownList": "2024",
                    "_ctl0:MainContentPlaceHolderMaster:gruposDropDownList": "2",
                    "_ctl0:token": "token123",
                },
            )
            initial_response.raise_for_status.assert_called_once()
            post_response.raise_for_status.assert_called_once()
            self.assertEqual(urls, ["/game1", "/game2"])

    def test_get_boxscore(self):
        with patch("requests.Session") as mock_session:
            mock_response = Mock()
            mock_response.content = b"boxscore data"
            mock_session.return_value.get.return_value = mock_response
            scraper = BoxscoreScraper()
            result = scraper.get_boxscore("http://example.com/game1")

            self.assertEqual(result, b"boxscore data")
            mock_session.return_value.get.assert_called_once_with("http://example.com/game1")

    def test_fetch_boxscores(self):
        with patch.object(BoxscoreScraper, "get_boxscore_urls") as mock_get_urls:
            with patch.object(BoxscoreScraper, "get_boxscore") as mock_get_boxscore:
                mock_get_urls.return_value = ["/game1", "/game2"]
                mock_get_boxscore.side_effect = [b"boxscore1", b"boxscore2"]
                scraper = BoxscoreScraper()
                results = scraper.fetch_boxscores("http://example.com/calendar")

                self.assertEqual(results, [b"boxscore1", b"boxscore2"])
                mock_get_urls.assert_called_once_with("http://example.com/calendar", None, None)
                self.assertEqual(mock_get_boxscore.call_count, 2)

    def test_error_handling(self):
        with patch("requests.Session") as mock_session:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.RequestException("Network error")
            mock_session.return_value.get.return_value = mock_response

            scraper = BoxscoreScraper()
            with self.assertRaises(requests.RequestException):
                scraper.get_boxscore_urls("http://example.com/calendar")
