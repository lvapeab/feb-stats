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


def transform_cum_stats_shots(shots_series: pd.Series, prefix="shots") -> pd.DataFrame:
    """Shots with the format made-attempted"""
    split_fn = lambda x: x.split()[0]  # Remove percentage
    return pd.DataFrame(
        shots_series.map(split_fn).str.split("/").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_attempted"],
        dtype="float32",
    )


def transform_cum_stats_minutes(
    minutes_timeseries: pd.Series, prefix="minutes"
) -> pd.DataFrame:
    """Shots with the format made-attempted"""
    cast_fn = lambda x: "00:" + str(x)  # Add hours to min:seconds
    return pd.DataFrame({prefix: minutes_timeseries.map(cast_fn)})


def transform_cum_stats_blocks(
    blocks_series: pd.Series, prefix="blocks"
) -> pd.DataFrame:
    """Blocks with the format made/received"""

    return pd.DataFrame(
        blocks_series.str.split(" ").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_received"],
        dtype="float32",
    )


def transform_cum_stats_fouls(fouls_series: pd.Series, prefix="fouls") -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(
        fouls_series.str.split(" ").tolist(),
        columns=[f"{prefix}_made", f"{prefix}_received"],
        dtype="float32",
    )


def transform_cum_stats_rebounds(
    rebs_series: pd.Series, prefix="rebounds"
) -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(
        rebs_series.str.split(" ").tolist(),
        columns=[f"defensive_{prefix}", f"offensive_{prefix}", f"total_{prefix}"],
        dtype="float32",
    )


def transform_game_stats_df(
    initial_df: pd.DataFrame, home_team: bool = False
) -> pd.DataFrame:

    no_transform_keys = {
        "dorsal": "number",
        "inicial": "starter",
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
    }

    for transform_key, transform_tuple in transform_keys.items():
        new_name, transform_function = transform_tuple
        new_df = transform_function(df.loc[:, transform_key], prefix=new_name)
        df = pd.concat([df, new_df], axis=1)
        df = df.drop(axis="columns", labels=transform_key)

    df.at[df.shape[0] - 1, "point_balance"] = 0.0

    cast_keys = {
        "starter": np.bool,
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
    df.at[df.shape[0] - 1, "player"] = "Total"
    return df
