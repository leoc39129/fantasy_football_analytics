import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from app.models import *
from app import create_app

app = create_app()


def get_player_performance(player_id):
    """Fetch past game performances for a specific player."""
    return PlayerGame.query.filter_by(player_id=player_id).all()

def get_pos_vs_team(team_id, position):
    """Fetch performances of players with the same position against a specific team."""
    return (PlayerGame.query
            .join(Game, PlayerGame.game_id == Game.id)
            .join(Player, PlayerGame.player_id == Player.id)
            .filter((Game.away_team_id == team_id) | (Game.home_team_id == team_id))
            .filter(Player.position == position)
            .all())

def create_stat_dataset(player_games, stat):
    """Convert PlayerGame instances to a DataFrame with a specific stat."""
    data = []
    for i, pg in enumerate(player_games):
        data.append({
            'game_index': i,
            'stat': getattr(pg, stat)
        })
    return pd.DataFrame(data)

def train_stat_model(df):
    """Train a Random Forest model on the given stat."""
    if df.empty or len(df) < 2:
        return None

    X = df[['game_index']]
    y = df['stat']

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    return model

def predict_next_stat(model, num_games):
    """Predict the next stat using the trained model."""
    if not model:
        return 0.0
    return model.predict([[num_games]])[0]

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

        stats = ['rush_attempts', 'rush_yards', 'rush_tds', 'receptions', 'rec_yards', 'rec_tds']
        predictions = {}


        for stat in stats:
            print(f"\nTraining model for {stat}...")

            player_games = get_player_performance(player.id)
            pos_vs_team_games = get_pos_vs_team(team.id, player.position)

            player_df = create_stat_dataset(player_games, stat)
            pos_vs_team_df = create_stat_dataset(pos_vs_team_games, stat)

            combined_df = pd.concat([player_df, pos_vs_team_df], ignore_index=True)
            print(f"Length of combined dataset: {len(combined_df)}")

            model = train_stat_model(combined_df)
            prediction = predict_next_stat(model, len(combined_df))
            predictions[stat] = prediction

        print(f"\nPredicted performance for {player.name}'s upcoming game against {team.name}:")
        for stat, value in predictions.items():
            print(f"{stat.replace('_', ' ').title()}: {value:.2f}")

if __name__ == "__main__":
    main()

