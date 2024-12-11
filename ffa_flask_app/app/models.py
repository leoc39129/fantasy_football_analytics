from app import db
from flask import current_app

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(20), nullable=False)

    # Relationships
    player_teams = db.relationship("PlayerTeam", back_populates="player")
    player_games = db.relationship('PlayerGame', back_populates='player')

    def __repr__(self):
        return f'<Player {self.name} - {self.position}>'
    
def add_player(name, position, team_id, start_date=None, id=None):
    try:
        if not team_id:
            raise ValueError("team_id cannot be None")
        
        # Check if the player already exists
        existing_player = Player.query.filter_by(name=name, position=position).first()
        if existing_player:
            current_app.logger.info(f"Player already exists: {name}")
            return existing_player
        
        new_player = Player(
            id=id, 
            name=name, 
            position=position
        )

        db.session.add(new_player)
        db.session.commit()

        # Add a PlayerTeam entry for the player's current team if it doesn't exist already
        add_player_team(new_player.id, team_id, start_date)

        current_app.logger.info(f"Successfully added player: {name}")
        return new_player
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to add player {name}: {e}")
        raise


class PlayerTeam(db.Model):
    __tablename__ = 'player_teams'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)  # Null means the player is currently on this team

    # Relationships
    player = db.relationship("Player", back_populates="player_teams")
    team = db.relationship("Team")


def add_player_team(player_id, team_id, start_date, end_date=None):
    ''' Add a PlayerTeam entry for the player's current team if it doesn't exist already '''
    try:
        # Check if a PlayerTeam entry already exists with the same player_id, team_id, and start_date
        existing_entry = PlayerTeam.query.filter_by(
            player_id=player_id,
            team_id=team_id,
        ).first()

        if existing_entry:
            current_app.logger.info(f"PlayerTeam entry already exists: Player ID {player_id}, Team ID {team_id}, Start Date {start_date}")
            return existing_entry

        if not start_date:
            current_app.logger.info("PlayerTeam call needs a start date")
            return None

        # If no existing entry, create a new PlayerTeam entry
        new_player_team = PlayerTeam(
            player_id=player_id,
            team_id=team_id,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_player_team)
        db.session.commit()
        current_app.logger.info(f"Successfully added PlayerTeam entry: Player ID {player_id}, Team ID {team_id}")
        return new_player_team

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to add PlayerTeam for Player ID {player_id}: {e}")
        raise

    
    
class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(3), nullable=False)
    division = db.Column(db.String(10), nullable=False)

    # Relationships
    player_teams = db.relationship("PlayerTeam", back_populates="team", lazy="dynamic")

    def __repr__(self):
        return f'<Team {self.name} - {self.division}>'

def add_team(name, division, id=None):
    try:
        new_team = Team(id=id, name=name, division=division)
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

    home_team_score = db.Column(db.Integer, nullable=True)
    away_team_score = db.Column(db.Integer, nullable=True)

    date = db.Column(db.Date, nullable=True)  # Add date field
    game_time = db.Column(db.Time, nullable=True)  # Add time field

    stats_processed = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    player_games = db.relationship('PlayerGame', back_populates='game')

    def __repr__(self):
        return f'<Game ID: {self.id}, Home Team: {self.home_team}, Away Team: {self.away_team}>'
    
def add_game(home_team_id, away_team_id, spread=None, over_under=None, home_team_score=None, away_team_score=None, date=None, game_time=None, id=None):
    """Adds a new game to the database, ensuring no duplicate games are added."""
    try:
        if not home_team_id or not away_team_id:
            raise ValueError("Both home_team_id and away_team_id must be provided.")

        # Check if a game with the same non-nullable information already exists
        existing_game = Game.query.filter_by(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            date=date
        ).first()

        if existing_game:
            current_app.logger.info(f"Game already exists: Home Team ID {home_team_id}, Away Team ID {away_team_id}, Date {date}")
            return None

        # Create a new game
        new_game = Game(
            id=id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            spread=spread,
            over_under=over_under,
            home_team_score=home_team_score,
            away_team_score=away_team_score,
            date=date,
            game_time=game_time
        )
        db.session.add(new_game)
        db.session.commit()
        current_app.logger.info(f"Game added: Home Team ID {home_team_id}, Away Team ID {away_team_id}, Date {date}")
        return new_game.id  # Return the game ID for reference if needed
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding game: {e}")
        return None



class PlayerGame(db.Model):
    __tablename__ = 'player_games'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)

    pass_attempts = db.Column(db.Integer, default=0)
    pass_completions = db.Column(db.Integer, default=0)
    pass_yards = db.Column(db.Integer, default=0)
    pass_tds = db.Column(db.Integer, default=0)
    pass_int = db.Column(db.Integer, default=0)
    rush_attempts = db.Column(db.Integer, default=0)
    rush_yards = db.Column(db.Integer, default=0)
    rush_tds = db.Column(db.Integer, default=0)
    longest_rush = db.Column(db.Integer, default=0)
    targets = db.Column(db.Integer, default=0)
    receptions = db.Column(db.Integer, default=0)
    rec_yards = db.Column(db.Integer, default=0)
    rec_tds = db.Column(db.Integer, default=0)
    longest_rec = db.Column(db.Integer, default=0)

    # Relationships
    player = db.relationship('Player', back_populates='player_games')
    game = db.relationship('Game', back_populates='player_games')

    def __repr__(self):
        return f'<PlayerGame Player ID: {self.player_id}, Game ID: {self.game_id}>'

def add_player_game(player_id, game_id, pass_attempts=0, pass_completions=0, pass_yards=0, pass_tds=0, pass_int=0,
                    rush_attempts=0, rush_yards=0, rush_tds=0, longest_rush=0,
                    targets=0, receptions=0, rec_yards=0.0, rec_tds=0, longest_rec=0):
    """Adds a player's performance in a specific game to the database."""
    existing_player_game = PlayerGame.query.filter_by(player_id=player_id, game_id=game_id).first()
    if not existing_player_game:

        player = Player.query.get(player_id)
        if not player:
            raise ValueError(f"Player with ID {player_id} does not exist.")
        
        game = Game.query.get(game_id)
        if not game:
            raise ValueError(f"Game with ID {game_id} does not exist.")
        
        try:
            new_player_game = PlayerGame(
                player_id=player.id,
                game_id=game.id,
                pass_attempts=pass_attempts,
                pass_completions=pass_completions,
                pass_yards=pass_yards,
                pass_tds=pass_tds,
                pass_int=pass_int,
                rush_attempts=rush_attempts,
                rush_yards=rush_yards,
                rush_tds=rush_tds,
                longest_rush=longest_rush,
                targets=targets,
                receptions=receptions,
                rec_yards=rec_yards,
                rec_tds=rec_tds,
                longest_rec=longest_rec
            )
            db.session.add(new_player_game)
            db.session.commit()
            current_app.logger.info(f"Player Game added: Player ID {player_id}, Game ID {game_id}")
            return new_player_game.id  # Return the player game ID for reference if needed
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding player game: {e}")
            return None
