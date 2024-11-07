# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://leocooley:new_password@localhost:5432/ffb_project")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids overhead of tracking modifications

    # Logging configuration
    ENV = os.getenv("FLASK_ENV")
    LOGGING_LEVEL = "DEBUG" if ENV == "development" else "INFO"
    LOGGING_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    LOG_FILE = "app.log" if ENV == "development" else None  # Log to file only in development

