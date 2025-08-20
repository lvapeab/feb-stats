import os
from collections.abc import Callable
from typing import TypeVar
from urllib.parse import urlparse

import lxml.html as lh
import pandas as pd
import requests
from lxml.html import Element

from src.core.analysis.entities import Boxscore, Game, League, Player, Team
from src.core.parsers.exceptions import UnfinishedGameException
from src.core.parsers.transforms import transform_game_stats_df

T = TypeVar("T", str, bytes)


class FEBLivescoreParser:
    id: int
    name: str
    season_stats: pd.DataFrame | None = None

    @staticmethod
    def parse_str(input_str: str | bytes, decode_bytes: bool = False) -> str:
        if decode_bytes:
            input_str = bytes(str(input_str), "utf-8").decode("utf-8")
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
            game_at=f"{metadata['date']} {metadata['time']}",  # type: ignore[arg-type]  # Validated by Pydantic
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
        for i, link in enumerate(boxscores):
            doc = reader_fn(link)  # type: ignore[arg-type]
            try:
                game = cls.parse_game_stats(doc)
            except (UnfinishedGameException, ValueError):
                continue
            all_games.append(game)
            for team in game.teams:
                all_teams.add(team)

        if all_games:
            return cls.create_league(all_games, all_teams)
        else:
            raise ValueError(f"No games found in {len(boxscores)} boxscores.")

    @classmethod
    def read_link_bytes(cls, link: bytes) -> Element:
        document_string = link.decode("utf-8")
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
                with open(link, encoding="utf-8") as f:
                    document_string = f.read()
                    return lh.fromstring(document_string)
            else:
                return lh.fromstring(link)
        raise ValueError("Input must be a string (URL, file path, or HTML)")

    @classmethod
    def extract_nested_value(cls, doc: Element, xpath: str) -> str | None:
        value = None
        current_path = doc.xpath(xpath)
        while not value:
            try:
                if current_path[-1].text_content():
                    value = cls.parse_str(current_path[-1].text_content(), decode_bytes=True)
                    return value
                current_path = [x for x in current_path[-1]]
            except IndexError:
                return None
        return value

    @classmethod
    def parse_game_metadata(cls, doc: Element) -> dict[str, str]:
        # Parse data by id
        date = None
        time = None
        time_and_date_str = cls.extract_nested_value(doc, '//div[@class="fecha"]')
        if time_and_date_str is not None:
            split_time_and_date = time_and_date_str.split()  # Format: "Fecha XX/XX/XXXX - HH:MM
            if len(split_time_and_date) > 1:
                date = split_time_and_date[1]
                time = split_time_and_date[-1]

        season = cls.extract_nested_value(doc, '//span[@class="temporada"]')
        league = cls.extract_nested_value(doc, '//span[@class="liga"]')
        home_team = cls.extract_nested_value(doc, '//span[@id="_ctl0_MainContentPlaceHolderMaster_equipoLocalNombre"]')
        home_score = cls.extract_nested_value(doc, '//div[@class="columna equipo local"]//span[@class="resultado"]')
        away_team = cls.extract_nested_value(
            doc,
            '//span[@id="_ctl0_MainContentPlaceHolderMaster_equipoVisitanteNombre"]',
        )
        away_score = cls.extract_nested_value(doc, '//div[@class="columna equipo visitante"]//span[@class="resultado"]')

        _ = cls.extract_nested_value(doc, '//div[@class="arbitros"]')  # Format: Arbitros X W. Z | A B. C |

        # main_referee = ref[0]
        # second_referee = ref[1]
        # home_team = codecs.latin_1_encode(self.parse_str(home_score[0].text_content()))
        metadata_dict = {
            "date": date or "",
            "time": time or "",
            "league": league or "",
            "season": season or "",
            "home_team": home_team or "",
            "home_score": home_score or "",
            "away_team": away_team or "",
            "away_score": away_score or "",
            # TODO(alvaro): Parse referees
            "main_referee": "-",  # self.parse_str(main_referee),
            "second_referee": "-",  # self.parse_str(second_referee),
        }

        return metadata_dict

    @classmethod
    def is_finished_game(cls, doc: Element) -> bool:
        played_quarters = doc.xpath('.//span[@class="cuarto play"]')
        return len(played_quarters) >= 4

    @classmethod
    def get_tables(cls, doc: Element, base_xpath: str = "//table") -> tuple[list[Element], list[Element]]:
        xpath = f"{base_xpath}//tbody"
        try:
            table_local, table_away = cls.get_elements(doc, xpath)[-2:]
            if len(table_local) <= 1 or len(table_away) <= 1:
                raise ValueError
            return table_local, table_away
        except ValueError:
            table_local, table_away = cls.get_elements(doc, base_xpath)[-2:]
            return table_local, table_away

    @classmethod
    def parse_game_stats(cls, doc: Element) -> Game:
        game_stats = {}
        metadata = cls.parse_game_metadata(doc)
        if not cls.is_finished_game(doc):
            raise UnfinishedGameException
        try:
            table_local, table_away = cls.get_tables(doc)
        except ValueError:
            raise ValueError(f"Unable to parse stats from {doc}")

        for local, table in zip((True, False), (table_local, table_away)):
            key = "home_boxscore" if local else "away_boxscore"
            ori_df = cls.elements_to_df(table, initial_row=2)
            df = transform_game_stats_df(ori_df, home_team=local)
            game_stats[key] = df

        assert game_stats
        return cls.create_game(metadata, game_stats)

    @classmethod
    def elements_to_df(
        cls,
        tr_elements: list[Element],
        initial_row: int = 2,
        discard_last: int = 0,
    ) -> pd.DataFrame:
        table_rows = []
        # Since out first row is the header, data is stored on the second row onwards
        for j in range(initial_row, len(tr_elements) - discard_last):
            # T is our j'th row
            T = tr_elements[j]
            row = {}
            for t in T.iterchildren():
                column_title = t.attrib["class"]
                data = cls.parse_str(t.text_content(), decode_bytes=True)
                # Append the data to the empty list of the i'th column
                row[column_title] = data
            table_rows.append(row)

        df = pd.DataFrame(table_rows)
        return df
