from app.models import *
from app import create_app
import time
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime, date

# Load environment variables from the .env file
load_dotenv()

app = create_app()


def import_game_data(games):
    '''
    Takes the json response from https://v1.american-football.api-sports.io/games (with team and season parameters)
    and creates a new game object, adding it to the database by calling add_game (in models.py)
    '''
    with app.app_context():
        for game in games:
            game_info = game.get("game", {})
            if game_info.get("stage") != "Pre Season":

                game_id = game_info.get("id")

                teams = game.get("teams", {})
                scores = game.get("scores", {})

                home_team = teams.get("home", {})
                away_team = teams.get("away", {})
                home_team_score = scores.get("home", {}).get("total")
                away_team_score = scores.get("away", {}).get("total")

                home_team_id = home_team.get("id")
                away_team_id = away_team.get("id")

                date_str = game_info.get("date").get("date")
                game_time_str = game_info.get("date").get("time")
                
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                game_time = datetime.strptime(game_time_str, "%H:%M").time()

                if not home_team_id or not away_team_id or not home_team_score or not away_team_score:
                    print(f"Skipping game due to missing information")
                    continue
                
                print(f"ID: {game_info.get("id")} - Date & Time: {date_str} {game_time_str} - {home_team.get('name')} vs {away_team.get('name')}: {home_team_score} - {away_team_score}")
                # Add game to the database
                add_game(home_team_id, away_team_id, home_team_score=home_team_score, away_team_score=away_team_score, 
                        date=date, game_time=game_time, id=game_id)
            

def static_team_game_import():
    '''
    API call commented out in case this function is accidentally recalled.
    This function does a static import for all 32 NFL teams from a specific season (year)
    into the postgres database
    '''
    team_ids = {
        "Raiders" : ["OAK", "AFC West", 1],
        "Jaguars" : ["JAX", "AFC South", 2],
        "Patriots" : ["NE", "AFC East", 3],
        "Giants" : ["NYG", "NFC East", 4],
        "Ravens" : ["BAL", "AFC North", 5],
        "Titans" : ["TEN", "AFC South", 6],
        "Lions" : ["DET", "NFC North", 7],
        "Falcons" : ["ATL", "NFC South", 8],
        "Browns" : ["CLE", "AFC North", 9],
        "Bengals" : ["CIN", "AFC North", 10],
        "Cardinals" : ["ARI", "NFC West", 11],
        "Eagles" : ["PHI", "NFC East", 12],
        "Jets" : ["NYJ", "AFC East", 13],
        "49ers" : ["SF", "NFC West", 14],
        "Packers" : ["GB", "NFC North", 15],
        "Bears" : ["CHI", "NFC North", 16],
        "Chiefs" : ["KC", "AFC West", 17],
        "Commanders" : ["WAS", "NFC East", 18],
        "Panthers" : ["CAR", "NFC South", 19],
        "Bills" : ["BUF", "AFC East", 20],
        "Colts" : ["IND", "AFC South", 21],
        "Steelers" : ["PIT", "AFC North", 22],
        "Seahawks" : ["SEA", "NFC West", 23],
        "Buccaneers" : ["TB", "NFC South", 24],
        "Dolphins" : ["MIA", "AFC East", 25],
        "Texans" : ["HOU", "AFC South", 26],
        "Saints" : ["NO", "NFC South", 27],
        "Broncos" : ["DEN", "AFC West", 28],
        "Cowboys" : ["DAL", "NFC East", 29],
        "Chargers" : ["LAC", "NFC West", 30],
        "Rams" : ["LAR", "NFC West", 31],
        "Vikings" : ["MIN", "NFC North", 32]
    }
    # with app.app_context():
    #     for team in team_ids:
    #         add_team(team_ids[team][0], team_ids[team][1], team_ids[team][2])

    API_URL = "https://v1.american-football.api-sports.io"
    API_KEY = os.getenv("API_SPORTS_NFL_KEY")

    endpoint = "/games"

    api_counter = 0

    for team in team_ids:
        # Parameters to be sent in the query string
        params = {
            "season": "2022",
            "team": str(team_ids[team][2]),
            "timezone" : "America/New_York"
        }

        # Headers to include in the request
        headers = {
            'x-rapidapi-host': "v1.american-football.api-sports.io",
            'x-rapidapi-key': API_KEY
        }
        
        # Make the GET request

        # TEN REQUESTS PER MINUTE
        api_counter += 1
        if api_counter % 10 == 0:
            print("Waiting to not screw with rate limiter...")
            time.sleep(61)
            print("Back to it!")
        
        response = requests.get(API_URL + endpoint, headers=headers, params=params)

        # Check the response status
        if response.status_code == 200:
            # Successful request
            data = response.json()
            games = data.get("response", [])
            import_game_data(games)
            print("Data added to database!")
        else:
            # Something went wrong
            print(f"Error: {response.status_code} - {response.text}")


