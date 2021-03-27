import numpy as np
import pandas as pd

__all__ = [
    "transform_cum_stats_shots",
    "transform_cum_stats_minutes",
    "transform_cum_stats_blocks",
    "transform_cum_stats_fouls",
    "transform_cum_stats_rebounds",
    "transform_game_stats_df",
]


def transform_cum_stats_shots(shots_series: pd.Series, prefix: str = "shots"
                              ) -> pd.DataFrame:
    """Shots with the format made-attempted"""
    split_fn = lambda x: x.split()[0]  # Remove percentage
    return pd.DataFrame(
        shots_series.map(split_fn).str.split("/").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_attempted"],
        dtype="float32",
    )


def transform_cum_stats_minutes(minutes_timeseries: pd.Series,
                                prefix: str = "minutes") -> pd.DataFrame:
    """Shots with the format made-attempted"""
    cast_fn = lambda x: "00:" + str(x)  # Add hours to min:seconds
    return pd.DataFrame({prefix: minutes_timeseries.map(cast_fn)})


def transform_cum_stats_blocks(
        blocks_series: pd.Series, prefix: str = "blocks"
) -> pd.DataFrame:
    """Blocks with the format made/received"""

    return pd.DataFrame(
        blocks_series.str.split(" ").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_received"],
        dtype="float32",
    )


def transform_cum_stats_fouls(fouls_series: pd.Series, prefix: str = "fouls") -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(
        fouls_series.str.split(" ").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_received"],
        dtype="float32",
    )


def transform_cum_stats_rebounds(
        rebs_series: pd.Series, prefix: str = "rebounds"
) -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(
        rebs_series.str.split(" ").tolist(),
        columns=[f"defensive_{prefix}", f"offensive_{prefix}", f"total_{prefix}"],
        dtype="float32",
    )


def transform_game_stats_df(initial_df: pd.DataFrame, home_team: bool) -> pd.DataFrame:
    if home_team:
        rebounds_str = "Rebotes D O T"
        blocks_str = "Tapones Fa Co"
    else:
        rebounds_str = "Rebotes Def Of To"
        blocks_str = "Tapones F C"

    no_transform_keys = {
        "N": "number",
        "I": "starter",
        "Jugador": "player",
        "Ptos": "points_made",
        "As": "assists",
        "B.P": "turnovers",
        "B.R": "steals",
        "Mat": "dunks",
        "Val": "ranking",
        "+/-": "point_balance",
    }

    df = initial_df.rename(no_transform_keys, axis="columns")
    df = df.drop("starter", axis="columns")  # TODO: Manage this
    transform_keys = {
        # key, Dict[new_key_prefix, function]
        "2 pt": ("2_point", transform_cum_stats_shots),
        "Min": ("minutes", transform_cum_stats_minutes),
        "3 pt": ("3_point", transform_cum_stats_shots),
        "T.Camp": ("field_goal", transform_cum_stats_shots),
        "T.L": ("free_throw", transform_cum_stats_shots),
        rebounds_str: ("rebounds", transform_cum_stats_rebounds),
        "Faltas C R": ("fouls", transform_cum_stats_fouls),
        blocks_str: ("blocks", transform_cum_stats_blocks),
    }

    for transform_key, transform_tuple in transform_keys.items():
        new_name, transform_function = transform_tuple
        new_df = transform_function(df.loc[:, transform_key], prefix=new_name)
        df = pd.concat([df, new_df], axis=1)
        df = df.drop(axis="columns", labels=transform_key)

    df.at[df.shape[0] - 1, "point_balance"] = 0.0

    cast_keys = {
        "points_made": np.float32,
        "point_balance": np.float32,
        "assists": np.float32,
        "turnovers": np.float32,
        "steals": np.float32,
        "dunks": np.float32,
        "ranking": np.float32,
    }
    df = df.astype(cast_keys)
    df.loc[:, "minutes"] = pd.to_timedelta(df.loc[:, "minutes"])
    df.loc[:, "games"] = 1
    df.at[df.shape[0] - 1, "point_balance"] = df.loc[:, "point_balance"].sum()

    return df
