from app import create_app
from app.models import db, PlayerGame, PlayerTeam, Game, Team, Player

app = create_app()

def get_team_id_by_abbreviation(abbreviation):
    """Fetch the team ID using the team's abbreviation."""
    team = Team.query.filter_by(name=abbreviation).first()
    if not team:
        print(f"Team with abbreviation '{abbreviation}' not found.")
        return None
    return team.id

def create_missing_player_team_entries():
    """Iterate through PlayerGame objects and ensure corresponding PlayerTeam entries exist."""
    with app.app_context():
        player_games = PlayerGame.query.all()
        missing_count = 0

        for player_game in player_games:
            player = Player.query.get(player_game.player_id)
            game = Game.query.get(player_game.game_id)
            game_date = game.date

            home_team = Team.query.get(game.home_team_id)
            away_team = Team.query.get(game.away_team_id)

            home_team_entry = (
                PlayerTeam.query.filter_by(player_id=player.id, team_id=home_team.id)
                .filter(PlayerTeam.start_date <= game_date)
                .filter((PlayerTeam.end_date.is_(None)) | (PlayerTeam.end_date >= game_date))
                .first()
            )
            away_team_entry = (
                PlayerTeam.query.filter_by(player_id=player.id, team_id=away_team.id)
                .filter(PlayerTeam.start_date <= game_date)
                .filter((PlayerTeam.end_date.is_(None)) | (PlayerTeam.end_date >= game_date))
                .first()
            )

            if not home_team_entry and not away_team_entry:
                # PlayerTeam entry is missing for both home and away teams
                print()
                print(
                    f"Missing PlayerTeam entry for Player {player.name} (ID: {player.id}) in Game {player_game.game_id} "
                    f"on {game_date} between {home_team.name} (Home) and {away_team.name} (Away)."
                )
                team_abbreviation = input(f"Enter the team abbreviation for Player {player.name} (e.g., 'GB', 'LAR'): ").strip()
                team_id = get_team_id_by_abbreviation(team_abbreviation)

                if team_id:
                    # Create a new PlayerTeam entry
                    new_player_team = PlayerTeam(
                        player_id=player.id,
                        team_id=team_id,
                        start_date=game_date,  # Use the game date as a starting point
                        end_date=None  # Leave end_date open-ended for now
                    )
                    db.session.add(new_player_team)
                    missing_count += 1
                    print(f"Added PlayerTeam for Player {player.name}, Team {team_abbreviation}, Start Date {game_date}")
                else:
                    print(f"Skipping Player {player.name} for Game {player_game.game_id} due to missing team information.")

        # Commit all changes to the database
        db.session.commit()
        print(f"Completed! Added {missing_count} missing PlayerTeam entries.")

if __name__ == "__main__":
    create_missing_player_team_entries()
