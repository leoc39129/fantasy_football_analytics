from app.models import *
from app import create_app
import time
import pandas as pd

app = create_app()

def add_player_if_not_exists(player_id, player_name, team, position):
    """
    Check if a player exists in the database, and add them if not.
    :param player_id: The player's ID.
    :param player_name: The player's name.
    :param team: The player's team.
    :param position: The player's position.
    """
    with app.app_context():
        existing_player = Player.query.get(player_id)
        if not existing_player:
            try:
                new_player = Player(id=player_id, name=player_name, team=team, position=position)
                db.session.add(new_player)
                db.session.commit()
                print(f"Added new player: {player_name} (ID: {player_id})")
            except Exception as e:
                db.session.rollback()
                print(f"Error adding player {player_name} (ID: {player_id}): {e}")


def import_weekly_player_stats(player_id, player_name, team, position, csv_path):
    """
    Import weekly stats for a player from a CSV file and insert them into the database.
    :param player_id: The player's ID in the database.
    :param player_name: The player's name.
    :param team: The player's team.
    :param position: The player's position.
    :param csv_path: Path to the CSV file with weekly stats.
    """
    # Check if the player exists and add them if not
    add_player_if_not_exists(player_id, player_name, team, position)

    # Load the CSV data into a DataFrame
    df = pd.read_csv(csv_path, skiprows=1)

    # Define the columns to extract
    relevant_columns = [
        "Date", "Att", "Yds", "TD", "Tgt", "Rec", "Yds.1", "TD.1"
    ]

    # Rename columns for consistency with the PlayerGame model
    column_mapping = {
        "Date": "date",
        "Att": "rush_attempts",
        "Yds": "rush_yards",
        "TD": "rush_tds",
        "Tgt": "targets",
        "Rec": "receptions",
        "Yds.1": "rec_yards",
        "TD.1": "rec_tds"
    }
    
    # Filter and rename the relevant columns
    df = df[relevant_columns].rename(columns=column_mapping)

    # Remove any rows with aggregate or non-week data
    # df = df.dropna(subset=[""])

    with app.app_context():
        for _, row in df.iterrows():
            try:
                # Create a new PlayerGame instance
                add_player_game(
                    player_id=player_id,
                    game_id=1,
                    rush_attempts=int(row["rush_attempts"]),
                    rush_yards=float(row["rush_yards"]),
                    rush_tds=int(row["rush_tds"]),
                    targets=int(row["targets"]),
                    receptions=int(row["receptions"]),
                    rec_yards=float(row["rec_yards"]),
                    rec_tds=int(row["rec_tds"])
                )

            except Exception as e:
                db.session.rollback()
                print(f"Error importing stats for Week {row['date']}: {e}")

if __name__ == "__main__":    

    rb_ids = {
        "Breece Hall" : [22526, "NYJ", "RB"],
        "Saquon Barkley" : [19766, "PHI", "RB"],
        "Derrick Henry" : [17959, "BAL", "RB"],
        "Alvin Kamara" : [18878, "NO", "RB"],
        "Bijan Robinson" : [23189, "ATL", "RB"],
        "Jonathan Taylor" : [21682, "IND", "RB"],
        "Joe Mixon" : [18858, "HOU", "RB"],
        "Aaron Jones" : [19045, "MIN", "RB"],
        "Chase Brown" : [24374, "CIN", "RB"],
        "Jahmyr Gibbs" : [23200, "DET", "RB"],
        "David Montgomery" : [20882, "DET", "RB"],
        "Josh Jacobs" : [20824, "GB", "RB"],
        "Kyren Williams" : [23212, "LAR", "RB"],
        "JK Dobbins" : [21674, "LAC", "RB"],
        "James Conner" : [18983, "ARI", "RB"],
        "Bucky Irving" : [24967, "TB", "RB"]
    }

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

    
