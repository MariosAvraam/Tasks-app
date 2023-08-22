from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class BoardForm(FlaskForm):
    title = StringField('Board Title', validators=[DataRequired()])
    submit = SubmitField('Create Board')


class TaskForm(FlaskForm):
    task_content = StringField('Task', validators=[DataRequired()])
    priority_choices = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    priority = SelectField('Priority', choices=priority_choices, default='medium')
    submit = SubmitField('Add Task')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ColumnForm(FlaskForm):
    column_title = StringField('Column Title', validators=[DataRequired()])
    submit = SubmitField('Add Column')

class EditBoardForm(FlaskForm):
    title = StringField('Board Title', validators=[DataRequired()])
    submit = SubmitField('Update Board')

class EditColumnForm(FlaskForm):
    title = StringField('Column Title', validators=[DataRequired()])
    submit = SubmitField('Update Column')

class EditTaskForm(FlaskForm):
    task_content = StringField('Task', validators=[DataRequired()])
    priority_choices = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    priority = SelectField('Priority', choices=priority_choices, default='medium')
    submit = SubmitField('Update Task')



