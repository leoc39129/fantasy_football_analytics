import json
import sys
from app import create_app, db
from app.models import Player, Team
from flask import current_app

# Initialize the Flask application context
app = create_app()
app.app_context().push()

def import_data_from_json(file_path):
    # Load data from JSON file
    with open(file_path, "r") as f:
        data = json.load(f)

    team_mapping = {}

    # Insert teams
    for team_data in data["teams"]:
        team = Team.query.filter_by(name=team_data["name"]).first()
        if not team:
            team = Team(name=team_data["name"], 
                        division=team_data["division"], 
                        wins=team_data["wins"], 
                        losses=team_data["losses"]
                        )
            db.session.add(team)
            db.session.commit()
            current_app.logger.info(f"Added team: {team_data['name']}")
        else:
            current_app.logger.info(f"Team {team_data['name']} already exists")

        # Store team ID for quick reference
        team_mapping[team_data["name"]] = team.id

    # Insert players
    for player_data in data["players"]:
        team_id = team_mapping.get(player_data["team_name"])
        if team_id:
            player = Player.query.filter_by(name=player_data["name"]).first()
            if not player:
                player = Player(
                    name=player_data["name"],
                    position=player_data["position"],
                    team_id=team.id,
                    fantasy_points=player_data["fantasy_points"]
                )
                db.session.add(player)
                db.session.commit()
                current_app.logger.info(f"Added player: {player_data['name']}")
            else:
                current_app.logger.info(f"Player {player_data['name']} already exists")
        else:
            current_app.logger.warning(f"Team {player_data['team_name']} not found for player {player_data['name']}")

    print("Data import completed successfully.")

# Use the first argument as the JSON file path
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    import_data_from_json(json_file_path)
