# ffa_flask_app/app/routes/__init__.py


from .players import players_bp
from .teams import teams_bp  # Import additional blueprints here

# Create a list of all blueprints to simplify registration
all_blueprints = [
    (players_bp, '/api/players'),  # Blueprint with URL prefix
    (teams_bp, '/api/teams'),      # Additional blueprints and their prefixes
]
