from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, ValidationError


class password_form(FlaskForm):
    password = StringField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired(), Length(max=20)])




