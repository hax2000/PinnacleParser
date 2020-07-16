from sqlalchemy import Column, Integer, VARCHAR, REAL, ForeignKey
from database import Base,db_Session


class Line(Base):
    __tablename__ = 'lines'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    label = Column(VARCHAR(50), nullable=False)
    value = Column(REAL, nullable=False)
    
    def __repr__(self):
        return "Значение линии \"{}\", для некоторого показателя, равно {}".format(self.label,str(self.value))


class Counter(Base):
    __tablename__ = 'counters'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=False)
    
    def __repr__(self):
        return "Показатель \"{}\", id в базе: {}".format(self.name,str(self.id))



class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(40), nullable=False)
    
    def __repr__(self):
        return "Команда \"{}\", id в базе: {}".format(self.name,str(self.id))



class Tournament(Base):
    __tablename__ = 'tournaments'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    fullTitle = Column(VARCHAR(50), nullable=False)
    
    def __repr__(self):
        return "Турнир \"{}\", id в базе: {}".format(self.fullTitle,str(self.id))



class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    firstOpponent_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    secondOpponent_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    def __repr__(self):
        firstOpponent_name = db_Session.query(Team).filter_by(id=self.firstOpponent_id).first().name
        secondOpponent_name = db_Session.query(Team).filter_by(id=self.secondOpponent_id).first().name
        tournament_name = db_Session.query(Tournament).filter_by(id=self.tournament_id).first().fullTitle
        return "Матч \"{} - {}\", Турнир: {}, id в базе: {}".format(firstOpponent_name,
            secondOpponent_name,tournament_name,str(self.id))



class Statistics(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    counter_id = Column(Integer, ForeignKey('counters.id'), nullable=False)
    line_id = Column(Integer, ForeignKey('lines.id'),nullable=False)
    
    def __repr__(self):
        counter_name = db_Session.query(Counter).filter_by(id=self.counter_id).first().name
        team_name = db_Session.query(Team).filter_by(id=self.team_id).first().name

        match_info = db_Session.query(Match).filter_by(id=self.match_id).first()
        opponent_id = match_info.firstOpponent_id if match_info.firstOpponent_id!=self.team_id else match_info.secondOpponent_id
        opponent_name = db_Session.query(Team).filter_by(id=opponent_id).first().name
        tournament_name = db_Session.query(Tournament).filter_by(id=match_info.tournament_id).first().fullTitle
        
        line_info = db_Session.query(Line).filter_by(id=self.line_id).first()
        line_data = "{} - {}".format(line_info.label,str(line_info.value))

        return "В Матче \"{} - {}\", турнира \"{}\", команда \"{}\" имеет следующую линию для показателя \"{}\": \n{}".format(
            team_name,opponent_name,tournament_name,team_name,counter_name,line_data)
