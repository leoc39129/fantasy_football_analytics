from app.models import *
from app import create_app
import time
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

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
            

if __name__ == "__main__":    

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
            "season": "2024",
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
    


'''
# # Save to a file
# with open("patriots_season_2024.json", "w") as json_file:
#     json.dump(data, json_file, indent=4)  # Use `indent=4` for pretty formatting
'''


    
