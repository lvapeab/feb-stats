from django.core.validators import MinValueValidator
from django.db import models

from feb_stats.constants import LARGE_CHAR_FIELD_SIZE
from feb_stats.models_generic import DateModel, ExidModel


class Player(DateModel, ExidModel):
    first_name = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)
    last_name = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Referee(DateModel, ExidModel):
    first_name = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)
    last_name = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Team(DateModel, ExidModel):
    name = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)

    def __str__(self) -> str:
        return self.name


class League(DateModel, ExidModel):
    name = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)
    season = models.CharField(max_length=LARGE_CHAR_FIELD_SIZE)

    def __str__(self) -> str:
        return f"{self.name} - {self.season}"

    class Meta:
        unique_together = ["name", "season"]


class LeagueTeam(DateModel):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(class)ss",
        related_query_name="%(class)ss",
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(class)ss",
        related_query_name="%(class)ss",
    )

    def __str__(self) -> str:
        return f"{self.team.name} - {self.league.name} - {self.league.season}"


class Game(DateModel, ExidModel):
    game_at = models.DateTimeField()
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(class)ss",
        related_query_name="%(class)ss",
    )
    main_referee = models.ForeignKey(
        Referee,
        on_delete=models.PROTECT,
        null=False,
        related_name="main_games",
        related_query_name="main_games",
    )
    aux_referee = models.ForeignKey(
        Referee,
        on_delete=models.PROTECT,
        null=False,
        related_name="aux_games",
        related_query_name="aux_games",
    )

    home_team = models.ForeignKey(
        LeagueTeam,
        on_delete=models.PROTECT,
        null=False,
        related_name="home_games",
        related_query_name="home_games",
    )
    away_team = models.ForeignKey(
        LeagueTeam,
        on_delete=models.PROTECT,
        null=False,
        related_name="away_games",
        related_query_name="away_games",
    )

    home_score = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    away_score = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    @property
    def date(self) -> str:
        return self.game_at.strftime("%d/%m/%Y")

    @property
    def time(self) -> str:
        return self.game_at.strftime("%H:%M")


class BoxscoreEntry(DateModel):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        null=False,
    )
    team = models.ForeignKey(
        LeagueTeam,
        on_delete=models.PROTECT,
        null=False,
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        null=False,
    )

    is_starter = models.BooleanField()
    minutes = models.DurationField()
    points = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    assists = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    steals = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    turnovers = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    two_point_made = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    two_point_attempted = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    three_point_made = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    three_point_attempted = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    field_goal_made = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    field_goal_attempted = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    free_throw_made = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    free_throw_attempted = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    offensive_rebounds = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    defensive_rebounds = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    fouls_made = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    fouls_received = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    blocks_made = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    blocks_received = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    dunks = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    ranking = models.IntegerField()
    point_balance = models.IntegerField()

    class Meta:
        unique_together = ["game", "team", "player"]

    @property
    def two_point_percentage(self) -> float | None:
        if not self.two_point_attempted:
            return None
        return self.two_point_made / self.two_point_attempted

    @property
    def three_point_percentage(self) -> float | None:
        if not self.three_point_attempted:
            return None
        return self.three_point_made / self.three_point_attempted

    @property
    def free_throw_percentage(self) -> float | None:
        if not self.free_throw_attempted:
            return None
        return self.free_throw_made / self.free_throw_attempted

    @property
    def total_rebounts(self) -> int:
        return self.offensive_rebounds + self.defensive_rebounds
