from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class BoardForm(FlaskForm):
    """Form to create a new board."""
    title = StringField('Board Title', validators=[DataRequired()])
    submit = SubmitField('Create Board')

class TaskForm(FlaskForm):
    """Form to add a new task."""
    task_content = StringField('Task', validators=[DataRequired()])
    priority_choices = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    priority = SelectField('Priority', choices=priority_choices, default='medium')
    submit = SubmitField('Add Task')


class RegistrationForm(FlaskForm):
    """Form to register a user."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm):
    """Form to login a user."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ColumnForm(FlaskForm):
    """Form to add a column."""
    column_title = StringField('Column Title', validators=[DataRequired()])
    submit = SubmitField('Add Column')

class EditBoardForm(FlaskForm):
    """Form to edit a board title."""
    title = StringField('Board Title', validators=[DataRequired()])
    submit = SubmitField('Update Board')

class EditColumnForm(FlaskForm):
    """Form to edit a column title."""
    title = StringField('Column Title', validators=[DataRequired()])
    submit = SubmitField('Update Column')

class EditTaskForm(FlaskForm):
    """Form to edit a task."""
    task_content = StringField('Task', validators=[DataRequired()])
    priority_choices = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    priority = SelectField('Priority', choices=priority_choices, default='medium')
    submit = SubmitField('Update Task')
