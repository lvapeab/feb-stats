import pandas as pd
from typing import List


def parse_str(input_str: str):
    return ' '.join(input_str.replace('\n', '').replace('\t', '').replace('\r', '').replace(',', '.').split())


def get_elements(doc: str,
                 id: str):
    # Parse data by id
    table_elements = doc.xpath(id)
    return table_elements


def cum_stats_elements_to_df(tr_elements: List[str],
                             initial_row:int=2,
                             n_elem: int=0
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
                # Check if row is empty
                if i > 0:
                    # Convert any numerical value to integers
                    try:
                        data = float(data)
                    except:
                        pass
                # Append the data to the empty list of the i'th column
                col[i][1].append(data)
                # Increment i for the next column
                i += 1

    data_dict = {title: column for (title, column) in col}
    df = pd.DataFrame(data_dict)
    return df



def game_stats_elements_to_df(tr_elements: List[str],
                             initial_row:int=2,
                             n_elem: int=0
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
                # Check if row is empty
                if i > 0:
                    # Convert any numerical value to integers
                    try:
                        data = float(data)
                    except:
                        pass
                # Append the data to the empty list of the i'th column
                col[i][1].append(data)
                # Increment i for the next column
                i += 1

    data_dict = {title: column for (title, column) in col}
    df = pd.DataFrame(data_dict)
    return df




