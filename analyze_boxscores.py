import glob
import lxml.html as lh
import os
import requests
from urllib.parse import urlparse
from typing import Dict, Optional, List, Tuple
from hashlib import md5

from feb_stats.parser import get_elements, table_to_df, get_game_metadata
from feb_stats.game_stats_transforms import parse_game_stats_df
from feb_stats.entities import Game, Boxscore, Team, Player, League, get_team_by_name, get_games_by_team
from feb_stats.transforms import compute_der, aggregate_boxscores

from feb_stats.utils import dataframe_to_excel


def parse_games_stats(link: str,
                      ids: List[Optional[str]] = None) -> Tuple[Game, Tuple[Team, Team]]:
    ids = ids or [
        ('//table[@id="jugadoresLocalDataGrid"]//tr', True),
        ('//table[@id="jugadoresVisitanteDataGrid"]//tr', False)
    ]

    result = urlparse(link)
    if all([result.scheme, result.netloc, result.path]):
        page = requests.get(link)
        # Store the contents of the website under doc
        doc = lh.fromstring(page.content)
    elif os.path.isfile(link):
        with open(link,
                  mode="r",
                  encoding='latin1') as f:
            page_str = f.read()
        doc = lh.fromstring(page_str)
    else:
        raise ValueError(f'Unable to find the resource {link} (not a valid URL nor an existing file.)')

    game_stats = {}
    metadata = get_game_metadata(doc)

    for (id, local) in ids:
        elements = get_elements(doc,
                                id)
        key = 'local_boxscore' if local else 'visitante_boxscore'
        if elements:
            ori_df = table_to_df(elements,
                                 initial_row=2,
                                 n_elem=18)
            df = parse_game_stats_df(ori_df,
                                     local_team=local)
            game_stats[key] = df
        else:
            raise ValueError(f'Unable to parse stats from {id}')
    local_team = Team(
        id=int(md5(str.encode(metadata['equipo_local'], encoding='UTF-8')).hexdigest(), 16),
        name=metadata['equipo_local']
    )
    away_team = Team(
        id=int(md5(str.encode(metadata['equipo_visitante'], encoding='UTF-8')).hexdigest(), 16),
        name=metadata['equipo_visitante']
    )
    game = Game(
        id=int(md5(str.encode(
            f"{metadata['liga']}_{metadata['fecha']}_{metadata['equipo_local']}_{metadata['equipo_visitante']}",
            encoding='UTF-8')).hexdigest(), 16),
        date=metadata['fecha'],
        hour=metadata['hora'],
        league=metadata['liga'],
        season=metadata['temporada'],
        local_team=local_team,
        local_score=int(metadata['resultado_local']),
        away_team=away_team,
        away_score=int(metadata['resultado_visitante']),
        main_referee=Player(
            id=int(md5(str.encode(metadata['arbitro_principal'], encoding='UTF-8')).hexdigest(), 16),
            name=metadata['arbitro_principal']
        ),
        aux_referee=Player(
            id=int(md5(str.encode(metadata['arbitro_auxiliar'], encoding='UTF-8')).hexdigest(), 16),
            name=metadata['arbitro_auxiliar']
        ),
        local_boxscore=Boxscore(
            id=int(md5(str.encode(f"{metadata['liga']}_{metadata['fecha']}_{metadata['equipo_local']}",
                                  encoding='UTF-8')).hexdigest(), 16),

            boxscore=game_stats['local_boxscore']
        ),
        away_boxscore=Boxscore(
            id=int(md5(str.encode(f"{metadata['liga']}_{metadata['fecha']}_{metadata['equipo_visitante']}",
                                  encoding='UTF-8')).hexdigest(), 16),

            boxscore=game_stats['visitante_boxscore']
        )
    )
    return game, (local_team, away_team)


def analyze_boxscores(boxscores_dir: str) -> League:
    all_games = []
    all_teams = set()
    for link in glob.iglob(os.path.join(boxscores_dir, '*.html'), recursive=False):
        game, teams = parse_games_stats(link)
        all_games.append(game)
        for team in teams:
            all_teams.add(team)

    if all_games:
        league = League(
            id=int(md5(str.encode(f"{all_games[0].league}", encoding='UTF-8')).hexdigest(), 16),
            name=all_games[0].league,
            season=all_games[0].season,
            teams=set(all_teams),
            games=all_games
        )
        return league
    else:
        raise ValueError('No games found')


if __name__ == '__main__':
    # link = 'http://competiciones.feb.es/estadisticas/Estadisticas.aspx?g=39&t=0'
    link = '/home/lvapeab/projects/feb-stats/test_artifacts/game_sheet.html'
    league = analyze_boxscores('/home/lvapeab/projects/feb-stats/test_artifacts/')

    team = get_team_by_name(league,
                            'GUILLÉN GROUP ALGINET')

    # rival_boxscores = [game.away_boxscore if game.local_team == team else game.local_boxscore for game in get_games_by_team(league, team)]
    own_boxscores = [game.local_boxscore if game.local_team == team else game.away_boxscore for game in get_games_by_team(league, team)]
    aggregate_boxscores(own_boxscores)

    # ders = compute_der(league,
    #                    team)
    # print(ders)
    # parsed_df = parse_games_stats(link)
    # dataframe_to_excel(parsed_df,
    #                    './df.xlsx',
    #                    sheet_name='Game Sheet')
