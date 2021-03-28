import hashlib
import os
from abc import ABC, abstractmethod
from typing import TypeVar, List, Optional, Set, Tuple, Dict, Callable, Union
from urllib.parse import urlparse

import lxml.html as lh
import pandas as pd
import requests
from lxml.html import Element

from feb_stats.core.entities import Game, Team, League, Boxscore, Player

T = TypeVar("T")


class GenericParser(ABC):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None

    @staticmethod
    def parse_str(input_str: Union[str, bytes], decode_bytes: bool = False) -> str:
        if decode_bytes:
            input_str = bytes(str(input_str), "iso-8859-1").decode("utf-8")
        assert isinstance(input_str, str)
        return " ".join(input_str.replace("\n", " ").
                        replace("\t", " ").
                        replace("\r", " ").
                        replace(",", ".").
                        split()).\
            strip()

    @staticmethod
    def get_elements(doc: Element, id: str) -> List[Element]:
        # Parse data by id
        table_elements: List[Element] = doc.xpath(id)
        return table_elements

    def create_league(self, all_games: List[Game], all_teams: Set[Team]) -> League:
        return League(
            id=hashlib.md5(f"{all_games[0].league}".encode('utf-8')).hexdigest(),
            name=all_games[0].league,
            season=all_games[0].season,
            teams=list(all_teams),
            games=all_games,
        )

    def create_objects(self,
                       metadata: Dict[str, str],
                       game_stats: Dict[str, pd.DataFrame]
                       ) -> Tuple[Game, Tuple[Team, Team]]:
        home_team: Team = Team(
            id=hashlib.md5(metadata["home_team"].encode('utf-8')).hexdigest(),
            name=metadata["home_team"],
        )
        away_team: Team = Team(
            id=hashlib.md5(metadata["away_team"].encode('utf-8')).hexdigest(),
            name=metadata["away_team"],
        )
        game: Game = Game(
            id=hashlib.md5(
                f"{metadata['league']}{metadata['date']}{metadata['home_team']}{metadata['away_team']}".encode(
                    'utf-8')).hexdigest(),
            date=metadata["date"],
            hour=metadata["hour"],
            league=metadata["league"],
            season=metadata["season"],
            home_team=home_team,
            home_score=int(metadata["home_score"]),
            away_team=away_team,
            away_score=int(metadata["away_score"]),
            main_referee=Player(
                id=hashlib.md5(metadata["main_referee"].encode('utf-8')).hexdigest(),
                name=metadata["main_referee"],
            ),
            aux_referee=Player(
                id=hashlib.md5(metadata["second_referee"].encode('utf-8')).hexdigest(),
                name=metadata["second_referee"],
            ),
            local_boxscore=Boxscore(
                id=hashlib.md5(
                    f"{metadata['league']}_{metadata['date']}_{metadata['home_team']}".encode('utf-8')).hexdigest(),
                boxscore=game_stats["home_boxscore"],
            ),
            away_boxscore=Boxscore(
                id=hashlib.md5(
                    f"{metadata['league']}_{metadata['date']}_{metadata['away_team']}".encode('utf-8')).hexdigest(),
                boxscore=game_stats["away_boxscore"],
            ),
        )
        return game, (home_team, away_team)

    def parse_boxscores(
            self, boxscores_bytes: List[bytes], reader_fn: Optional[Callable] = None
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
    def parse_game_stats(self,
                         doc: Element,
                         ids: Optional[Union[List[Tuple[str, bool]], str]] = None
                         ) -> Tuple[Game, Tuple[Team, Team]]:
        pass
