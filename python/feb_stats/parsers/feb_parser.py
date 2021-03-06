from lxml.html import Element
from typing import Dict, Optional, List, Tuple
from hashlib import md5
import pandas as pd

from python.feb_stats.parsers.generic_parser import GenericParser
from python.feb_stats.parsers.feb_stats_transforms import transform_game_stats_df
from python.feb_stats.entities import Game, Boxscore, Team, Player


class FEBParser(GenericParser):
    def parse_game_metadata(self, doc: Element) -> Dict[str, str]:
        # Parse data by id
        date = doc.xpath('//span[@id="fechaLabel"]')
        hour = doc.xpath('//span[@id="horaLabel"]')
        league = doc.xpath('//span[@id="paginaTitulo_ligaLabel"]')
        season = doc.xpath('//span[@id="paginaTitulo_temporadaLabel"]')
        home_team = doc.xpath('//a[@id="equipoLocalHyperLink"]')
        home_score = doc.xpath('//span[@id="resultadoLocalLabel"]')
        away_team = doc.xpath('//a[@id="equipoVisitanteHyperLink"]')
        away_score = doc.xpath('//span[@id="resultadoVisitanteLabel"]')

        main_referee = doc.xpath('//span[@id="arbitroPrincipalLabel"]')
        second_referee = doc.xpath('//span[@id="arbitroAuxiliarLabel"]')

        metadata_dict = {
            "date": self.parse_str(date[0].text_content()),
            "hour": self.parse_str(hour[0].text_content()),
            "league": self.parse_str(league[0].text_content()),
            "season": self.parse_str(season[0].text_content()),
            "home_team": self.parse_str(home_team[0].text_content()),
            "home_score": self.parse_str(home_score[0].text_content()),
            "away_team": self.parse_str(away_team[0].text_content()),
            "away_score": self.parse_str(away_score[0].text_content()),
            "main_referee": self.parse_str(main_referee[0].text_content()),
            "second_referee": self.parse_str(second_referee[0].text_content()),
        }

        return metadata_dict

    def parse_game_stats(
        self, doc: Element, ids: List[Optional[str]] = None
    ) -> Tuple[Game, Tuple[Team, Team]]:
        ids = ids or [
            ('//table[@id="jugadoresLocalDataGrid"]//tr', True),
            ('//table[@id="jugadoresVisitanteDataGrid"]//tr', False),
        ]
        game_stats = {}
        metadata = self.parse_game_metadata(doc)

        for (doc_id, local) in ids:
            elements = self.get_elements(doc, doc_id)
            key = "home_boxscore" if local else "away_boxscore"
            if elements:
                ori_df = self.elements_to_df(elements, initial_row=2, n_elem=18)
                df = transform_game_stats_df(ori_df, home_team=local)
                game_stats[key] = df
            else:
                raise ValueError(f"Unable to parse stats from {doc_id}")
        home_team = Team(
            id=int(
                md5(str.encode(metadata["home_team"], encoding="UTF-8")).hexdigest(), 16
            ),
            name=metadata["home_team"],
        )
        away_team = Team(
            id=int(
                md5(str.encode(metadata["away_team"], encoding="UTF-8")).hexdigest(), 16
            ),
            name=metadata["away_team"],
        )
        game = Game(
            id=int(
                md5(
                    str.encode(
                        f"{metadata['league']}_{metadata['date']}_{metadata['home_team']}_{metadata['away_team']}",
                        encoding="UTF-8",
                    )
                ).hexdigest(),
                16,
            ),
            date=metadata["date"],
            hour=metadata["hour"],
            league=metadata["league"],
            season=metadata["season"],
            home_team=home_team,
            home_score=int(metadata["home_score"]),
            away_team=away_team,
            away_score=int(metadata["away_score"]),
            main_referee=Player(
                id=int(
                    md5(
                        str.encode(metadata["main_referee"], encoding="UTF-8")
                    ).hexdigest(),
                    16,
                ),
                name=metadata["main_referee"],
            ),
            aux_referee=Player(
                id=int(
                    md5(
                        str.encode(metadata["second_referee"], encoding="UTF-8")
                    ).hexdigest(),
                    16,
                ),
                name=metadata["second_referee"],
            ),
            local_boxscore=Boxscore(
                id=int(
                    md5(
                        str.encode(
                            f"{metadata['league']}_{metadata['date']}_{metadata['home_team']}",
                            encoding="UTF-8",
                        )
                    ).hexdigest(),
                    16,
                ),
                boxscore=game_stats["home_boxscore"],
            ),
            away_boxscore=Boxscore(
                id=int(
                    md5(
                        str.encode(
                            f"{metadata['league']}_{metadata['date']}_{metadata['away_team']}",
                            encoding="UTF-8",
                        )
                    ).hexdigest(),
                    16,
                ),
                boxscore=game_stats["away_boxscore"],
            ),
        )
        return game, (home_team, away_team)

    def elements_to_df(
        self, tr_elements: List[Element], initial_row: int = 2, n_elem: int = 0
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
