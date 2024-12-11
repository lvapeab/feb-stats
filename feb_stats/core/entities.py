from dataclasses import dataclass
from typing import Generic, TypeVar

import pandas as pd

T = TypeVar("T")


@dataclass(frozen=True)
class Player(Generic[T]):
    """Player from a team."""

    id: str
    name: str
    season_stats: pd.DataFrame | None = None


@dataclass(frozen=True)
class Team(Generic[T]):
    """Team from a league."""

    id: str
    name: str
    season_stats: pd.DataFrame | None = None

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.name)


@dataclass(frozen=True)
class Boxscore(Generic[T]):
    """Boxscore from a game."""

    boxscore: pd.DataFrame
    id: str | None = None


@dataclass(frozen=True)
class Game(Generic[T]):
    """Game from a league."""

    id: str
    date: str
    time: str
    league: str
    season: str
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int
    main_referee: Player
    aux_referee: Player
    local_boxscore: Boxscore
    away_boxscore: Boxscore


@dataclass(frozen=True)
class League(Generic[T]):
    """Basketball league."""

    id: str
    name: str
    season: str
    teams: list[Team]
    games: list[Game]
    aggregated_games: pd.DataFrame | None = None

    def __str__(self) -> str:
        return f"{self.name} - {self.season}"
