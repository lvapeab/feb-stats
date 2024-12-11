import pandas as pd
from lxml.html import Element

from feb_stats.core.entities import Game, Team
from feb_stats.parsers.feb_stats_transforms import transform_game_stats_df
from feb_stats.parsers.generic_parser import GenericParser


class FEBParser(GenericParser):
    @classmethod
    def parse_game_metadata(cls, doc: Element) -> dict[str, str]:
        # Parse data by id
        date = doc.xpath('//span[@id="fechaLabel"]')
        time = doc.xpath('//span[@id="horaLabel"]')
        league = doc.xpath('//span[@id="paginaTitulo_ligaLabel"]')
        season = doc.xpath('//span[@id="paginaTitulo_temporadaLabel"]')
        home_team = doc.xpath('//a[@id="equipoLocalHyperLink"]')
        home_score = doc.xpath('//span[@id="resultadoLocalLabel"]')
        away_team = doc.xpath('//a[@id="equipoVisitanteHyperLink"]')
        away_score = doc.xpath('//span[@id="resultadoVisitanteLabel"]')

        main_referee = doc.xpath('//span[@id="arbitroPrincipalLabel"]')
        second_referee = doc.xpath('//span[@id="arbitroAuxiliarLabel"]')

        metadata_dict = {
            "date": cls.parse_str(date[0].text_content()),
            "time": cls.parse_str(time[0].text_content()),
            "league": cls.parse_str(league[0].text_content()),
            "season": cls.parse_str(season[0].text_content()),
            "home_team": cls.parse_str(home_team[0].text_content()),
            "home_score": cls.parse_str(home_score[0].text_content()),
            "away_team": cls.parse_str(away_team[0].text_content()),
            "away_score": cls.parse_str(away_score[0].text_content()),
            "main_referee": cls.parse_str(main_referee[0].text_content()),
            "second_referee": cls.parse_str(second_referee[0].text_content()),
        }

        return metadata_dict

    @classmethod
    def parse_game_stats(
        cls, doc: Element, ids: list[tuple[str, bool]] | str | None = None
    ) -> tuple[Game, tuple[Team, Team]]:
        ids = ids or [
            ('//table[@id="jugadoresLocalDataGrid"]//tr', True),
            ('//table[@id="jugadoresVisitanteDataGrid"]//tr', False),
        ]
        game_stats = {}
        metadata: dict[str, str] = cls.parse_game_metadata(doc)

        assert not isinstance(ids, str)
        for doc_id, local in ids:
            elements = cls.get_elements(doc, doc_id)
            key = "home_boxscore" if local else "away_boxscore"
            if elements:
                ori_df = cls.elements_to_df(elements, initial_row=2, n_elem=18)
                df = transform_game_stats_df(ori_df, home_team=local)
                game_stats[key] = df
            else:
                raise ValueError(f"Unable to parse stats from {doc_id}")
        assert game_stats
        return cls.create_objects(metadata, game_stats)

    @classmethod
    def elements_to_df(cls, tr_elements: list[Element], initial_row: int = 2, n_elem: int = 0) -> pd.DataFrame:
        col: list = []
        i = 0
        # For each row, store each first element (header) and an empty list
        for t in tr_elements[0]:
            i += 1
            name = cls.parse_str(t.text_content())
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
                    data = cls.parse_str(t.text_content())
                    # Append the data to the empty list of the i'th column
                    col[i][1].append(data)
                    # Increment i for the next column
                    i += 1

        data_dict = {title: column for (title, column) in col}
        df = pd.DataFrame(data_dict)
        return df
