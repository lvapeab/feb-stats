import lxml.html as lh
import os
import pandas as pd
import requests
from urllib.parse import urlparse
from typing import Optional

from feb_stats.parser import get_elements, table_to_df
from feb_stats.cum_stats_transforms import parse_cum_stats_df
from feb_stats.utils import league_to_excel

def parse_cum_stats(link: str,
                    id: Optional[str] = '//table[@id="estadisticasTotalesDataGrid"]//tr') -> pd.DataFrame:
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

    elements = get_elements(doc,
                            id)
    ori_df = table_to_df(elements,
                         initial_row=2,
                         n_elem=16)
    df = parse_cum_stats_df(ori_df)
    return df


if __name__ == '__main__':
    # link = 'http://competiciones.feb.es/estadisticas/Estadisticas.aspx?g=39&t=0'
    link = '/home/lvapeab/projects/feb-stats/data/1.html'
    parsed_df = parse_cum_stats(link)
    league_to_excel(parsed_df,
                       './df.xlsx',
                    sheet_name='Game Sheet')
