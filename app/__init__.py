from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from .config import Config
from .database import db

# Create the Flask app instance
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# Load configurations from the Config class
app.config.from_object(Config)

# Initialize Flask-Bootstrap
Bootstrap5(app)

# Initialize the Flask-Login extension
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    """Load a user based on its user_id."""
    from .models import User
    return db.get_or_404(User, user_id)

# Initialize Flask-SQLAlchemy with the app
db.init_app(app)

# Import routes after app initialization to avoid circular imports
from . import routes
