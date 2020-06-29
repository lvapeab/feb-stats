from lxml.html import Element
from typing import Dict, Optional, List, Tuple
from hashlib import md5

from python.feb_stats.parsers.generic_parser import GenericParser
from python.feb_stats.parsers.feb_stats_transforms import transform_game_stats_df
from python.feb_stats.entities import Game, Boxscore, Team, Player


class FEBParser(GenericParser):

    def parse_game_metadata(self,
                            doc: Element) -> Dict[str, str]:
        # Parse data by id
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
            'fecha': self.parse_str(fecha[0].text_content()),
            'hora': self.parse_str(hora[0].text_content()),
            'liga': self.parse_str(liga[0].text_content()),
            'temporada': self.parse_str(temporada[0].text_content()),
            'equipo_local': self.parse_str(equipo_local[0].text_content()),
            'resultado_local': self.parse_str(resultado_local[0].text_content()),
            'equipo_visitante': self.parse_str(equipo_visitante[0].text_content()),
            'resultado_visitante': self.parse_str(resultado_visitante[0].text_content()),
            'arbitro_principal': self.parse_str(arbitro_principal[0].text_content()),
            'arbitro_auxiliar': self.parse_str(arbitro_auxiliar[0].text_content()),
        }

        return metadata_dict

    def parse_game_stats(self,
                         doc: Element,
                         ids: List[Optional[str]] = None) -> Tuple[Game, Tuple[Team, Team]]:
        ids = ids or [
            ('//table[@id="jugadoresLocalDataGrid"]//tr', True),
            ('//table[@id="jugadoresVisitanteDataGrid"]//tr', False)
        ]
        game_stats = {}
        metadata = self.parse_game_metadata(doc)

        for (doc_id, local) in ids:
            elements = self.get_elements(doc,
                                         doc_id)
            key = 'local_boxscore' if local else 'visitante_boxscore'
            if elements:
                ori_df = self.elements_to_df(elements,
                                             initial_row=2,
                                             n_elem=18)
                df = transform_game_stats_df(ori_df,
                                             local_team=local)
                game_stats[key] = df
            else:
                raise ValueError(f'Unable to parse stats from {doc_id}')
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
