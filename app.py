from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from wtforms.validators import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SECRET_KEY'] = 'Secret_Key'
Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

db = SQLAlchemy()
db.init_app(app)

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    columns = db.relationship('Column', backref='board', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    todos = db.relationship('Todo', backref='column', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    column_id = db.Column(db.Integer, db.ForeignKey('column.id'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    boards = db.relationship('Board', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
from forms import TodoForm, BoardForm, TaskForm, RegistrationForm, LoginForm

def validate_username(form, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
        raise ValidationError('Username already in use.')

def validate_email(form, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
        raise ValidationError('Email already registered.')

RegistrationForm.validate_username = validate_username
RegistrationForm.validate_email = validate_email



@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('boards'))
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        login_user(user)  # Automatically log the user in after registration
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/boards')
@login_required
def boards():
    user_boards = Board.query.filter_by(user_id=current_user.id).all()
    return render_template("boards.html", all_boards=user_boards)


@app.route('/create_board', methods=['GET', 'POST'])
@login_required
def create_board():
    form = BoardForm()
    if form.validate_on_submit():
        board_title = form.title.data
        new_board = Board(title=board_title, user_id=current_user.id)
        
        default_columns = ["To Do", "In Progress", "Done"]
        for col_title in default_columns:
            column = Column(title=col_title, board=new_board)
            db.session.add(column)
        
        db.session.add(new_board)
        db.session.commit()
        flash('Board created successfully!', 'success')
        return redirect(url_for('index'))  # or redirect to the new board's page
    return render_template('create_board.html', form=form)


@app.route('/board/<int:board_id>')
@login_required
def display_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.user_id != current_user.id:
        flash('Access denied!')
        return redirect(url_for('boards'))
    columns = Column.query.filter_by(board_id=board_id).all()
    return render_template('board.html', board=board, columns=columns)


@app.route('/board/<int:board_id>/add_task/<int:column_id>', methods=['GET', 'POST'])
@login_required
def add_task(board_id, column_id):
    form = TaskForm()
    if form.validate_on_submit():
        task_content = form.task_content.data
        new_task = Todo(task=task_content, completed=False, column_id=column_id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('display_board', board_id=board_id))
    return render_template('add_task.html', form=form)



@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        task = form.task.data
        new_todo = Todo(
            task=task,
            completed=False,
        )
        db.session.add(new_todo)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_todo.html', form=form)

@app.route('/update_task_column', methods=['POST'])
def update_task_column():
    data = request.json
    task_id = data['task_id']
    new_column_id = data['column_id']

    task = Todo.query.get(task_id)
    if not task:
        return jsonify(status='error', message='Task not found')

    task.column_id = new_column_id
    db.session.commit()

    return jsonify(status='success')



@app.route('/complete/<int:index>')
def complete_todo(index):
    if 0 <= index < len(todos):
        todos[index]['completed'] = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
