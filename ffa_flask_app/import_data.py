from app.models import add_player_game, db, Player, PlayerGame
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
    print(player_name)
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
    # print("Uncomment instructions!")

    # Call the function with the specified player ID
    
    # Set up argument parser
    wr_ids = {
        "Ja'marr Chase" : 22564,
        "Amon-Ra St. Brown" : 22587,
        "CeeDee Lamb" : 21679,
        "Justin Jefferson" : 21685,
        "Terry McLaurin" : 20873,
        "Garrett Wilson" : 23122,
        "Jaxon Smith-Njigba" : 23157,
        "Zay Flowers" : 23120,
        "Cortland Sutton" : 19800,
        "Malik Nabers" : 24953,
        "Ladd McConkey" : 25097,
        "Nico Collins" : 21756
    }

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

    for rb in rb_ids:
        # Path to your CSV file
        first, last = rb.split(" ")[0].lower(), rb.split(" ")[1].lower()
        CSV_FILE_PATH = f"../data/{first}_{last}_2024.csv"

        # Load the CSV and print the column names
        df = pd.read_csv(CSV_FILE_PATH, skiprows=1)
        print(df.columns)

        import_weekly_player_stats(rb_ids[rb][0], rb, rb_ids[rb][1], rb_ids[rb][2], CSV_FILE_PATH)

    
