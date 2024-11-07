# ffa_flask_app/app/routes/teams.py

from flask import Blueprint, jsonify, current_app
from app.models import Team

# Create a Blueprint for team routes
teams_bp = Blueprint('teams', __name__)

# Define team-related routes
@teams_bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    team_data = [
        {
            "name": team.name,
            "division": team.division,
            "wins": team.wins,
            "losses": team.losses
        }
        for team in teams
    ]
    return jsonify(team_data)

@teams_bp.route('/teams/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    current_app.logger.debug(f"Received request to fetch team with ID: {team_id}")
    try:
        team = Team.query.get(team_id)
        if team:
            team_data = {
                "id": team.id,
                "name": team.name,
                "city": team.city
            }
            current_app.logger.info(f"Team with ID {team_id} retrieved successfully.")
            return jsonify(team_data), 200
        else:
            current_app.logger.warning(f"No team found with ID: {team_id}")
            return jsonify({"error": "Team not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching team with ID {team_id}: {e}")
        return jsonify({"error": "An error occurred while fetching team data"}), 500
