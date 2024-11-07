# models.py
from app import db
from flask import current_app

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    fantasy_points = db.Column(db.Float)

    # Foreign key and relationship to Team
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team = db.relationship("Team", back_populates="players")

    def __repr__(self):
        return f'<Player {self.name} - {self.position}>'
    
    
class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    division = db.Column(db.String(20), nullable=False)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

    # Optional: Define a relationship to reference players in a team
    players = db.relationship("Player", back_populates="team", cascade="all, delete")

    def __repr__(self):
        return f'<Team {self.name} - {self.division}>'
    
    
def add_player(name, position, team_id, fantasy_points):
    try:
        new_player = Player(name=name, position=position, team_id=team_id, fantasy_points=fantasy_points)
        db.session.add(new_player)
        db.session.commit()
        current_app.logger.info(f"Successfully added player: {name}")
        return new_player
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to add player {name}: {e}")
        raise

def add_team(name, city):
    try:
        new_team = Team(name=name, city=city)
        db.session.add(new_team)
        db.session.commit()
        current_app.logger.info(f"Successfully added team: {name}")
        return new_team
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to add team {name}: {e}")
        raise

