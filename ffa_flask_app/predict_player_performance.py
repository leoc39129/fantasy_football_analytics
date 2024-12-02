import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, accuracy_score
import warnings

from sqlalchemy import create_engine
from app.models import PlayerGame, Player
from app import create_app

# # Suppress warnings for simplicity
# warnings.filterwarnings("ignore")

# # Load your data (adjust the path)
# CSV_FILE_PATH = "player_game_stats.csv"  # Replace with your file path
# data = pd.read_csv(CSV_FILE_PATH)

# # Example dataset structure:
# # Columns: ["rush_attempts", "rush_yards", "rush_tds", "targets", "receptions", "rec_yards", "rec_tds", "performance_metric"]
# # "performance_metric" can be the total fantasy points, yards, or any performance measure you're trying to predict.

# # Prepare features (X) and target (y)
# X = data[["rush_attempts", "targets", "receptions", "rec_yards", "rush_yards"]]
# y = data["performance_metric"]  # Replace with your target variable

# # Split the data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Placeholder for results
# results = {}

# # 1. Linear Regression
# def linear_regression():
#     model = LinearRegression()
#     model.fit(X_train, y_train)
#     predictions = model.predict(X_test)
#     mse = mean_squared_error(y_test, predictions)
#     results["Linear Regression"] = mse
#     print("Linear Regression MSE:", mse)

# # 2. Logistic Regression (for binary classification tasks, e.g., "over/under 10 points")
# def logistic_regression():
#     # Convert target to binary (example: above or below 10 points)
#     binary_y_train = (y_train > 10).astype(int)
#     binary_y_test = (y_test > 10).astype(int)
#     model = LogisticRegression()
#     model.fit(X_train, binary_y_train)
#     predictions = model.predict(X_test)
#     accuracy = accuracy_score(binary_y_test, predictions)
#     results["Logistic Regression"] = accuracy
#     print("Logistic Regression Accuracy:", accuracy)

# # 3. Decision Tree Regressor
# def decision_tree():
#     model = DecisionTreeRegressor(random_state=42)
#     model.fit(X_train, y_train)
#     predictions = model.predict(X_test)
#     mse = mean_squared_error(y_test, predictions)
#     results["Decision Tree"] = mse
#     print("Decision Tree MSE:", mse)

# # 4. Neural Network (MLP Regressor)
# def neural_network():
#     model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
#     model.fit(X_train, y_train)
#     predictions = model.predict(X_test)
#     mse = mean_squared_error(y_test, predictions)
#     results["Neural Network"] = mse
#     print("Neural Network MSE:", mse)

# Run all models
# if __name__ == "__main__":
#     print("Training and evaluating models...\n")
#     linear_regression()
#     logistic_regression()
#     decision_tree()
#     neural_network()

#     print("\nResults Summary:")
#     for model, score in results.items():
#         print(f"{model}: {score}")


# Define fantasy scoring rules
def calculate_fantasy_points(row):
    """Calculate PPR fantasy points based on game stats."""
    return (
        row['receptions'] +
        row['rec_yards'] / 10 +
        row['rush_yards'] / 10 +
        row['rec_tds'] * 6 +
        row['rush_tds'] * 6
    )

# Connect to the Flask app and database
app = create_app()

def fetch_player_data(player_id):
    """Fetch historical player game data from the database."""
    with app.app_context():
        # Use SQLAlchemy to query the PlayerGame table
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        query = f"""
        SELECT rush_attempts, rush_yards, rush_tds, targets, receptions, rec_yards, rec_tds
        FROM player_games
        WHERE player_id = {player_id};
        """
        df = pd.read_sql(query, engine)
        return df

def predict_next_week_fantasy_points(player_id):
    """Predict a player's fantasy points for the next week using Linear Regression."""
    # Fetch historical data
    player_data = fetch_player_data(player_id)

    if player_data.empty:
        print(f"No data found for Player ID {player_id}")
        return

    # Add fantasy points column based on historical data
    player_data['fantasy_points'] = player_data.apply(calculate_fantasy_points, axis=1)

    # Prepare features (X) and target (y)
    X = player_data[["rush_attempts", "targets", "receptions", "rec_yards", "rush_yards"]]
    y = player_data["fantasy_points"]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Linear Regression model
    lin_model = LinearRegression()
    lin_model.fit(X_train, y_train)

    # Predict fantasy points for the test set
    predictions = lin_model.predict(X_test)

    # Compare predictions with actual values
    test_results = pd.DataFrame({
        "Actual": y_test,
        "Predicted": predictions
    })
    print("\nTest Set Predictions vs Actual Values:")
    print(test_results)

    # Calculate evaluation metrics
    mae = np.mean(np.abs(test_results["Actual"] - test_results["Predicted"]))
    mse = np.mean((test_results["Actual"] - test_results["Predicted"])**2)
    print(f"\nModel Evaluation Metrics:")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Squared Error (MSE): {mse:.2f}")

    return test_results

# Example usage
if __name__ == "__main__":
    # Replace with the actual player ID
    player_id = 22526  # Example: Breece Hall's Player ID
    predict_next_week_fantasy_points(player_id)

