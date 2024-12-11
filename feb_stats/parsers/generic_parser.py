import os
from abc import ABC, abstractmethod
from typing import TypeVar
from collections.abc import Callable
from urllib.parse import urlparse

import lxml.html as lh
import pandas as pd
import requests
from lxml.html import Element

from feb_stats.core.entities import Boxscore, Game, League, Player, Team

T = TypeVar("T", str, bytes)


class GenericParser(ABC):
    id: int
    name: str
    season_stats: pd.DataFrame | None = None

    @staticmethod
    def parse_str(input_str: str | bytes, decode_bytes: bool = False) -> str:
        if decode_bytes:
            input_str = bytes(str(input_str), "latin-1").decode("latin-1")
        assert isinstance(input_str, str)
        return " ".join(
            input_str.replace("\n", " ").replace("\t", " ").replace("\r", " ").replace(",", ".").split()
        ).strip()

    @staticmethod
    def get_elements(doc: Element, id: str) -> list[Element]:
        # Parse data by id
        table_elements: list[Element] = doc.xpath(id)
        return table_elements

    @staticmethod
    def create_league(all_games: list[Game], all_teams: set[Team]) -> League:
        return League(
            name=all_games[0].league,
            season=all_games[0].season,
            teams=list(all_teams),
            games=all_games,
        )

    @staticmethod
    def create_game(metadata: dict[str, str], game_stats: dict[str, pd.DataFrame]) -> Game:
        return Game(
            game_at=f'{metadata["date"]} {metadata["time"]}',  # type: ignore[arg-type]  # Validated by Pydantic
            league=metadata["league"],
            season=metadata["season"],
            main_referee=Player(name=metadata["main_referee"]),
            aux_referee=Player(name=metadata["second_referee"]),
            home_boxscore=Boxscore(
                boxscore=game_stats["home_boxscore"],
                team=Team(name=metadata["home_team"]),
                score=int(metadata["home_score"]),
            ),
            away_boxscore=Boxscore(
                boxscore=game_stats["away_boxscore"],
                team=Team(name=metadata["away_team"]),
                score=int(metadata["away_score"]),
            ),
        )

    @classmethod
    def parse_boxscores(
        cls,
        boxscores: list[T],
        reader_fn: Callable[[T], Element],
    ) -> League:
        all_games = []
        all_teams = set()
        for link in boxscores:
            doc = reader_fn(link)  # type: ignore[arg-type]
            game = cls.parse_game_stats(doc)
            all_games.append(game)
            for team in game.teams:
                all_teams.add(team)

        if all_games:
            return cls.create_league(all_games, all_teams)
        else:
            raise ValueError(f"No games found in {boxscores}")

    @classmethod
    def read_link_bytes(cls, link: bytes) -> Element:
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
                return lh.fromstring(page.content)
            elif os.path.isfile(link):
                with open(link, encoding="latin1") as f:
                    document_string = f.read()
                    return lh.fromstring(document_string)
            else:
                return lh.fromstring(link)
        raise ValueError("Input must be a string (URL, file path, or HTML)")

    @classmethod
    @abstractmethod
    def elements_to_df(cls, tr_elements: list[Element], initial_row: int = 2, n_elem: int = 0) -> pd.DataFrame:
        pass

    @classmethod
    @abstractmethod
    def parse_game_metadata(cls, doc: Element) -> dict[str, str]:
        pass

    @classmethod
    @abstractmethod
    def parse_game_stats(cls, doc: Element, ids: list[tuple[str, bool]] | str | None = None) -> Game:
        pass
