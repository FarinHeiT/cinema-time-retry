from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError


class Password_form(FlaskForm):
    password = StringField("Password", validators=[])
    name = StringField("Name", validators=[DataRequired(), Length(max=20)])
    color = SelectField('color', choices=[('000000', 'black'), ('0000FF', 'blue'), ('FF0000', 'red'), ('00FF00', 'green')])


class Message_form(FlaskForm):
    box = StringField("Message", validators=[DataRequired()])
    button = SubmitField(label='Send')
