from sqlalchemy import Column, ForeignKey, Integer, String, Date, Time

from python.web.webapp import db

db.metadata.clear()


class Player(db.Model):
    """Player from a team."""

    __tablename__ = "player"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(250), primary_key=False)

    def __init__(self, name):
        self.name = name


class Team(db.Model):
    """Team from a league."""

    __tablename__ = "team"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(250), primary_key=False)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def init_db():
    db.create_all()


if __name__ == "__main__":
    init_db()

#
# @dataclass(frozen=True)
# class Boxscore(Generic[T]):
#     """Boxscore from a game."""
#
#     boxscore: pd.DataFrame
#     id: Optional[int] = None

'''
class Game(declarative_base()):
    """Game from a league."""

    __tablename__ = "game"

    id = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=False)
    hour = Column(Time, primary_key=False)
    # league = relationship(League)
    season = Column(String(250), primary_key=False)
    home_team: relationship(Team)
    away_team: relationship(Team)
    home_score: Column(Integer, primary_key=False)
    away_score: Column(Integer, primary_key=False)
    main_referee: relationship(Player)
    aux_referee = relationship(Player)
    # local_boxscore: Boxscore
    # away_boxscore: Boxscore


class League(declarative_base()):
    """Basketball league."""

    __tablename__ = "league"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), primary_key=False)
    season = Column(String(250), primary_key=False)
    teams = relationship(Team)
    games = relationship(Game)

    def __str__(self):
        return f"{self.name} - {self.season}"
'''