def process_player_stats_from_game(data, game_id, game_date):
    
    # Create a dictionary to aggregate stats by player_id
    aggregated_stats = {}

    for team_data in data['response']:
        team_id = team_data['team']['id']
        for group in team_data['groups']:
            if group['name'] == 'Passing' or group['name'] == 'Rushing' or group['name'] == 'Receiving':
                for player_data in group['players']:
                    player_info = player_data['player']
                    player_id = player_info['id']
                    stats = {stat['name']: stat['value'] for stat in player_data['statistics']}

                    # Initialize stats for the player if not already aggregated
                    if player_id not in aggregated_stats:
                        
                        player = Player.query.filter_by(id=player_id).first()
                        if player:
                            position = player.position
                        else:  
                            if group['name'] == 'Passing':
                                position = "QB"
                            elif group['name'] == 'Rushing':
                                position = "RB"
                            else:
                                position = "WR"

                        aggregated_stats[player_id] = {
                            'team_id': team_id,
                            'name': player_info['name'],
                            'position': position,
                            'pass_attempts': 0,
                            'pass_completions': 0,
                            'pass_yards': 0,
                            'pass_tds': 0,
                            'pass_int': 0,
                            'rush_attempts': 0,
                            'rush_yards': 0,
                            'rush_tds': 0,
                            'longest_rush': 0,
                            'targets': 0,
                            'receptions': 0,
                            'rec_yards': 0,
                            'rec_tds': 0,
                            'longest_rec': 0,
                        }

                    # Aggregate the statistics for the player
                    if group['name'] == 'Passing':
                        aggregated_stats[player_id]['pass_attempts'] += int(stats.get('comp att', '0').split('/')[1]) if 'comp att' in stats else 0
                        aggregated_stats[player_id]['pass_completions'] += int(stats.get('comp att', '0').split('/')[0]) if 'comp att' in stats else 0
                        aggregated_stats[player_id]['pass_yards'] += int(stats.get('yards', '0'))
                        aggregated_stats[player_id]['pass_tds'] += int(stats.get('passing touch downs', '0'))
                        aggregated_stats[player_id]['pass_int'] += int(stats.get('interceptions', '0'))

                    elif group['name'] == 'Rushing':
                        aggregated_stats[player_id]['rush_attempts'] += int(stats.get('total rushes', '0'))
                        aggregated_stats[player_id]['rush_yards'] += int(stats.get('yards', '0'))
                        aggregated_stats[player_id]['rush_tds'] += int(stats.get('rushing touch downs', '0'))
                        aggregated_stats[player_id]['longest_rush'] = int(stats.get('longest rush', '0'))

                    elif group['name'] == 'Receiving':
                        aggregated_stats[player_id]['targets'] += int(stats.get('targets', '0'))
                        aggregated_stats[player_id]['receptions'] += int(stats.get('total receptions', '0'))
                        aggregated_stats[player_id]['rec_yards'] += int(stats.get('yards', '0'))
                        aggregated_stats[player_id]['rec_tds'] += int(stats.get('receiving touch downs', '0'))
                        aggregated_stats[player_id]['longest_rec'] = int(stats.get('longest reception', '0'))
                    

    # Process the aggregated statistics
    for player_id, stats in aggregated_stats.items():
        # Add the player to the database if he doesn't exist

        add_player(stats['name'], stats['position'], stats['team_id'], start_date=game_date, id=player_id)

        print(f"Name: {stats['name']} - Position: {stats['position']} - Team ID: {stats['team_id']} - Player ID: {player_id}")

        # Add the PlayerGame to the database if it doesn't exist for this player and game

        add_player_game(
            player_id,
            game_id,
            pass_attempts=stats['pass_attempts'],
            pass_completions=stats['pass_completions'],
            pass_yards=stats['pass_yards'],
            pass_tds=stats['pass_tds'],
            pass_int=stats['pass_int'],
            rush_attempts=stats['rush_attempts'],
            rush_yards=stats['rush_yards'],
            rush_tds=stats['rush_tds'],
            longest_rush=stats['longest_rush'],
            targets=stats['targets'],
            receptions=stats['receptions'],
            rec_yards=stats['rec_yards'],
            rec_tds=stats['rec_tds'],
            longest_rec=stats['longest_rec']
        )

        print(f"Player ID: {player_id} - Game ID: {game_id}")
        print(f"Passing - Attempts: {stats['pass_attempts']} | Completions: {stats['pass_completions']} | Yds: {stats['pass_yards']} | Tds: {stats['pass_tds']} | Int: {stats['pass_int']}")
        print(f"Rushing - Attempts: {stats['rush_attempts']} | Yds: {stats['rush_yards']} | Tds: {stats['rush_tds']} | Longest Rush: {stats['longest_rush']}")
        print(f"Receiving - Targets: {stats['targets']} | Recs: {stats['receptions']} | Yds: {stats['rec_yards']} | Tds: {stats['rec_tds']} | Longest Rec: {stats['longest_rec']}")
        print("----------------------------------------------------------------------")
        print()

