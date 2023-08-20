from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import TodoForm, BoardForm, TaskForm
from flask_bootstrap import Bootstrap5
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SECRET_KEY'] = 'Secret_Key'
Bootstrap5(app)

db = SQLAlchemy()
db.init_app(app)

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    columns = db.relationship('Column', backref='board', lazy=True)

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


@app.route('/')
def index():
    results = db.session.execute(db.select(Board)).scalars()
    boards = results.all()
    return render_template("index.html", all_boards=boards)

@app.route('/create_board', methods=['GET', 'POST'])
def create_board():
    form = BoardForm()
    if form.validate_on_submit():
        board_title = form.title.data
        new_board = Board(title=board_title)
        
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
def display_board(board_id):
    board = Board.query.get_or_404(board_id)
    columns = Column.query.filter_by(board_id=board_id).all()
    return render_template('board.html', board=board, columns=columns)

@app.route('/board/<int:board_id>/add_task/<int:column_id>', methods=['GET', 'POST'])
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
