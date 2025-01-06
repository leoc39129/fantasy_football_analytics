import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from itertools import groupby
from operator import attrgetter
from sqlalchemy.sql import func, case

from app.models import *
from app import create_app

app = create_app()


def get_player_performance(player_id, num_games=8):
    """Fetch past game performances for a specific player."""
    return (PlayerGame.query
            .join(Game, PlayerGame.game_id == Game.id)
            .filter(PlayerGame.player_id == player_id)
            .order_by(Game.date.desc())  # Sort by most recent games
            .limit(num_games)  # Fetch the last `num_games` performances
            .all())

def get_pos_vs_team(team_id, position, num_games=8):
    """Fetch performances of players with the same position against a specific team."""
    if position not in ["QB", "RB", "WR"]:
        raise ValueError(f"Unsupported position: {position}. Supported positions are QB, RB, WR.")
    
    performances = (PlayerGame.query
                       .join(Game, PlayerGame.game_id == Game.id)
                       .join(Player, PlayerGame.player_id == Player.id)
                       .filter((Game.away_team_id == team_id) | (Game.home_team_id == team_id))
                       .filter(Player.position == position)  # Filter by position
                       .order_by(Game.date.desc())  # Sort by most recent games
                       .all())
    
    # Group by game_id and sort within each game by rushing yards and attempts
    grouped_by_game = groupby(performances, key=attrgetter('game_id'))

    top_performances = []

    for game_id, game_performances in grouped_by_game:
        # Define sorting criteria based on position
        if position == "QB":
            # Sort by passing yards, then passing attempts
            top_player = sorted(game_performances, 
                                key=lambda x: (x.pass_yards, x.pass_attempts), 
                                reverse=True)[0]
        elif position == "RB":
            # Sort by rushing yards, then rushing attempts
            top_player = sorted(game_performances, 
                                key=lambda x: (x.rush_yards, x.rush_attempts), 
                                reverse=True)[0]
        elif position == "WR":
            # Sort by receiving yards, then receptions
            top_player = sorted(game_performances, 
                                key=lambda x: (x.rec_yards, x.receptions), 
                                reverse=True)[0]

        top_performances.append(top_player)

    # Limit to the last `num_games`
    return top_performances[:num_games]


def calculate_moving_averages(player_games, stats, window=3):
    """Calculate moving averages for the player over their past games."""
    data = {stat: [] for stat in stats}
    
    for game in player_games:
        for stat in stats:
            data[stat].append(getattr(game, stat, 0))  # Default to 0 if stat is missing

    df = pd.DataFrame(data)
    moving_averages = df.rolling(window=window).mean().iloc[-1]  # Get the most recent moving averages
    return moving_averages

def calculate_opponent_averages(pos_vs_team_games, stats):
    """Calculate averages for players of the same position against the opponent."""
    data = {stat: [] for stat in stats}

    for game in pos_vs_team_games:
        for stat in stats:
            data[stat].append(getattr(game, stat, 0))  # Default to 0 if stat is missing

    df = pd.DataFrame(data)
    opponent_averages = df.mean()  # Compute the mean for each stat
    return opponent_averages


def train_model(historical_data_df, target_column):
    """Train a Random Forest model for a specific stat."""
    # Use all columns except the target column and non-relevant ones as features
    feature_columns = [col for col in historical_data_df.columns if col not in ['game_id', 'player_id', 'position', 'rank', target_column]]

    X = historical_data_df[feature_columns]
    y = historical_data_df[target_column]

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"{target_column} - Mean Squared Error: {mse:.2f}")

    return model



def predict_stat(model, combined_features, feature_columns):
    """Predict a single stat using the trained model."""
    # Ensure combined_features only includes the necessary columns
    input_data = combined_features[feature_columns].to_numpy().reshape(1, -1)
    return model.predict(input_data)[0]



