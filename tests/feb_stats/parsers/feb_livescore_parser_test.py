import unittest
from typing import Any

from feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser


class GenericParserTestCase_1(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any):
        super(GenericParserTestCase_1, self).__init__(*args, **kwargs)
        self.parser = FEBLivescoreParser()
        self.test_file = "tests/test_data/1_livescore.html"

    def test_parse_str(self) -> None:
        test_str = (
            "             Rebotes                            D          O          T "
        )
        desired_test_str = "Rebotes D O T"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "\n\t\t\t\t\t\t\n\t\t\t\t\nRebotes\n\t\t\t\t\t\n\t\t\tD\n\t\t\t\t\t\tO\n\t\t\t\t\t\tT\n\t\t\t\t\t\t"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "                       0                               0                               0           "
        desired_test_str = "0 0 0"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = (
            "\n\t\t\t\t\t\t\n\t\t\t\t\n0\n\t\t\t\t\t\n\t\t\t0\n\t\t\t\t\t\t0\t\t\t\t\t"
        )
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = (
            "             Tapones                            Fa          Co          "
        )
        desired_test_str = "Tapones Fa Co"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "                       0                               0           "
        desired_test_str = "0 0"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

    def test_get_elements(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        id = '//table[@cellpadding="0"]//tbody'
        table_local, table_away = self.parser.get_elements(doc, id)
        self.assertEqual(len(table_local), 13)
        self.assertEqual(len(table_away), 15)

    def test_elements_to_df(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        id = '//table[@cellpadding="0"]//tbody'
        table_local, table_away = self.parser.get_elements(doc, id)
        local_df = self.parser.elements_to_df(
            table_local, initial_row=2, discard_last=0
        )
        away_df = self.parser.elements_to_df(table_away, initial_row=2, discard_last=0)
        self.assertEqual(local_df.shape, (11, 22))
        self.assertEqual(away_df.shape, (13, 22))
        for df in (local_df, away_df):
            self.assertListEqual(
                list(df.columns),
                [
                    "inicial",
                    "dorsal",
                    "nombre jugador",
                    "minutos",
                    "puntos",
                    "tiros dos",
                    "tiros tres",
                    "tiros campo",
                    "tiros libres",
                    "rebotes total",
                    "rebotes defensivos",
                    "rebotes ofensivos",
                    "asistencias",
                    "recuperaciones",
                    "perdidas",
                    "tapones favor",
                    "tapones contra",
                    "mates",
                    "faltas cometidas",
                    "faltas recibidas",
                    "valoracion",
                    "balance",
                ],
            )

    def test_parse_boxscores(self) -> None:
        with open(self.test_file, mode="rb") as f:
            boxscores_bytes = f.read()
        league = self.parser.parse_boxscores([boxscores_bytes])
        self.assertEqual(2, len(league.teams))
        self.assertEqual(1, len(league.games))

    def test_read_link_bytes(self) -> None:
        with open(self.test_file, mode="rb") as f:
            link_bytes = f.read()
        doc = self.parser.read_link_bytes(link_bytes)
        self.assertIsNotNone(doc.forms)
        self.assertIsNotNone(doc.body)
        self.assertIsNotNone(doc.head)

    def test_read_link_file(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        self.assertIsNotNone(doc.forms)
        self.assertIsNotNone(doc.body)
        self.assertIsNotNone(doc.head)

    def test_parse_game_metadata(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        game_metadata = self.parser.parse_game_metadata(doc)

        desired_dict = {
            "date": "08/03/2020",
            "hour": "18:00",
            "league": "LIGA EBA",
            "season": "2019/2020",
            "home_team": "HERO JAIRIS",
            "home_score": "75",
            "away_team": "UCAM MURCIA JIFFY",
            "away_score": "68",
            "main_referee": "-",  # "SERRAT MOLINS. ALBERT",
            "second_referee": "-",  # "ARAQUE CACERES. MAURO",
        }
        self.assertDictEqual(game_metadata, desired_dict)

    def test_parse_game_stats(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        game, (local_team, away_team) = self.parser.parse_game_stats(doc)
        self.assertEqual(game.date, "08/03/2020")
        self.assertEqual(game.hour, "18:00")
        self.assertEqual(game.league, "LIGA EBA")
        self.assertEqual(game.season, "2019/2020")
        self.assertEqual(game.home_score, 75)
        self.assertEqual(game.away_score, 68)
        # self.assertEqual(game.main_referee, "SERRAT MOLINS. ALBERT")
        # self.assertEqual(game.aux_referee, "ARAQUE CACERES. MAURO")
        self.assertEqual(local_team.name, "HERO JAIRIS")
        self.assertEqual(away_team.name, "UCAM MURCIA JIFFY")


class GenericParserTestCase_3(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any):
        super(GenericParserTestCase_3, self).__init__(*args, **kwargs)
        self.parser = FEBLivescoreParser()
        self.test_file = "tests/test_data/3_livescore.html"

    def test_parse_str(self) -> None:
        test_str = (
            "             Rebotes                            D          O          T "
        )
        desired_test_str = "Rebotes D O T"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "\n\t\t\t\t\t\t\n\t\t\t\t\nRebotes\n\t\t\t\t\t\n\t\t\tD\n\t\t\t\t\t\tO\n\t\t\t\t\t\tT\n\t\t\t\t\t\t"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "                       0                               0                               0           "
        desired_test_str = "0 0 0"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = (
            "\n\t\t\t\t\t\t\n\t\t\t\t\n0\n\t\t\t\t\t\n\t\t\t0\n\t\t\t\t\t\t0\t\t\t\t\t"
        )
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = (
            "             Tapones                            Fa          Co          "
        )
        desired_test_str = "Tapones Fa Co"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "                       0                               0           "
        desired_test_str = "0 0"
        out_str = self.parser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

    def test_get_elements(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        id = '//table[@cellpadding="0"]//tbody'
        table_local, table_away = self.parser.get_elements(doc, id)[-2:]
        self.assertEqual(len(table_local), 13)
        self.assertEqual(len(table_away), 15)

    def test_elements_to_df(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        id = '//table[@cellpadding="0"]//tbody'
        table_local, table_away = self.parser.get_elements(doc, id)[-2:]
        local_df = self.parser.elements_to_df(
            table_local, initial_row=2, discard_last=0
        )
        away_df = self.parser.elements_to_df(table_away, initial_row=2, discard_last=0)
        self.assertEqual(local_df.shape, (11, 22))
        self.assertEqual(away_df.shape, (13, 22))
        for df in (local_df, away_df):
            self.assertListEqual(
                list(df.columns),
                [
                    "inicial",
                    "dorsal",
                    "nombre jugador",
                    "minutos",
                    "puntos",
                    "tiros dos",
                    "tiros tres",
                    "tiros campo",
                    "tiros libres",
                    "rebotes ofensivos",
                    "rebotes defensivos",
                    "rebotes total",
                    "asistencias",
                    "recuperaciones",
                    "perdidas",
                    "tapones favor",
                    "tapones contra",
                    "mates",
                    "faltas cometidas",
                    "faltas recibidas",
                    "valoracion",
                    "balance",
                ],
            )

    def test_parse_boxscores(self) -> None:
        with open(self.test_file, mode="rb") as f:
            boxscores_bytes = f.read()
        league = self.parser.parse_boxscores([boxscores_bytes])
        self.assertEqual(2, len(league.teams))
        self.assertEqual(1, len(league.games))

    def test_read_link_bytes(self) -> None:
        with open(self.test_file, mode="rb") as f:
            link_bytes = f.read()
        doc = self.parser.read_link_bytes(link_bytes)
        self.assertIsNotNone(doc.forms)
        self.assertIsNotNone(doc.body)
        self.assertIsNotNone(doc.head)

    def test_read_link_file(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        self.assertIsNotNone(doc.forms)
        self.assertIsNotNone(doc.body)
        self.assertIsNotNone(doc.head)

    def test_parse_game_metadata(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        game_metadata = self.parser.parse_game_metadata(doc)

        desired_dict = {
            "date": "14-10-2022",
            "hour": "20:30",
            "league": "LIGA EBA",
            "season": "2022/2023",
            "home_team": "JOVENS L´ELIANA",
            "home_score": "63",
            "away_team": "NB PATERNA POWER ELECTRONICS",
            "away_score": "79",
            "main_referee": "-",  # "SERRAT MOLINS. ALBERT",
            "second_referee": "-",  # "ARAQUE CACERES. MAURO",
        }
        self.assertDictEqual(game_metadata, desired_dict)

    def test_parse_game_stats(self) -> None:
        doc = self.parser.read_link_file(self.test_file)
        game, (local_team, away_team) = self.parser.parse_game_stats(doc)
        self.assertEqual(game.date, "14-10-2022")
        self.assertEqual(game.hour, "20:30")
        self.assertEqual(game.league, "LIGA EBA")
        self.assertEqual(game.season, "2022/2023")
        self.assertEqual(game.home_score, 63)
        self.assertEqual(game.away_score, 79)
        # self.assertEqual(game.main_referee, "HERROJO JIMENEZ. JORGE")
        # self.assertEqual(game.aux_referee, "GARCIA SALA. ADRIAN")
        self.assertEqual(local_team.name, "JOVENS L´ELIANA")
        self.assertEqual(away_team.name, "NB PATERNA POWER ELECTRONICS")


if __name__ == "__main__":
    unittest.main()
