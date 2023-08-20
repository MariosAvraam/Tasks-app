from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class TodoForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    submit = SubmitField('Add')

class BoardForm(FlaskForm):
    title = StringField('Board Title', validators=[DataRequired()])
    submit = SubmitField('Create Board')