def get_oldest_unprocessed_game():
    try:
        # Query for the oldest game with stats_processed=False
        game = Game.query.filter_by(stats_processed=False).order_by(Game.date.asc()).first()
        if game:
            print(f"Oldest unprocessed game found: Game ID {game.id}, Date: {game.date}")
            return game.id, game.date  # Return the game ID
        else:
            print("No unprocessed games found.")
            return None
    except Exception as e:
        print(f"Error retrieving oldest unprocessed game: {e}")
        return None, None


if __name__ == "__main__":

    with app.app_context():
        for x in range(100):
            print()
            print(x)
            if x != 0 and x % 10 == 0:
                print("Waiting to not screw up API access")
                time.sleep(60)

            game_id, game_date = get_oldest_unprocessed_game()
            if not game_id or not game_date:
                print("No more unprocessed games available.")
                break

            if game_id:

                API_URL = "https://v1.american-football.api-sports.io"
                API_KEY = os.getenv("API_SPORTS_NFL_KEY")

                endpoint = "/games/statistics/players"

                api_counter = 0

                # Headers to include in the request
                headers = {
                    'x-rapidapi-host': "v1.american-football.api-sports.io",
                    'x-rapidapi-key': API_KEY
                }

                params = {
                    "id" : game_id
                }

                response = requests.get(API_URL + endpoint, headers=headers, params=params)

                # Check the response status
                if response.status_code == 200:
                    # Successful request

                    data = response.json()

                    # Modify function to accept raw json rather than a file path
                    process_player_stats_from_game(data, game_id, game_date)

                    print(f"Processed player stats from game: {game_id}")

                    # Update the stats_processed field in the database
                    try:
                        game = Game.query.get(game_id)
                        if game:
                            game.stats_processed = True
                            db.session.commit()
                            print(f"Game ID {game_id} marked as processed.")
                        else:
                            print(f"Game ID {game_id} not found.")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Error updating stats_processed for Game ID {game_id}: {e}")
                else:
                    # Something went wrong
                    print(f"Error: {response.status_code} - {response.text}")

        


    
    


'''
# # Save to a file
# with open("patriots_season_2024.json", "w") as json_file:
#     json.dump(data, json_file, indent=4)  # Use `indent=4` for pretty formatting
'''


    
