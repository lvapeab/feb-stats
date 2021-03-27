import pandas as pd
from lxml.html import Element
from hashlib import md5
import lxml.html as lh
import os
import requests
from urllib.parse import urlparse
from abc import ABC, abstractmethod

from typing import TypeVar, List, Optional, Set, Tuple, Dict, Callable, Union
from python.feb_stats.entities import Game, Team, League

T = TypeVar("T")


class GenericParser(ABC):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None

    @staticmethod
    def parse_str(input_str: Union[str, bytes], decode_bytes: bool = False) -> str:
        if decode_bytes:
            input_str = bytes(str(input_str), "iso-8859-1").decode("utf-8")
        return " ".join(
            input_str.replace("\n", " ")
            .replace("\t", " ")
            .replace("\r", " ")
            .replace(",", ".")
            .split()
        ).strip()

    @staticmethod
    def get_elements(doc: Element, id: str) -> List[Element]:
        # Parse data by id
        table_elements = doc.xpath(id)
        return table_elements

    def create_league(self, all_games: List[Game], all_teams: Set[Team]) -> League:
        return League(
            id=int(
                md5(str.encode(f"{all_games[0].league}", encoding="UTF-8")).hexdigest(),
                16,
            ),
            name=all_games[0].league,
            season=all_games[0].season,
            teams=list(all_teams),
            games=all_games,
        )

    def parse_boxscores(
        self, boxscores_bytes: List[TypeVar], reader_fn: Optional[Callable] = None
    ) -> League:
        all_games = []
        all_teams = set()
        reader_fn = reader_fn or self.read_link_bytes
        for link in boxscores_bytes:
            doc = reader_fn(link)
            game, teams = self.parse_game_stats(doc)
            all_games.append(game)
            for team in teams:
                all_teams.add(team)

        if all_games:
            return self.create_league(all_games, all_teams)
        else:
            raise ValueError(f"No games found in {boxscores_bytes}")

    @staticmethod
    def read_link_bytes(link: bytes) -> Element:
        document_string = link.decode("latin1")
        doc = lh.fromstring(document_string)
        return doc

    @staticmethod
    def read_link_file(link: str) -> Element:
        if isinstance(link, str):
            result = urlparse(link)
            if all([result.scheme, result.netloc, result.path]):
                page = requests.get(link)
                # Store the contents of the website under doc
                document_string = lh.fromstring(page.content)
            elif os.path.isfile(link):
                with open(link, mode="r", encoding="latin1") as f:
                    document_string = f.read()
            else:
                raise ValueError(
                    f"Unable to find the resource {link} (not a valid URL nor an existing file.)"
                )
        doc = lh.fromstring(document_string)

        return doc

    @abstractmethod
    def elements_to_df(
        self, tr_elements: List[Element], initial_row: int = 2, n_elem: int = 0
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def parse_game_metadata(self, doc: Element) -> Dict[str, str]:
        pass

    @abstractmethod
    def parse_game_stats(
        self, doc: Element, ids: List[Optional[str]] = None
    ) -> Tuple[Game, Tuple[Team, Team]]:
        pass
