# models.py
from app import db
from flask import current_app

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    team = db.Column(db.String(3), nullable=False)

    # Foreign key and relationships
    player_games = db.relationship('PlayerGame', back_populates='player')

    def __repr__(self):
        return f'<Player {self.name} - {self.position}>'
    
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
    
    
class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    division = db.Column(db.String(20), nullable=False)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

    # Define a relationship to reference players in a team
    # players = db.relationship("Player", back_populates="team", lazy="dynamic")

    def __repr__(self):
        return f'<Team {self.name} - {self.division}>'

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

    
class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    spread = db.Column(db.Float, nullable=True)
    over_under = db.Column(db.Float, nullable=True)

    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    # player_games = db.relationship('PlayerGame', back_populates='game')

    def __repr__(self):
        return f'<Game ID: {self.id}, Home Team: {self.home_team}, Away Team: {self.away_team}>'
    
def add_game(home_team_id, away_team_id, spread=None, over_under=None):
    """Adds a new game to the database."""
    try:
        new_game = Game(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            spread=spread,
            over_under=over_under
        )
        db.session.add(new_game)
        db.session.commit()
        print(f"Game added: Home Team ID {home_team_id}, Away Team ID {away_team_id}")
        return new_game.id  # Return the game ID for reference if needed
    except Exception as e:
        db.session.rollback()
        print(f"Error adding game: {e}")
        return None


class PlayerGame(db.Model):
    __tablename__ = 'player_games'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    game_id = db.Column(db.Integer, nullable=True)
    rush_attempts = db.Column(db.Integer, default=0)
    rush_yards = db.Column(db.Float, default=0)
    rush_tds = db.Column(db.Integer, default=0)
    targets = db.Column(db.Integer, default=0)
    receptions = db.Column(db.Integer, default=0)
    rec_yards = db.Column(db.Float, default=0)
    rec_tds = db.Column(db.Integer, default=0)

    # Relationships
    player = db.relationship('Player', back_populates='player_games')
    # game = db.relationship('Game', back_populates='player_games')

    def __repr__(self):
        return f'<PlayerGame Player ID: {self.player_id}, Game ID: {self.game_id}, Stats: Pass Yds: {self.pass_yards}, Rush Yds: {self.rush_yards}, Rec Yds: {self.rec_yards}>'

def add_player_game(player_id, game_id, rush_attempts=0, rush_yards=0.0, rush_tds=0, 
                    targets=0, receptions=0, rec_yards=0.0, rec_tds=0):
    """Adds a player's performance in a specific game to the database."""
    try:
        new_player_game = PlayerGame(
            player_id=player_id,
            game_id=game_id,
            rush_attempts=rush_attempts,
            rush_yards=rush_yards,
            rush_tds=rush_tds,
            targets=targets,
            receptions=receptions,
            rec_yards=rec_yards,
            rec_tds=rec_tds
        )
        db.session.add(new_player_game)
        db.session.commit()
        print(f"Player Game added: Player ID {player_id}, Game ID {game_id}")
        return new_player_game.id  # Return the player game ID for reference if needed
    except Exception as e:
        db.session.rollback()
        print(f"Error adding player game: {e}")
        return None