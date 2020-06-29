import pandas as pd
from lxml.html import Element
from hashlib import md5
import lxml.html as lh
import os
import requests
from urllib.parse import urlparse
from abc import ABC, abstractmethod

from typing import Dict, Tuple, Union
from typing import TypeVar, List, Optional
from python.feb_stats.entities import Game, Team, League

T = TypeVar('T')


class GenericParser(ABC):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None

    @staticmethod
    def parse_str(input_str: str):
        return ' '.join(
            input_str.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace(',', '.').split()).strip()

    @staticmethod
    def get_elements(doc: Element,
                     id: str) -> List[Element]:
        # Parse data by id
        table_elements = doc.xpath(id)
        return table_elements

    def elements_to_df(self,
                       tr_elements: List[Element],
                       initial_row: int = 2,
                       n_elem: int = 0
                       ) -> pd.DataFrame:
        col = []
        i = 0
        # For each row, store each first element (header) and an empty list
        for t in tr_elements[0]:
            i += 1
            name = self.parse_str(t.text_content())
            col.append((name, []))
        if n_elem == 0:
            n_elem = len(col)
        # Since out first row is the header, data is stored on the second row onwards
        for j in range(initial_row, len(tr_elements)):
            # T is our j'th row
            T = tr_elements[j]
            # If row is not of size 16, the //tr data is not from our table
            if len(T) == n_elem:
                # i is the index of our column
                i = 0
                # Iterate through each element of the row
                for t in T.iterchildren():
                    data = self.parse_str(t.text_content())
                    # Append the data to the empty list of the i'th column
                    col[i][1].append(data)
                    # Increment i for the next column
                    i += 1

        data_dict = {title: column for (title, column) in col}
        df = pd.DataFrame(data_dict)
        return df

    def parse_boxscores(self,
                        boxscores_bytes: List[bytes]) -> League:
        all_games = []
        all_teams = set()
        for link in boxscores_bytes:
            doc = self.read_link_bytes(link)
            game, teams = self.parse_game_stats(doc)
            all_games.append(game)
            for team in teams:
                all_teams.add(team)

        if all_games:
            league = League(
                id=int(md5(str.encode(f"{all_games[0].league}", encoding='UTF-8')).hexdigest(), 16),
                name=all_games[0].league,
                season=all_games[0].season,
                teams=list(all_teams),
                games=all_games
            )
            return league
        else:
            raise ValueError(f'No games found in {boxscores_bytes}')


    @staticmethod
    def read_link_bytes(link: bytes) -> Element:
        document_string = link.decode('latin1')
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
                with open(link,
                          mode="r",
                          encoding='latin1') as f:
                    document_string = f.read()
            else:
                raise ValueError(f'Unable to find the resource {link} (not a valid URL nor an existing file.)')
        doc = lh.fromstring(document_string)

        return doc


    @abstractmethod
    def parse_game_metadata(self,
                            doc: Element) -> Dict[str, str]:
        pass

    @abstractmethod
    def parse_game_stats(self,
                         doc: Element,
                         ids: List[Optional[str]] = None) -> Tuple[Game, Tuple[Team, Team]]:
        pass
