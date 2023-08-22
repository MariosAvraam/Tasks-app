from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from .config import Config
from .database import db

app = Flask(__name__,
            template_folder='../templates',  # Adjust the path to your templates folder
            static_folder='../static')       # Adjust the path to your static folder

app.config.from_object(Config)

Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.get_or_404(User, user_id)

db.init_app(app)

# Import routes after app initialization to avoid circular imports
from . import routes
