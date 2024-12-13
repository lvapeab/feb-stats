import requests
from bs4 import BeautifulSoup


class BoxscoreScraper:
    def __init__(self):
        self.session = requests.Session()

    def get_boxscore_urls(self, calendar_url: str) -> list[str]:
        """Extract all boxscore URLs from a calendar page"""
        response = self.session.get(calendar_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all links that match finished games
        finished_games = soup.find_all("td", class_="resultado")
        links = [cell.find("a")["href"] for cell in finished_games]
        return links

    def get_boxscore(self, game_url: str) -> bytes:
        response = self.session.get(game_url)
        response.raise_for_status()
        return response.content

    def fetch_boxscores(self, results_url: str) -> list[bytes]:
        game_urls = self.get_boxscore_urls(results_url)
        return [self.get_boxscore(url) for url in game_urls]
