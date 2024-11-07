# ffa_flask_app/__init__.py

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config  # Direct relative import
import logging
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    # Clear the log file each time the app starts (only in development mode)
    if app.config['ENV'] == 'development' and app.config.get("LOG_FILE"):
        with open(app.config["LOG_FILE"], "w"):
            pass  # Opens the file in write mode to clear it

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Set up logging
    configure_logging(app)

    # Import models and register routes
    from .models import Player  # Direct relative import

    # Import and register all blueprints from routes
    from .routes import all_blueprints
    for blueprint, prefix in all_blueprints:
        app.register_blueprint(blueprint, url_prefix=prefix)

    return app

def configure_logging(app):
    # Set up logging based on configuration settings
    logging_level = app.config.get("LOGGING_LEVEL", "INFO")
    logging_format = app.config.get("LOGGING_FORMAT", "[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    log_file = app.config.get("LOG_FILE")

    # Configure the root logger
    if log_file:
        # Log to a file if LOG_FILE is specified
        logging.basicConfig(filename=log_file, level=logging_level, format=logging_format)
    else:
        # Log to the console
        logging.basicConfig(level=logging_level, format=logging_format)

    # Flask's built-in logger
    app.logger.setLevel(logging_level)
