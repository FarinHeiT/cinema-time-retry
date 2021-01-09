from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class Password_form(FlaskForm):
    password = StringField("Password", validators=[])
    name = StringField("Name", validators=[DataRequired(), Length(max=20)])


class Message_form(FlaskForm):
    box = StringField("Message", validators=[DataRequired()])
    button = SubmitField(label='Send')
