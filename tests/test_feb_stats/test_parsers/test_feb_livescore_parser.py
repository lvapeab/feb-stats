from pathlib import Path
import glob
import json
import unittest
from typing import Any

from feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser


class TestLivescoreParserScenarios(unittest.TestCase):
    @staticmethod
    def read_labeled_html_json(filename: str) -> dict:
        with open(filename) as f:
            labeled_file = json.load(f)
        return labeled_file

    def __init__(self, *args: Any, **kwargs: Any):
        super(TestLivescoreParserScenarios, self).__init__(*args, **kwargs)

    def test_scenarios(self):
        test_dir = Path(__file__).parent.parent.parent
        for test_file in glob.glob(str(test_dir / "data/*_livescore.json")):
            labeled_file = self.read_labeled_html_json(test_file)
            raw_text = labeled_file["raw_text"]
            self.assert_get_elements(raw_text, labeled_file)
            self.assert_elements_to_df(raw_text, labeled_file)
            self.assert_parse_game_metadata(raw_text, labeled_file)
            self.assert_parse_game_stats(raw_text, labeled_file)

    def assert_get_elements(self, input_doc, expected_dict) -> None:
        doc = FEBLivescoreParser.read_link_file(input_doc)
        id = '//table[@cellpadding="0" and @cellspacing="0"]//tbody'
        table_local, table_away = FEBLivescoreParser.get_elements(doc, id)[-2:]
        self.assertEqual(expected_dict["local_table_rows"], len(table_local))
        self.assertEqual(expected_dict["away_table_rows"], len(table_away))

    def assert_elements_to_df(self, input_doc, expected_dict) -> None:
        initial_row = 2
        doc = FEBLivescoreParser.read_link_file(input_doc)
        id = '//table[@cellpadding="0" and @cellspacing="0"]//tbody'
        table_local, table_away = FEBLivescoreParser.get_elements(doc, id)[-2:]
        local_df = FEBLivescoreParser.elements_to_df(table_local, initial_row=initial_row, discard_last=0)
        away_df = FEBLivescoreParser.elements_to_df(table_away, initial_row=initial_row, discard_last=0)
        self.assertEqual(local_df.shape, (expected_dict["local_table_rows"] - initial_row, 22))
        self.assertEqual(away_df.shape, (expected_dict["away_table_rows"] - initial_row, 22))
        for df in (local_df, away_df):
            self.assertSetEqual(
                set(df.columns),
                {
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
                },
            )

    def assert_parse_game_metadata(self, input_doc, expected_dict) -> None:
        doc = FEBLivescoreParser.read_link_file(input_doc)
        game_metadata = FEBLivescoreParser.parse_game_metadata(doc)

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
        doc = FEBLivescoreParser.read_link_file(input_doc)
        game, (local_team, away_team) = FEBLivescoreParser.parse_game_stats(doc)
        self.assertEqual(expected_dict["date"], game.date)
        self.assertEqual(expected_dict["time"], game.time)
        self.assertEqual(expected_dict["league"], game.league)
        self.assertEqual(expected_dict["season"], game.season)
        self.assertEqual(int(expected_dict["home_score"]), game.home_score)
        self.assertEqual(int(expected_dict["away_score"]), game.away_score)
        self.assertEqual(expected_dict["home_team"], local_team.name)
        self.assertEqual(expected_dict["away_team"], away_team.name)
        # self.assertEqual(game.main_referee, "SERRAT MOLINS. ALBERT")
        # self.assertEqual(game.aux_referee, "ARAQUE CACERES. MAURO")


class GenericParserTestCase(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any):
        super(GenericParserTestCase, self).__init__(*args, **kwargs)
        test_dir = Path(__file__).parent.parent.parent

        self.test_files = [
            str(test_dir / "data/1_livescore.html"),
            str(test_dir / "data/3_livescore.htm"),
        ]

    def test_parse_str(self) -> None:
        test_str = "             Rebotes                            D          O          T "
        desired_test_str = "Rebotes D O T"
        out_str = FEBLivescoreParser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "\n\t\t\t\t\t\t\n\t\t\t\t\nRebotes\n\t\t\t\t\t\n\t\t\tD\n\t\t\t\t\t\tO\n\t\t\t\t\t\tT\n\t\t\t\t\t\t"
        out_str = FEBLivescoreParser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "                       0                               0                               0           "
        desired_test_str = "0 0 0"
        out_str = FEBLivescoreParser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "\n\t\t\t\t\t\t\n\t\t\t\t\n0\n\t\t\t\t\t\n\t\t\t0\n\t\t\t\t\t\t0\t\t\t\t\t"
        out_str = FEBLivescoreParser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "             Tapones                            Fa          Co          "
        desired_test_str = "Tapones Fa Co"
        out_str = FEBLivescoreParser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = "                       0                               0           "
        desired_test_str = "0 0"
        out_str = FEBLivescoreParser.parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

    def test_parse_boxscores(self) -> None:
        for test_file in self.test_files:
            with open(test_file, mode="rb") as f:
                boxscores_bytes = f.read()
            league = FEBLivescoreParser.parse_boxscores([boxscores_bytes], FEBLivescoreParser.read_link_bytes)
            self.assertEqual(2, len(league.teams))
            self.assertEqual(1, len(league.games))

    def test_read_link_bytes(self) -> None:
        for test_file in self.test_files:
            with open(test_file, mode="rb") as f:
                link_bytes = f.read()
            doc = FEBLivescoreParser.read_link_bytes(link_bytes)
            self.assertIsNotNone(doc.forms)
            self.assertIsNotNone(doc.body)
            self.assertIsNotNone(doc.head)

    def test_read_link_file(self) -> None:
        for test_file in self.test_files:
            doc = FEBLivescoreParser.read_link_file(test_file)
            self.assertIsNotNone(doc.forms)
            self.assertIsNotNone(doc.body)
            self.assertIsNotNone(doc.head)
