from dataclasses import dataclass
import os
import pandas as pd
import numpy as np
from typing import TypeVar, Generic, List, Optional

from python.feb_stats.utils import numerical_columns, get_sorted_list_of_columns, timedelta_to_str

T = TypeVar('T')


@dataclass(frozen=True)
class Player(Generic[T]):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None


@dataclass(frozen=True)
class Team(Generic[T]):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Boxscore(Generic[T]):
    boxscore: pd.DataFrame
    id: Optional[int] = None


@dataclass(frozen=True)
class Game(Generic[T]):
    id: int
    date: str
    hour: str
    league: str
    season: str
    local_team: Team
    away_team: Team
    local_score: int
    away_score: int
    main_referee: Player
    aux_referee: Player
    local_boxscore: Boxscore
    away_boxscore: Boxscore


@dataclass(frozen=True)
class League(Generic[T]):
    id: int
    name: str
    season: str
    teams: List[Team]
    games: List[Game]
    aggregated_games: Optional[pd.DataFrame] = None

    def __str__(self):
        return f'{self.name} - {self.season}'

    def export_to_excel(self,
                        dir: Optional[str] = None,
                        filename: Optional[str] = None, ) -> str:
        dir = dir or '.'
        filename = filename or f'{self.name}_{self.season.replace("/", "-")}.xlsx'
        if self.aggregated_games is not None:
            league_to_excel(self,
                            os.path.join(dir, filename),
                            sheet_name=f'{self.name}_{self.season.replace("/", "-")}')
            return os.path.join(dir, filename)
        else:
            raise NotImplementedError('Still unimplemented')


# TODO: These ops should be done in a DB
def get_team_by_name(league: League,
                     team_name: str) -> Team:
    for team in league.teams:
        if team.name == team_name:
            return team
    raise Exception(f'Unable to find the team {team_name} in the league {league}')


def get_games_by_team(league: League,
                      team: Team) -> List[Game]:
    matching_games = []
    for game in league.games:
        if team in {game.local_team, game.away_team}:
            matching_games.append(game)
    return matching_games


def get_team_boxscores(league: League,
                       team: Team) -> List[Boxscore]:
    return [game.local_boxscore if game.local_team == team else game.away_boxscore
            for game in get_games_by_team(league, team)]


def get_rival_boxscores(league: League,
                        team: Team) -> List[Boxscore]:
    return [game.local_boxscore if game.local_team != team else game.away_boxscore
            for game in get_games_by_team(league, team)]


def average_games(df: pd.DataFrame,
                  individual_columns: bool = False) -> pd.DataFrame:
    n_games = df.loc[:, 'partidos'].astype(np.float32)

    a = [(col, col in df) for col in numerical_columns()]
    # a = 'posesiones_totales' in df
    df.loc[:, numerical_columns(individual_columns=individual_columns)] = \
        df.loc[:, numerical_columns(individual_columns=individual_columns)].astype(np.float32).div(n_games, axis='rows')
    if 'minutos' in df:
        df.loc[:, 'minutos'] /= n_games
    df.loc[:, 'modo'] = 'Media'
    return df


def league_to_excel(league,
                    filename: str = 'stats.xlsx',
                    sheet_name='Sheet 1',
                    col_width: int = 20) -> None:
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(filename,
                            engine='xlsxwriter',
                            )

    if league.aggregated_games is not None:
        columns = get_sorted_list_of_columns()
        column_names = list(map(lambda x: ' '.join(x.capitalize().split('_')),
                                columns))

        aggregated_games = league.aggregated_games
        averaged_games = average_games(aggregated_games.copy())

        aggregated_games.loc[:, 'minutos'] = aggregated_games['minutos'].apply(
            lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
        )
        averaged_games.loc[:, 'minutos'] = averaged_games['minutos'].apply(
            lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
        )
        aggregated_games.to_excel(
            writer,
            float_format="%.3f",
            columns=columns,
            header=column_names,
            sheet_name=sheet_name)

        averaged_games.to_excel(
            writer,
            float_format="%.3f",
            columns=columns,
            header=column_names,
            sheet_name=sheet_name + '-medias')

        player_columns = get_sorted_list_of_columns(individual_columns=True)
        player_column_names = list(map(lambda x: ' '.join(x.capitalize().split('_')),
                                       player_columns))
        for team in league.teams:
            if team.season_stats is not None:
                aggregated_team_season_games = team.season_stats
                averaged_team_season_games = average_games(aggregated_team_season_games.copy(),
                                                           individual_columns=True
                                                           )

                aggregated_team_season_games.loc[:, 'minutos'] = aggregated_team_season_games['minutos'].apply(
                    lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
                )
                averaged_team_season_games.loc[:, 'minutos'] = averaged_team_season_games['minutos'].apply(
                    lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
                )
                aggregated_team_season_games.to_excel(
                    writer,
                    float_format="%.3f",
                    columns=player_columns,
                    header=player_column_names,
                    sheet_name=team.name[:31])
                averaged_team_season_games.to_excel(
                    writer,
                    float_format="%.3f",
                    columns=player_columns,
                    header=player_column_names,
                    sheet_name=f'medias - {team.name}'[:31])

        for n_sheet, (worksheet_name, worksheet) in enumerate(writer.sheets.items()):
            #     worksheet.conditional_format('C2:C8', {type': '3_color_scale'})
            if n_sheet < 2:
                worksheet.set_column(1, 1, 2 * col_width)
            else:
                worksheet.set_column(0, 0, 3 * col_width)

            worksheet.set_column(2, len(columns), col_width)
        writer.save()
    print(f"Data saved in {filename}")