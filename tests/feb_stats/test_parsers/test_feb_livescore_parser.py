import glob
import json
import unittest
from typing import Any, Dict

from feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser


class TestLivescoreParserScenarios(unittest.TestCase):
    @staticmethod
    def read_labeled_html_json(filename: str) -> Dict:
        with open(filename, "r") as f:
            labeled_file = json.load(f)
        return labeled_file

    def __init__(self, *args: Any, **kwargs: Any):
        super(TestLivescoreParserScenarios, self).__init__(*args, **kwargs)
        self.parser = FEBLivescoreParser()
        for test_file in glob.glob("tests/data/*_livescore.json"):
            labeled_file = self.read_labeled_html_json(test_file)
            raw_text = labeled_file["raw_text"]
            self.assert_get_elements(raw_text, labeled_file)
            self.assert_elements_to_df(raw_text, labeled_file)
            self.assert_parse_game_metadata(raw_text, labeled_file)
            self.assert_parse_game_stats(raw_text, labeled_file)

    def assert_get_elements(self, input_doc, expected_dict) -> None:
        doc = self.parser.read_link_file(input_doc)
        id = '//table[@cellpadding="0"]//tbody'
        table_local, table_away = self.parser.get_elements(doc, id)
        self.assertEqual(len(table_local), expected_dict["local_table_rows"])
        self.assertEqual(len(table_away), expected_dict["local_table_rows"])

    def assert_elements_to_df(self, input_doc, expected_dict) -> None:
        initial_row = 2
        doc = self.parser.read_link_file(input_doc)
        id = '//table[@cellpadding="0"]//tbody'
        table_local, table_away = self.parser.get_elements(doc, id)
        local_df = self.parser.elements_to_df(
            table_local, initial_row=initial_row, discard_last=0
        )
        away_df = self.parser.elements_to_df(
            table_away, initial_row=initial_row, discard_last=0
        )
        self.assertEqual(
            local_df.shape, (expected_dict["local_table_rows"] - initial_row, 22)
        )
        self.assertEqual(
            away_df.shape, (expected_dict["away_table_rows"] - initial_row, 22)
        )
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

    def assert_parse_game_metadata(self, input_doc, expected_dict) -> None:
        doc = self.parser.read_link_file(input_doc)
        game_metadata = self.parser.parse_game_metadata(doc)

        desired_dict = {
            "date": expected_dict["date"],
            "time": expected_dict["time"],
            "league": expected_dict["league"],
            "season": expected_dict["season"],
            "home_team": expected_dict["home_team"],
            "home_score": expected_dict["home_score"],
            "away_team": expected_dict["away_team"],
            "away_score": expected_dict["away_score"],
            "main_referee": "-",  # "SERRAT MOLINS. ALBERT",
            "second_referee": "-",  # "ARAQUE CACERES. MAURO",
        }
        self.assertDictEqual(game_metadata, desired_dict)

    def assert_parse_game_stats(self, input_doc, expected_dict) -> None:
        doc = self.parser.read_link_file(input_doc)
        game, (local_team, away_team) = self.parser.parse_game_stats(doc)
        self.assertEqual(game.date, expected_dict["date"])
        self.assertEqual(game.time, expected_dict["date"])
        self.assertEqual(game.league, expected_dict["league"])
        self.assertEqual(game.season, expected_dict["season"])
        self.assertEqual(game.home_score, int(expected_dict["home_score"]))
        self.assertEqual(game.away_score, int(expected_dict["away_score"]))
        # self.assertEqual(game.main_referee, "SERRAT MOLINS. ALBERT")
        # self.assertEqual(game.aux_referee, "ARAQUE CACERES. MAURO")
        self.assertEqual(local_team.name, int(expected_dict["home_team"]))
        self.assertEqual(away_team.name, int(expected_dict["away_team"]))


class GenericParserTestCase(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any):
        super(GenericParserTestCase, self).__init__(*args, **kwargs)
        self.parser = FEBLivescoreParser()
        self.test_file = "tests/data/1_livescore.html"

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
