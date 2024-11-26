import requests
import argparse
from app.models import add_player_game, db, Player
from app import create_app

app = create_app()
app.app_context().push()

def add_player_if_not_exists(player_id, player_name, position, team):
    """
    Check if a player exists in the database. If not, add them.
    
    Args:
        player_id (int): The player's ID.
        player_name (str): The player's name.
        position (str): The player's position.
        team (str): The player's team (short name).
    """
    existing_player = Player.query.get(player_id)
    if not existing_player:
        try:
            # Add player to the database
            new_player = Player(id=player_id, name=player_name, position=position, team=team)
            db.session.add(new_player)
            db.session.commit()
            print(f"Added new player: {player_name} (ID: {player_id})")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding player {player_name} (ID: {player_id}): {e}")


def import_player_game_data(api_url):
    """
    Fetch player game data from an API and import it into the database.

    Args:
        api_url (str): The API endpoint URL.
        headers (dict): The headers required for API authentication.
    """
    try:
        # Fetch the data from the API
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Loop through the data and extract relevant fields
        for player_game in data:
            player_id = player_game.get("PlayerID")
            player_name = player_game.get("Name")
            position = player_game.get("Position")
            team = player_game.get("Team")

            # Ensure the player exists in the database
            add_player_if_not_exists(player_id, player_name, position, team)

            # Extract game and performance data
            game_id = player_game.get("GlobalGameID")  # Map to your Game model's ID if necessary
            rushing_attempts = player_game.get("RushingAttempts", 0)
            rushing_yards = player_game.get("RushingYards", 0)
            rushing_tds = player_game.get("RushingTouchdowns", 0)
            receiving_targets = player_game.get("ReceivingTargets", 0)
            receptions = player_game.get("Receptions", 0)
            receiving_yards = player_game.get("ReceivingYards", 0)
            receiving_tds = player_game.get("ReceivingTouchdowns", 0)

            # Add the player game data to the database
            add_player_game(
                player_id=player_id,
                game_id=game_id,
                rush_attempts=rushing_attempts,
                rush_yards=rushing_yards,
                rush_tds=rushing_tds,
                targets=receiving_targets,
                receptions=receptions,
                rec_yards=receiving_yards,
                rec_tds=receiving_tds,
            )

        print("Player game data imported successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error importing data: {e}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Import player game data into the database.")
    parser.add_argument("player_id", type=int, help="The ID of the player to fetch data for.")

    # Parse arguments
    args = parser.parse_args()

    # API configuration
    API_URL = "https://api.sportsdata.io/v3/nfl/stats/json/PlayerGameStatsBySeason/2024/" + str(args.player_id) + "/all?key=eb609e05efa8406fba6c84327f4ff4dc"

    # Call the function with the specified player ID
    import_player_game_data(API_URL)
