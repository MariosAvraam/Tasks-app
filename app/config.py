from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the Flask app."""
    SQLALCHEMY_DATABASE_URI = getenv("DB_URI", "sqlite:///tasks.db")
    SECRET_KEY = getenv("SECRET_KEY")
