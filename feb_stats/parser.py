import pandas as pd
from lxml.html import HtmlElement, Element
import glob
import lxml.html as lh
import os
import requests
from urllib.parse import urlparse
from typing import Dict, Optional, List, Tuple
from hashlib import md5

from feb_stats.game_stats_transforms import parse_game_stats_df
from feb_stats.entities import Game, Boxscore, Team, Player, League, get_team_by_name, get_games_by_team, \
    get_team_boxscores
from feb_stats.transforms import compute_der, aggregate_boxscores, compute_league_aggregates


def parse_str(input_str: str):
    return ' '.join(
        input_str.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace(',', '.').split()).strip()


def get_elements(doc: Element,
                 id: str) -> HtmlElement:
    # Parse data by id
    table_elements = doc.xpath(id)
    return table_elements


def get_game_metadata(doc: Element) -> Dict[str, str]:
    # Parse data by id

    # '//table[@id="jugadoresLocalDataGrid"]//tr'

    fecha = doc.xpath('//span[@id="fechaLabel"]')
    hora = doc.xpath('//span[@id="horaLabel"]')

    liga = doc.xpath('//span[@id="paginaTitulo_ligaLabel"]')
    temporada = doc.xpath('//span[@id="paginaTitulo_temporadaLabel"]')
    equipo_local = doc.xpath('//a[@id="equipoLocalHyperLink"]')
    resultado_local = doc.xpath('//span[@id="resultadoLocalLabel"]')
    equipo_visitante = doc.xpath('//a[@id="equipoVisitanteHyperLink"]')
    resultado_visitante = doc.xpath('//span[@id="resultadoVisitanteLabel"]')

    arbitro_principal = doc.xpath('//span[@id="arbitroPrincipalLabel"]')
    arbitro_auxiliar = doc.xpath('//span[@id="arbitroAuxiliarLabel"]')

    metadata_dict = {
        'fecha': parse_str(fecha[0].text_content()),
        'hora': parse_str(hora[0].text_content()),
        'liga': parse_str(liga[0].text_content()),
        'temporada': parse_str(temporada[0].text_content()),
        'equipo_local': parse_str(equipo_local[0].text_content()),
        'resultado_local': parse_str(resultado_local[0].text_content()),
        'equipo_visitante': parse_str(equipo_visitante[0].text_content()),
        'resultado_visitante': parse_str(resultado_visitante[0].text_content()),
        'arbitro_principal': parse_str(arbitro_principal[0].text_content()),
        'arbitro_auxiliar': parse_str(arbitro_auxiliar[0].text_content()),
    }

    return metadata_dict


def table_to_df(tr_elements: List[Element],
                initial_row: int = 2,
                n_elem: int = 0
                ) -> pd.DataFrame:
    col = []
    i = 0
    # For each row, store each first element (header) and an empty list
    for t in tr_elements[0]:
        i += 1
        name = parse_str(t.text_content())
        col.append((name, []))
    if n_elem == 0:
        n_elem = len(col)
    # Since out first row is the header, data is stored on the second row onwards
    for j in range(initial_row, len(tr_elements)):
        # T is our j'th row
        T = tr_elements[j]
        # If row is not of size 16, the //tr data is not from our table
        if len(T) == n_elem:
            # i is the index of our column
            i = 0
            # Iterate through each element of the row
            for t in T.iterchildren():
                data = parse_str(t.text_content())
                # Append the data to the empty list of the i'th column
                col[i][1].append(data)
                # Increment i for the next column
                i += 1

    data_dict = {title: column for (title, column) in col}
    df = pd.DataFrame(data_dict)
    return df


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


def parse_boxscores(boxscores_dir: str) -> League:
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
            teams=list(all_teams),
            games=all_games
        )
        return league
    else:
        raise ValueError('No games found')
