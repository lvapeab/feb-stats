import pandas as pd
from django.test import TestCase

from core.parsers.transforms import (
    transform_cum_stats_blocks,
    transform_cum_stats_fouls,
    transform_cum_stats_minutes,
    transform_cum_stats_rebounds,
    transform_cum_stats_shots,
)


class FebStatsTransformsTestCase(TestCase):
    def test_transform_cum_stats_shots(self) -> None:
        # feb.es boxscore format.
        series = pd.Series(["1/4 25%", "6/12 50%"])
        prefix = "x"
        df = transform_cum_stats_shots(series, prefix=prefix)
        desired_df = pd.DataFrame({f"{prefix}_made": [1, 6], f"{prefix}_attempted": [4, 12]}, dtype="float32")
        pd.testing.assert_frame_equal(df, desired_df)

    def test_transform_cum_stats_minutes(self) -> None:
        # feb.es boxscore format.
        series = pd.Series(["26:15", "26:12"])
        prefix = "x"
        df = transform_cum_stats_minutes(series, prefix=prefix)
        desired_df = pd.DataFrame({f"{prefix}": ["00:26:15", "00:26:12"]})
        pd.testing.assert_frame_equal(df, desired_df)

    def test_transform_cum_stats_blocks(self) -> None:
        # feb.es boxscore format.
        series = pd.Series(["0 0", "2 5"])
        prefix = "x"
        df = transform_cum_stats_blocks(series, prefix=prefix)
        desired_df = pd.DataFrame({f"{prefix}_made": [0, 2], f"{prefix}_received": [0, 5]}, dtype="float32")
        pd.testing.assert_frame_equal(df, desired_df)

    def test_transform_cum_stats_fouls(self) -> None:
        # feb.es boxscore format.
        series = pd.Series(["0 0", "2 5"])
        prefix = "x"
        df = transform_cum_stats_fouls(series, prefix=prefix)
        desired_df = pd.DataFrame({f"{prefix}_made": [0, 2], f"{prefix}_received": [0, 5]}, dtype="float32")
        pd.testing.assert_frame_equal(df, desired_df)

    def test_transform_cum_stats_rebounds(self) -> None:
        # feb.es boxscore format.
        series = pd.Series(["0 0 0", "2 5 7"])
        prefix = "x"
        df = transform_cum_stats_rebounds(series, prefix=prefix)
        desired_df = pd.DataFrame(
            {
                f"defensive_{prefix}": [0, 2],
                f"offensive_{prefix}": [0, 5],
                f"total_{prefix}": [0, 7],
            },
            dtype="float32",
        )
        pd.testing.assert_frame_equal(df, desired_df)
