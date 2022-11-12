from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from lxml.html import Element

from feb_stats.core.entities import Game, Team
from feb_stats.parsers.feb_livescore_stats_transforms import transform_game_stats_df
from feb_stats.parsers.generic_parser import GenericParser


class FEBLivescoreParser(GenericParser):
    def extract_nested_value(self, doc: Element, xpath: str) -> Optional[str]:
        value = None
        current_path = doc.xpath(xpath)
        while not value:
            try:
                if current_path[-1].text:
                    value = self.parse_str(current_path[-1].text, decode_bytes=True)
                    return value
                current_path = [x for x in current_path[-1]]
            except IndexError:
                return None

    def parse_game_metadata(self, doc: Element) -> Dict[str, str]:
        # Parse data by id
        hour_date = doc.xpath('//div[@class="fecha"]')

        hour_date = self.parse_str(
            hour_date[-1].text_content(), decode_bytes=True
        ).split()  # Format: "Fecha XX/XX/XXXX - HH:MM
        date = hour_date[1]
        hour = hour_date[-1]

        season = self.extract_nested_value(doc, '//span[@class="temporada"]')
        league = self.extract_nested_value(doc, '//span[@class="liga"]')
        home_team = self.extract_nested_value(
            doc, '//span[@id="_ctl0_MainContentPlaceHolderMaster_equipoLocalNombre"]'
        )
        home_score = self.extract_nested_value(
            doc, '//div[@class="columna equipo local"]//span[@class="resultado"]'
        )
        away_team = self.extract_nested_value(
            doc,
            '//span[@id="_ctl0_MainContentPlaceHolderMaster_equipoVisitanteNombre"]',
        )
        away_score = self.extract_nested_value(
            doc, '//div[@class="columna equipo visitante"]//span[@class="resultado"]'
        )

        _ = self.extract_nested_value(
            doc, '//div[@class="arbitros"]'
        )  # Format: Arbitros X W. Z | A B. C |

        # main_referee = ref[0]
        # second_referee = ref[1]
        # home_team = codecs.latin_1_encode(self.parse_str(home_score[0].text_content()))
        metadata_dict = {
            "date": date,
            "hour": hour,
            "league": league,
            "season": season,
            "home_team": home_team,
            "home_score": home_score,
            "away_team": away_team,
            "away_score": away_score,
            # TODO(alvaro): Parse referees
            "main_referee": "-",  # self.parse_str(main_referee),
            "second_referee": "-",  # self.parse_str(second_referee),
        }

        return metadata_dict

    def parse_game_stats(
        self, doc: Element, ids: Optional[Union[List[Tuple[str, bool]], str]] = None
    ) -> Tuple[Game, Tuple[Team, Team]]:
        ids = ids or '//table[@cellpadding="0"]//tbody'
        game_stats = {}
        metadata = self.parse_game_metadata(doc)

        table_local, table_away = self.get_elements(doc, str(ids))[-2:]
        if table_away is None or table_local is None:
            raise ValueError(f"Unable to parse stats from {ids}")

        for local, table in zip((True, False), (table_local, table_away)):
            key = "home_boxscore" if local else "away_boxscore"
            ori_df = self.elements_to_df(table, initial_row=2)
            df = transform_game_stats_df(ori_df, home_team=local)
            game_stats[key] = df

        assert game_stats
        return self.create_objects(metadata, game_stats)

    def elements_to_df(
        self,
        tr_elements: List[Element],
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
                data = self.parse_str(t.text_content(), decode_bytes=True)
                # Append the data to the empty list of the i'th column
                row[column_title] = data
            table_rows.append(row)

        # data_dict = {title: column for (title, column) in table_rows}
        df = pd.DataFrame(table_rows)
        return df
