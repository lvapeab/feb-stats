from argparse import ArgumentParser
from python.feb_stats.utils import response_to_excel
def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Boxscore analysis')
    parser.add_argument('--response', action='store', type=str, dest='response')
    parser.add_argument('--output', action='store', type=str, dest='output')
    return parser



if __name__ == '__main__':
    args = get_parser().parse_args()
    response_to_excel(args.response,
                      args.output)

