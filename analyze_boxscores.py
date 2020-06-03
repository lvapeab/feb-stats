from feb_stats.parser import parse_boxscores
from feb_stats.transforms import compute_league_aggregates

if __name__ == '__main__':
    league = parse_boxscores('/home/lvapeab/projects/feb-stats/test_artifacts/')
    new_league = compute_league_aggregates(league)
    new_league.export_to_excel()
