import unittest
from typing import Any

import pandas as pd

from feb_stats.core.transforms import *


class TransformsTestCase(unittest.TestCase):
    def __init__(self, *args: Any, **kwargs: Any):
        super(TransformsTestCase, self).__init__(*args, **kwargs)
        data_dict = {
            "mode": {0: "Total", 1: "Total", 2: "Total"},
            "points_made": {0: 552.0, 1: 528.0, 2: 564.0},
            "assists": {0: 82.0, 1: 96.0, 2: 95.0},
            "steals": {0: 57.0, 1: 58.0, 2: 70.0},
            "turnovers": {0: 89.0, 1: 75.0, 2: 94.0},
            "dunks": {0: 0.0, 1: 1.0, 2: 4.0},
            "ranking": {0: 576.0, 1: 516.0, 2: 543.0},
            "point_balance": {0: -160.0, 1: -108.0, 2: -28.0},
            "2_point_made": {0: 130.0, 1: 134.0, 2: 159.0},
            "2_point_attempted": {0: 293.0, 1: 288.0, 2: 306.0},
            "3_point_made": {0: 55.0, 1: 58.0, 2: 63.0},
            "3_point_attempted": {0: 190.0, 1: 202.0, 2: 180.0},
            "field_goal_made": {0: 185.0, 1: 192.0, 2: 222.0},
            "field_goal_attempted": {0: 483.0, 1: 490.0, 2: 486.0},
            "free_throw_made": {0: 127.0, 1: 86.0, 2: 57.0},
            "free_throw_attempted": {0: 165.0, 1: 124.0, 2: 92.0},
            "defensive_rebounds": {0: 197.0, 1: 186.0, 2: 163.0},
            "offensive_rebounds": {0: 77.0, 1: 57.0, 2: 59.0},
            "total_rebounds": {0: 274.0, 1: 243.0, 2: 222.0},
            "fouls_made": {0: 115.0, 1: 128.0, 2: 155.0},
            "fouls_received": {0: 146.0, 1: 133.0, 2: 131.0},
            "blocks_made": {0: 13.0, 1: 6.0, 2: 18.0},
            "blocks_received": {0: 8.0, 1: 9.0, 2: 9.0},
            "games": {0: 7.0, 1: 7.0, 2: 7.0},
            "minutes": {
                0: pd.Timedelta("0 days 23:45:00"),
                1: pd.Timedelta("0 days 23:29:50"),
                2: pd.Timedelta("0 days 23:45:00"),
            },
            "oer_40_min": {0: 0.023, 1: 0.0238, 2: 0.0252},
            "der": {0: 0.88, 1: 0.82, 2: 0.90},
            "team": {0: "A", 1: "B", 2: "C"},
            "points_received": {0: 584.0, 1: 551.0, 2: 565.0},
        }
        self.data_df = pd.DataFrame(data_dict)

    def test_compute_oer(self) -> None:
        # OER = scored points / total possessions
        desired_series = pd.Series(
            {
                0: 552.0 / (483.0 + 165.0 / 2 + 89.0 + 82.0),
                1: 528.0 / (490.0 + 124.0 / 2 + 75.0 + 96.0),
                2: 564.0 / (486.0 + 92.0 / 2 + 94.0 + 95.0),
            },
            name="oer",
        )
        df = compute_oer(self.data_df)
        pd.testing.assert_series_equal(df.loc[:, "oer"], desired_series)

    def test_compute_total_possessions(self) -> None:
        # possessions = field_goal_attempted + free_throw_attempted / 2 + turnovers + assists
        desired_series = pd.Series(
            {
                0: 483.0 + 165.0 / 2 + 89.0 + 82.0,
                1: 490.0 + 124.0 / 2 + 75.0 + 96.0,
                2: 486.0 + 92.0 / 2 + 94.0 + 95.0,
            },
            name="total_possessions",
        )
        df = compute_total_possessions(self.data_df)
        pd.testing.assert_series_equal(df.loc[:, "total_possessions"], desired_series)

    def test_compute_shots_percentage(self) -> None:
        desired_series_2pt = pd.Series(
            {0: 100 * 130.0 / 293.0, 1: 100 * 134.0 / 288.0, 2: 100 * 159.0 / 306.0},
            name="2_point_percentage",
        )
        desired_series_3pt = pd.Series(
            {0: 100 * 55.0 / 190.0, 1: 100 * 58.0 / 202.0, 2: 100 * 63.0 / 180.0},
            name="3_point_percentage",
        )

        desired_series_fg = pd.Series(
            {0: 100 * 185.0 / 483.0, 1: 100 * 192.0 / 490.0, 2: 100 * 222.0 / 486.0},
            name="field_goal_percentage",
        )

        desired_series_ft = pd.Series(
            {0: 100 * 127.0 / 165.0, 1: 100 * 86.0 / 124.0, 2: 100 * 57.0 / 92.0},
            name="free_throw_percentage",
        )

        df = compute_shots_percentage(self.data_df)
        pd.testing.assert_series_equal(df.loc[:, "2_point_percentage"], desired_series_2pt)
        pd.testing.assert_series_equal(df.loc[:, "3_point_percentage"], desired_series_3pt)
        pd.testing.assert_series_equal(df.loc[:, "field_goal_percentage"], desired_series_fg)
        pd.testing.assert_series_equal(df.loc[:, "free_throw_percentage"], desired_series_ft)

    def test_compute_volumes(self) -> None:
        pass

    def test_compute_der(self) -> None:
        pass

    def test_sum_boxscores(self) -> None:
        pass

    def test_aggregate_boxscores(self) -> None:
        pass

    def test_compute_league_aggregates(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
