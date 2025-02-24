import datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator

from core.analysis.validation_functions import (
    validate_datetime,
    validate_int,
    validate_string,
)
from core.models import BoxscoreEntry, Game, League, LeagueTeam, Player, Referee, Team


class PlayerData(BaseModel):
    """PlayerData from a team."""

    name: str
    exid: str

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_string(v)

    def save_to_db(self) -> Player:
        try:
            last_name, first_name = self.name.split(",", 1)
        except ValueError:
            last_name, first_name = self.name, ""
        player, _ = Player.objects.update_or_create(
            exid=self.exid,
            defaults={
                "first_name": first_name.title(),
                "last_name": last_name.title(),
            },
        )
        return player


class RefereeData(BaseModel):
    """PlayerData from a team."""

    name: str
    exid: str

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_string(v)

    def save_to_db(self) -> Referee:
        last_name, first_name = self.name.split(",", 1)
        referee, _ = Referee.objects.update_or_create(
            exid=self.exid,
            defaults={
                "first_name": first_name.title(),
                "last_name": last_name.title(),
            },
        )
        return referee


class LeagueTeamData(BaseModel):
    """LeagueTeamData from a league."""

    name: str
    exid: str
    league: "LeagueData"
    season_stats: pd.DataFrame | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.name)

    def __hash__(self) -> int:
        return hash(self.exid + self.league.name + self.league.season)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_string(v)

    def save_to_db(self, league: League) -> LeagueTeam:
        team, _ = Team.objects.update_or_create(exid=self.exid, defaults={"name": self.name})
        league_team, _ = LeagueTeam.objects.get_or_create(team=team, league=league)
        return league_team


class BoxscoreData(BaseModel):
    """BoxscoreData from a game."""

    team: "LeagueTeamData"
    score: int
    boxscore: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: Any) -> int:
        return validate_int(v)

    def save_to_db(self, game: Game, team: LeagueTeam) -> list[BoxscoreEntry]:
        boxscore_entries = []
        for entry in self.boxscore.itertuples():
            if entry.player == "Total":
                continue
            player = PlayerData(name=entry.player, exid=entry.player_exid).save_to_db()

            boxscore_entry, _ = BoxscoreEntry.objects.update_or_create(
                player=player,
                team=team,
                game=game,
                defaults={
                    "is_starter": entry.starter,
                    "minutes": entry.minutes,
                    "points": int(entry.points_made),
                    "assists": int(entry.assists),
                    "steals": int(entry.steals),
                    "turnovers": int(entry.turnovers),
                    "two_point_made": int(entry.two_point_made),
                    "two_point_attempted": int(entry.two_point_attempted),
                    "three_point_made": int(entry.three_point_made),
                    "three_point_attempted": int(entry.three_point_attempted),
                    "field_goal_made": int(entry.field_goal_made),
                    "field_goal_attempted": int(entry.field_goal_attempted),
                    "free_throw_made": int(entry.free_throw_made),
                    "free_throw_attempted": int(entry.free_throw_attempted),
                    "offensive_rebounds": int(entry.offensive_rebounds),
                    "defensive_rebounds": int(entry.defensive_rebounds),
                    "fouls_made": int(entry.fouls_made),
                    "fouls_received": int(entry.fouls_received),
                    "blocks_made": int(entry.blocks_made),
                    "blocks_received": int(entry.blocks_received),
                    "dunks": int(entry.dunks),
                    "ranking": int(entry.ranking),
                    "point_balance": int(entry.point_balance),
                },
            )
            boxscore_entries.append(boxscore_entry)
        return boxscore_entries


class LeagueData(BaseModel):
    """Basketball league."""

    name: str
    season: str
    exid: str
    teams: list[LeagueTeamData]
    games: list["GameData"]

    aggregated_games: pd.DataFrame | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.season}"

    def save_to_db(self) -> League:
        league, _ = League.objects.update_or_create(
            exid=self.exid,
            defaults={
                "name": self.name,
                "season": self.season,
            },
        )
        for team in self.teams:
            team.save_to_db(league)
        for game in self.games:
            game.save_to_db(league)

        return League(
            name=self.name,
            season=self.season,
        )


class GameData(BaseModel):
    """Game from a league."""

    exid: str
    game_at: datetime.datetime
    league: LeagueData
    main_referee: RefereeData
    aux_referee: RefereeData
    home_boxscore: BoxscoreData
    away_boxscore: BoxscoreData

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
    def home_team(self) -> LeagueTeamData:
        return self.home_boxscore.team

    @property
    def away_team(self) -> LeagueTeamData:
        return self.away_boxscore.team

    @property
    def teams(self) -> list[LeagueTeamData]:
        return [self.home_boxscore.team, self.away_boxscore.team]

    def save_to_db(self, league: League) -> Game:
        main_referee = self.main_referee.save_to_db()
        aux_referee = self.aux_referee.save_to_db()
        home_league_team = LeagueTeam.objects.get(team__exid=self.home_team.exid, league=league)

        away_league_team = LeagueTeam.objects.get(team__exid=self.away_team.exid, league=league)

        game, _ = Game.objects.get_or_create(
            exid=self.exid,
            game_at=self.game_at,
            league=league,
            main_referee=main_referee,
            aux_referee=aux_referee,
            home_team=home_league_team,
            away_team=away_league_team,
            home_score=self.home_score,
            away_score=self.away_score,
        )
        self.home_boxscore.save_to_db(game, home_league_team)
        self.away_boxscore.save_to_db(game, away_league_team)
        return game
