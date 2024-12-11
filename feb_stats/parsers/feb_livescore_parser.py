import pandas as pd
from lxml.html import Element

from feb_stats.core.entities import Game
from feb_stats.parsers.feb_livescore_stats_transforms import transform_game_stats_df
from feb_stats.parsers.generic_parser import GenericParser


class FEBLivescoreParser(GenericParser):
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
    def parse_game_stats(
        cls,
        doc: Element,
        ids: list[tuple[str, bool]] | str | None = None,
    ) -> Game:
        ids = ids or '//table[@cellpadding="0" and @cellspacing="0"]//tbody'
        game_stats = {}
        metadata = cls.parse_game_metadata(doc)

        table_local, table_away = cls.get_elements(doc, str(ids))[-2:]
        if table_away is None or table_local is None:
            raise ValueError(f"Unable to parse stats from {ids}")

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
