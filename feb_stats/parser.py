import pandas as pd
from lxml.html import HtmlElement, Element
from typing import Dict, List


def parse_str(input_str: str):
    return ' '.join(input_str.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace(',', '.').split()).strip()


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
