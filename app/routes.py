from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from . import app, db
from .forms import RegistrationForm, LoginForm, BoardForm, EditBoardForm, TaskForm, ColumnForm, EditColumnForm, EditTaskForm
from .models import User, Board, Column, Task
from wtforms.validators import ValidationError

def validate_username(form, username):
    """Validate if the username is unique."""
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
        raise ValidationError('Username already in use.')

def validate_email(form, email):
    """Validate if the email is unique."""
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
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user)
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
        return redirect(url_for('display_board', board_id=new_board.id))
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


@app.route('/boards/<int:board_id>')
@login_required
def display_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.user_id != current_user.id:
        flash('Access denied!')
        return redirect(url_for('boards'))
    
    columns = Column.query.filter_by(board_id=board_id).all()
    for column in columns:
        column.tasks = Task.query.filter_by(column_id=column.id).order_by(Task.priority_value.desc()).all()
    
    return render_template('board.html', board=board, columns=columns)



@app.route('/boards/<int:board_id>/add_task/<int:column_id>', methods=['GET', 'POST'])
@login_required
def add_task(board_id, column_id):
    form = TaskForm()
    if form.validate_on_submit():
        task_content = form.task_content.data
        task_priority = form.priority.data
        deadline = form.deadline.data
        new_task = Task(task=task_content, completed=False, column_id=column_id, priority=task_priority, deadline=deadline)
        if form.priority.data == 'high':
            new_task.priority_value = 3
        elif form.priority.data == 'medium':
            new_task.priority_value = 2
        else:
            new_task.priority_value = 1
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('display_board', board_id=board_id))
    return render_template('add_task.html', form=form)

@app.route('/boards/<int:board_id>/edit', methods=['GET', 'POST'])
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

@app.route('/boards/<int:board_id>/add_column', methods=['GET', 'POST'])
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

    task = Task.query.get(task_id)
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

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = db.get_or_404(Task, task_id)
    form = EditTaskForm()
    if form.validate_on_submit():
        task.task = form.task_content.data
        task.priority = form.priority.data
        task.deadline = form.deadline.data
        if task.priority == 'High':
            task.priority_value = 3
        elif task.priority == 'Medium':
            task.priority_value = 2
        elif task.priority == 'Low':
            task.priority_value = 1
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('display_board', board_id=task.column.board_id))
    elif request.method == 'GET':
        form.task_content.data = task.task
        form.priority.data = task.priority
        form.deadline.data = task.deadline
    return render_template('edit_task.html', form=form, task=task)


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.get_or_404(Task, task_id)
    board_id = task.column.board_id
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('display_board', board_id=board_id))
