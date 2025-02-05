from types import TracebackType

import requests
from bs4 import BeautifulSoup


class BoxscoreScraper:
    def __init__(self) -> None:
        self.session: requests.Session = requests.Session()

    def __enter__(self) -> "BoxscoreScraper":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the requests session"""
        if self.session:
            self.session.close()

    def get_boxscore_urls(self, calendar_url: str, season: str | None = None, group_id: str | None = None) -> list[str]:
        """Extract all boxscore URLs from a calendar page"""
        response = self.session.get(calendar_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        if soup is None:
            return []
        # If the default group is the same as our query (group_id), we don't need to POST with the selected option.
        default_group = soup.find(  # type: ignore
            "select",
            {"id": "_ctl0_MainContentPlaceHolderMaster_gruposDropDownList"},
        ).find("option", selected=True)["value"]  # type: ignore[index]

        if season and group_id and group_id != default_group:
            viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]  # type: ignore[index]
            viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]  # type: ignore[index]
            eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]  # type: ignore[index]
            token = soup.find("input", {"name": "_ctl0:token"})["value"]  # type: ignore[index]
            form_data = {
                "__EVENTTARGET": "_ctl0$MainContentPlaceHolderMaster$temporadasDropDownList",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": viewstate,
                "__VIEWSTATEGENERATOR": viewstategenerator,
                "__EVENTVALIDATION": eventvalidation,
                "_ctl0:MainContentPlaceHolderMaster:temporadasDropDownList": season,
                "_ctl0:MainContentPlaceHolderMaster:gruposDropDownList": group_id,
                "_ctl0:token": token,
            }
            response = self.session.post(calendar_url, data=form_data)
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

    def fetch_boxscores(self, calendar_url: str, season: str | None = None, group_id: str | None = None) -> list[bytes]:
        game_urls = self.get_boxscore_urls(
            calendar_url,
            season,
            group_id,
        )
        return [self.get_boxscore(url) for url in game_urls]
