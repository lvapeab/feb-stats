import lxml.html as lh
import os
import pandas as pd
import requests
from urllib.parse import urlparse
from typing import Optional

from feb_stats.parser import get_elements, elements_to_df
from feb_stats.transforms import parse_df

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
    ori_df = elements_to_df(elements)
    df = parse_df(ori_df)
    return df
