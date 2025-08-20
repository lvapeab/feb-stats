from src.core.scrapers.boxscore_scraper import BoxscoreScraper


def read_boxscores_from_calendar_url(
    calendar_url: str,
    season: str | None = None,
    group_id: str | None = None,
) -> list[bytes]:
    """Scrapes boxscores as HTML files going through a calendar URL.
    :param calendar_url: The calendar URL.
    :return: a list of HTML files containing boxscores.
    """
    scraper = BoxscoreScraper()
    return scraper.fetch_boxscores(calendar_url, season, group_id)