def load_historical_data(position):
    """Fetch the best positional performance for each team from every game."""

    # Define performance metric based on position
    performance_metric = case(
        (Player.position == "QB", PlayerGame.pass_yards),
        (Player.position.in_(["RB", "WR"]), PlayerGame.rush_yards + PlayerGame.rec_yards),
        else_=0
    )

    subquery = (
        db.session.query(
            PlayerGame.game_id,
            Game.home_team_id,
            Game.away_team_id,
            Player.id.label("player_id"),
            Player.position,
            performance_metric.label("total_yards"),
            PlayerGame.rush_attempts,
            PlayerGame.rush_yards,
            PlayerGame.rush_tds,
            PlayerGame.targets,
            PlayerGame.receptions,
            PlayerGame.rec_yards,
            PlayerGame.rec_tds,
            PlayerGame.pass_attempts,
            PlayerGame.pass_completions,
            PlayerGame.pass_yards,
            PlayerGame.pass_tds,
            PlayerGame.pass_int,
            func.row_number().over(
                partition_by=[PlayerGame.game_id, Game.home_team_id, Game.away_team_id],
                order_by=performance_metric.desc()
            ).label("rank")
        )
        .join(Game, PlayerGame.game_id == Game.id)
        .join(Player, PlayerGame.player_id == Player.id)
        .filter(Player.position == position)  # Filter by the specified position
        .filter(performance_metric.isnot(None))  # Exclude rows where performance_metric is None
        .subquery()
    )

    # Query to fetch the top performance for each team in every game
    query = (
        db.session.query(subquery)
        .filter(subquery.c.rank <= 2)  # Top two performances per game (one per team)
        .order_by(subquery.c.game_id, subquery.c.total_yards.desc())
    )

    return query.all()





def main():
    with app.app_context():
        player_name = input("Enter the player's name who you want to predict performance for: ")
        player = Player.query.filter_by(name=player_name).first()
        if not player:
            print(f"Player '{player_name}' not found.")
            return

        team_name = input("Enter the team abbreviation this player is playing against: ")
        team = Team.query.filter_by(name=team_name).first()
        if not team:
            print(f"Team '{team_name}' not found.")
            return

        stats = ['rush_attempts', 'rush_yards', 'rush_tds',
                 'targets', 'receptions', 'rec_yards', 'rec_tds', 
                 'pass_attempts', 'pass_completions', 'pass_yards', 'pass_tds', 'pass_int']

        player_games = get_player_performance(player.id)
        pos_vs_team_games = get_pos_vs_team(team.id, player.position)

        if not player_games:
            print(f"No past performance data found for {player_name}.")
            return

        if not pos_vs_team_games:
            print(f"No performance data found for {player.position} against {team_name}.")
            return

        # Calculate moving averages
        print("\nCalculating player-specific moving averages...")
        player_moving_averages = calculate_moving_averages(player_games, stats, window=3)
        print(player_moving_averages)

        print("\nCalculating opponent-specific averages...")
        opponent_averages = calculate_opponent_averages(pos_vs_team_games, stats)
        print(opponent_averages)

        # Combine features
        print("\nCombining features...")

        # Rename columns for clarity
        player_moving_averages = player_moving_averages.rename(lambda x: f"player_{x}")
        opponent_averages = opponent_averages.rename(lambda x: f"opponent_{x}")

        combined_features = pd.concat([player_moving_averages, opponent_averages], axis=1)
        print(combined_features)

        # Step 3: Load historical data
        columns = [
            "game_id", "home_team_id", "away_team_id", "player_id", "position",
            "total_yards", "rush_attempts", "rush_yards", "rush_tds", "targets", "receptions",
            "rec_yards", "rec_tds", "pass_attempts", "pass_completions", "pass_yards",
            "pass_tds", "pass_int", "rank"
        ]
        historical_data_df = pd.DataFrame(load_historical_data(player.position), columns=columns)

        # Step 4: Train models for each stat
        print("Training models...")

        if player.position == 'RB' or player.position == 'WR' or player.position == 'TE':
            target_stats = ['rush_attempts', 'rush_yards', 'rush_tds', 'targets', 'receptions', 'rec_yards', 'rec_tds']

        elif player.position == 'QB':
            target_stats = ['rush_attempts', 'rush_yards', 'rush_tds',
                            'pass_attempts', 'pass_completions', 'pass_yards', 'pass_tds', 'pass_int']

        models = {}
        feature_columns_dict = {}
        for stat in target_stats:
            print(f"Training model for {stat}...")
            feature_columns = [f"player_{col}" if f"player_{col}" in combined_features.columns else f"opponent_{col}" for col in feature_columns]

            feature_columns_dict[stat] = feature_columns
            models[stat] = train_model(historical_data_df, stat)

        # Step 5: Predict performance
        print("\nPredicting performance...")
        predictions = {}
        for stat in target_stats:
            predictions[stat] = predict_stat(models[stat], combined_features, feature_columns_dict[stat])

        # Step 6: Display predictions
        print("\nPredicted performance:")
        for stat, value in predictions.items():
            print(f"{stat}: {value:.2f}")


if __name__ == "__main__":
    main()

