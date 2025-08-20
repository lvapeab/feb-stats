import numpy as np
import pandas as pd

from src.core.parsers.helpers import add_hours, remove_percentage

__all__ = [
    "transform_cum_stats_shots",
    "transform_cum_stats_minutes",
    "transform_cum_stats_blocks",
    "transform_cum_stats_fouls",
    "transform_cum_stats_rebounds",
    "transform_game_stats_df",
    "transform_starter",
]


def transform_starter(initial_series: pd.Series, prefix: str = "shots") -> pd.DataFrame:
    """Shots with the format made-attempted"""
    return pd.DataFrame(
        initial_series.map(lambda x: int(x.strip() == "*")).tolist(),
        columns=[prefix],
        dtype="int8",
    )


def transform_cum_stats_shots(shots_series: pd.Series, prefix: str = "shots") -> pd.DataFrame:
    """Shots with the format made-attempted"""

    return pd.DataFrame(
        shots_series.map(remove_percentage).str.split("/").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_attempted"],
        dtype="float32",
    )


def transform_cum_stats_minutes(minutes_timeseries: pd.Series, prefix: str = "minutes") -> pd.DataFrame:
    """Shots with the format made-attempted"""

    return pd.DataFrame({prefix: minutes_timeseries.map(add_hours)})


def transform_cum_stats_blocks(blocks_series: pd.Series, prefix: str = "blocks") -> pd.DataFrame:
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


def transform_cum_stats_rebounds(rebs_series: pd.Series, prefix: str = "rebounds") -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(
        rebs_series.str.split(" ").tolist(),
        columns=[f"defensive_{prefix}", f"offensive_{prefix}", f"total_{prefix}"],
        dtype="float32",
    )


def transform_game_stats_df(initial_df: pd.DataFrame, home_team: bool = False) -> pd.DataFrame:
    no_transform_keys = {
        "dorsal": "number",
        "nombre jugador": "player",
        "puntos": "points_made",
        "asistencias": "assists",
        "perdidas": "turnovers",
        "recuperaciones": "steals",
        "mates": "dunks",
        "valoracion": "ranking",
        "rebotes total": "total_rebounds",
        "rebotes defensivos": "defensive_rebounds",
        "rebotes ofensivos": "offensive_rebounds",
        "faltas cometidas": "fouls_made",
        "faltas recibidas": "fouls_received",
        "tapones favor": "blocks_made",
        "tapones contra": "blocks_received",
        "balance": "point_balance",
    }

    df = initial_df.rename(no_transform_keys, axis="columns")
    transform_keys = {
        # key, Dict[new_key_prefix, function]
        "tiros dos": ("2_point", transform_cum_stats_shots),
        "minutos": ("minutes", transform_cum_stats_minutes),
        "tiros tres": ("3_point", transform_cum_stats_shots),
        "tiros campo": ("field_goal", transform_cum_stats_shots),
        "tiros libres": ("free_throw", transform_cum_stats_shots),
        "inicial": ("starter", transform_starter),
    }

    for transform_key, transform_tuple in transform_keys.items():
        new_name, transform_function = transform_tuple
        new_df = transform_function(df.loc[:, transform_key], prefix=new_name)
        df = pd.concat([df, new_df], axis=1)
        df = df.drop(axis="columns", labels=transform_key)

    df.at[df.shape[0] - 1, "point_balance"] = 0.0

    cast_keys = {
        # "number": np.int,
        "starter": np.int8,
        "points_made": np.float32,
        "assists": np.float32,
        "turnovers": np.float32,
        "steals": np.float32,
        "dunks": np.float32,
        "ranking": np.float32,
        "total_rebounds": np.float32,
        "defensive_rebounds": np.float32,
        "offensive_rebounds": np.float32,
        "fouls_made": np.float32,
        "fouls_received": np.float32,
        "blocks_made": np.float32,
        "blocks_received": np.float32,
        "point_balance": np.float32,
    }
    df = df.astype(cast_keys)
    df.loc[:, "minutes"] = pd.to_timedelta(df.loc[:, "minutes"])
    df.loc[:, "games"] = 1
    df.at[df.shape[0] - 1, "point_balance"] = df.loc[:, "point_balance"].sum()
    df.at[df.shape[0] - 1, "player"] = "Total"
    return df
