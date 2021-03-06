import codecs
from lxml.html import Element
from typing import Dict, List, Tuple
import pandas as pd
from hashlib import md5

from python.feb_stats.parsers.generic_parser import GenericParser
from python.feb_stats.parsers.feb_livescore_stats_transforms import (
    transform_game_stats_df,
)
from python.feb_stats.entities import Game, Boxscore, Team, Player


class FEBLivescoreParser(GenericParser):
    def parse_game_metadata(self, doc: Element) -> Dict[str, str]:
        # Parse data by id
        hour_date = doc.xpath('//div[@class="fecha"]')

        hour_date = self.parse_str(
            hour_date[0].text_content(), decode_bytes=True
        ).split()  # Format: "Fecha XX/XX/XXXX - HH:MM
        date = hour_date[1]
        hour = hour_date[-1]

        league = doc.xpath('//span[@class="liga"]')
        season = doc.xpath('//span[@class="temporada"]')

        home_team = doc.xpath(
            '//span[@id="_ctl0_MainContentPlaceHolderMaster_equipoLocalNombre"]'
        )
        home_score = doc.xpath(
            '//div[@class="columna equipo local"]//span[@class="resultado"]'
        )
        away_team = doc.xpath(
            '//span[@id="_ctl0_MainContentPlaceHolderMaster_equipoVisitanteNombre"]'
        )
        away_score = doc.xpath(
            '//div[@class="columna equipo visitante"]//span[@class="resultado"]'
        )
        referees = doc.xpath(
            '//div[@class="arbitros"]'
        )  # Format: Arbitros X W. Z | A B. C |

        # ref = " ".join(self.parse_str(referees[0].text_content()).split()[1:]).split(
        #     "|"
        # )

        # main_referee = ref[0]
        # second_referee = ref[1]
        # home_team = codecs.latin_1_encode(self.parse_str(home_score[0].text_content()))
        metadata_dict = {
            "date": date,
            "hour": hour,
            "league": self.parse_str(league[0].text, decode_bytes=True),
            "season": self.parse_str(season[0].text, decode_bytes=True),
            "home_team": self.parse_str(home_team[0].text, decode_bytes=True),
            "home_score": self.parse_str(home_score[0].text, decode_bytes=True),
            "away_team": self.parse_str(away_team[0].text, decode_bytes=True),
            "away_score": self.parse_str(away_score[0].text, decode_bytes=True),
            # TODO(alvaro): Parse referees
            "main_referee": "-",  # self.parse_str(main_referee),
            "second_referee": "-",  # self.parse_str(second_referee),
        }

        return metadata_dict

    def parse_game_stats(
        self, doc: Element, ids: str = None
    ) -> Tuple[Game, Tuple[Team, Team]]:
        ids = ids or '//table[@cellpadding="0"]//tbody'
        game_stats = {}
        metadata = self.parse_game_metadata(doc)

        table_local, table_away = self.get_elements(doc, ids)[-2:]
        if table_away is None or table_local is None:
            raise ValueError(f"Unable to parse stats from {ids}")

        for local, table in zip((True, False), (table_local, table_away)):
            key = "home_boxscore" if local else "away_boxscore"
            ori_df = self.elements_to_df(table, initial_row=2)
            df = transform_game_stats_df(ori_df, home_team=local)
            game_stats[key] = df
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
        self, tr_elements: List[Element], initial_row: int = 2, discard_last: int = 0,
    ) -> pd.DataFrame:
        table_rows = []
        # Since out first row is the header, data is stored on the second row onwards
        for j in range(initial_row, len(tr_elements) - discard_last):
            # T is our j'th row
            T = tr_elements[j]
            row = {}
            for t in T.iterchildren():

                column_title = t.attrib["class"]
                data = self.parse_str(t.text_content(), decode_bytes=True)
                # Append the data to the empty list of the i'th column
                row[column_title] = data
            table_rows.append(row)

        # data_dict = {title: column for (title, column) in table_rows}
        df = pd.DataFrame(table_rows)
        return df
