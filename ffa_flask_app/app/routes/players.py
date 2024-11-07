# ffa_flask_app/app/routes/players.py

from flask import Blueprint, jsonify, current_app
from app.models import Player

# Create a Blueprint for player routes
players_bp = Blueprint('players', __name__)

# Route to get all players
@players_bp.route('/', methods=['GET'])
def get_all_players():
    players = Player.query.all()
    players_data = [
        {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "team": player.team.name,  # Display the team name
            "fantasy_points": player.fantasy_points
        }
        for player in players
    ]
    return jsonify(players_data)

# Route to get a specific player by ID
@players_bp.route('/<int:player_id>', methods=['GET'])
def get_player_by_id(player_id):
    current_app.logger.debug(f"Received request to fetch player with ID: {player_id}")
    try:
        player = Player.query.get(player_id)
        if player:
            player_data = {
                "id": player.id,
                "name": player.name,
                "position": player.position,
                "team": player.team.name,  # Display the team name
                "fantasy_points": player.fantasy_points
            }
            current_app.logger.info(f"Player with ID {player_id} retrieved successfully.")
            return jsonify(player_data), 200
        else:
            current_app.logger.warning(f"No player found with ID: {player_id}")
            return jsonify({"error": "Player not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching player with ID {player_id}: {e}")
        return jsonify({"error": "An error occurred while fetching player data"}), 500
