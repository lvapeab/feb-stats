from argparse import ArgumentParser

import sys

from python.feb_stats.parser import parse_boxscores
from python.feb_stats.transforms import compute_league_aggregates



def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Boxscore analysis')

    # Model Parameters
    parser.add_argument('--data', action='store', type=str, dest='data')
    parser.add_argument('--output', action='store', type=str, dest='output')

    return parser



if __name__ == '__main__':
    args = get_parser().parse_args()
    league = parse_boxscores(args.data)
    new_league = compute_league_aggregates(league)
    new_league.export_to_excel(args.output)
