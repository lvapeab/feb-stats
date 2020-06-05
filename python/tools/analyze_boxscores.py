import sys
from python.feb_stats.parser import parse_boxscores
from python.feb_stats.transforms import compute_league_aggregates

if __name__ == '__main__':
    league = parse_boxscores(sys.argv[1])
    new_league = compute_league_aggregates(league)
    new_league.export_to_excel()
