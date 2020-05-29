import glob
import lxml.html as lh
import os
import pandas as pd
import requests
from urllib.parse import urlparse
from typing import Dict, Optional, List

from feb_stats.parser import get_elements, game_stats_elements_to_df, get_game_metadata
from feb_stats.game_stats_transforms import parse_game_stats_df
from feb_stats.utils import dataframe_to_excel

def parse_game_stats(link: str,
                     ids: List[Optional[str]]=None) -> Dict[str, pd.DataFrame]:
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
    game_stats['metadata'] = get_game_metadata(doc)
    for (id, local) in ids:
        elements = get_elements(doc,
                                id)
        key = 'local_boxscore' if local else 'visitante_boxscore'
        if elements:
            ori_df = game_stats_elements_to_df(elements,
                                              initial_row=2,
                                              n_elem=18)
            df = parse_game_stats_df(ori_df,
                                     local_team=local)
            game_stats[key] = df
    return game_stats

def aggregate_boxscores(boxscores_dir):
    for link in glob.iglob(os.path.join(boxscores_dir, '*.html'), recursive=False):
        parsed_dfs = parse_game_stats(link)
    print(parsed_dfs)

if __name__ == '__main__':
    # link = 'http://competiciones.feb.es/estadisticas/Estadisticas.aspx?g=39&t=0'
    link = '/home/lvapeab/projects/feb-stats/test_artifacts/game_sheet.html'
    aggregate_boxscores('/home/lvapeab/projects/feb-stats/test_artifacts/')
    # parsed_df = parse_game_stats(link)
    # dataframe_to_excel(parsed_df,
    #                    './df.xlsx',
    #                    sheet_name='Game Sheet')
