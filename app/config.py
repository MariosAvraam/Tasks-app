from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the Flask app."""
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URL")
    SECRET_KEY = getenv("SECRET_KEY")
