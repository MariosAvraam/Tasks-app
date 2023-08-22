from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask import jsonify
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from wtforms.validators import ValidationError
from config import Config
from models import Board, Column, Todo, User
from database import db
from forms import BoardForm, TaskForm, RegistrationForm, LoginForm, ColumnForm, EditBoardForm, EditColumnForm

app = Flask(__name__)
app.config.from_object(Config)

Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

db.init_app(app)


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

@app.route('/delete_board/<int:board_id>', methods=['POST'])
@login_required
def delete_board(board_id):
    board = db.get_or_404(Board, board_id)
    if board.user_id != current_user.id:
        flash('Access denied!')
        return redirect(url_for('boards'))
    
    db.session.delete(board)
    db.session.commit()
    flash('Board deleted successfully!', 'success')
    return redirect(url_for('boards'))


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

@app.route('/board/<int:board_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_board(board_id):
    board = db.get_or_404(Board, board_id)
    form = EditBoardForm()
    if form.validate_on_submit():
        board.title = form.title.data
        db.session.commit()
        flash('Board updated successfully!', 'success')
        return redirect(url_for('boards', board_id=board_id))
    elif request.method == 'GET':
        form.title.data = board.title
    return render_template('edit_board.html', form=form, board=board)

@app.route('/board/<int:board_id>/add_column', methods=['GET', 'POST'])
@login_required
def add_column(board_id):
    form = ColumnForm()
    board = Board.query.get_or_404(board_id)
    if form.validate_on_submit():
        new_column = Column(title=form.column_title.data, board_id=board_id)
        db.session.add(new_column)
        db.session.commit()
        flash('Column added successfully!', 'success')
        return redirect(url_for('display_board', board_id=board_id))
    return render_template('add_column.html', form=form, board=board)


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

@app.route('/column/<int:column_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_column(column_id):
    column = db.get_or_404(Column, column_id)
    form = EditColumnForm()
    if form.validate_on_submit():
        column.title = form.title.data
        db.session.commit()
        flash('Column updated successfully!', 'success')
        return redirect(url_for('display_board', board_id=column.board_id))
    elif request.method == 'GET':
        form.title.data = column.title
    return render_template('edit_column.html', form=form, column=column)

@app.route('/column/<int:column_id>/delete', methods=['POST'])
@login_required
def delete_column(column_id):
    column = db.get_or_404(Column, column_id)
    board_id = column.board_id
    db.session.delete(column)
    db.session.commit()
    flash('Column deleted successfully!', 'success')
    return redirect(url_for('display_board', board_id=board_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
