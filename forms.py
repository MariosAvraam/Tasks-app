from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

class TodoForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    submit = SubmitField('Add')

class BoardForm(FlaskForm):
    title = StringField('Board Title', validators=[DataRequired()])
    submit = SubmitField('Create Board')

class TaskForm(FlaskForm):
    task_content = StringField('Task', validators=[DataRequired()])
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



