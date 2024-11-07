# seed.py
from app import app, db
from ffa_flask_app.app.models import Player

# Initialize the Flask app context
with app.app_context():
    # Example players to add to the database
    players = [
        Player(name="Derrick Henry", position="RB", team="TEN", fantasy_points=35.9),
        Player(name="Patrick Mahomes", position="QB", team="KC", fantasy_points=28.3),
        Player(name="Davante Adams", position="WR", team="LV", fantasy_points=24.4),
        # Add more players as needed
    ]

    # Add all players to the session
    db.session.add_all(players)
    db.session.commit()  # Commit the transaction

    print("Database seeded successfully!")
