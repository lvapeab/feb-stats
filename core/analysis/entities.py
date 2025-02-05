import datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator

from core.analysis.validation_functions import (
    validate_datetime,
    validate_int,
    validate_string,
)


class Player(BaseModel):
    """Player from a team."""

    name: str
    season_stats: pd.DataFrame | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_string(v)


class Team(BaseModel):
    """Team from a league."""

    name: str
    season_stats: pd.DataFrame | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.name)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_string(v)


class Boxscore(BaseModel):
    """Boxscore from a game."""

    team: Team
    score: int
    boxscore: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: Any) -> int:
        return validate_int(v)


class Game(BaseModel):
    """Game from a league."""

    game_at: datetime.datetime
    league: str
    season: str
    main_referee: Player
    aux_referee: Player
    home_boxscore: Boxscore
    away_boxscore: Boxscore

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("game_at", mode="before")
    @classmethod
    def validate_datetime(cls, v: Any) -> datetime.date:
        return validate_datetime(v)

    @property
    def date(self) -> str:
        return self.game_at.date().strftime("%d/%m/%Y")

    @property
    def time(self) -> str:
        return self.game_at.strftime("%H:%M")

    @property
    def home_score(self) -> int:
        return self.home_boxscore.score

    @property
    def away_score(self) -> int:
        return self.away_boxscore.score

    @property
    def home_team(self) -> Team:
        return self.home_boxscore.team

    @property
    def away_team(self) -> Team:
        return self.away_boxscore.team

    @property
    def teams(self) -> list[Team]:
        return [self.home_boxscore.team, self.away_boxscore.team]


class League(BaseModel):
    """Basketball league."""

    name: str
    season: str
    teams: list[Team]
    games: list[Game]

    aggregated_games: pd.DataFrame | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.season}"
