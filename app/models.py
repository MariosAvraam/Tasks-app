from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Board(db.Model):
    """Model for Boards."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    columns = db.relationship('Column', backref='board', lazy=True, cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Column(db.Model):
    """Model for Columns."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    tasks = db.relationship('Task', backref='column', lazy=True, cascade="all, delete-orphan")

class Task(db.Model):
    """Model for Tasks."""
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    column_id = db.Column(db.Integer, db.ForeignKey('column.id'), nullable=False)
    priority = db.Column(db.String(10), default='medium')
    priority_value = db.Column(db.Integer, default=2)
    deadline = db.Column(db.Date, nullable=True)

class User(UserMixin, db.Model):
    """Model for User."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    boards = db.relationship('Board', backref='user', lazy=True)

    def set_password(self, password):
        """Set a hashed password for the user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)
