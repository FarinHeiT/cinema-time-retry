from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class password_form(FlaskForm):
    password = StringField("Password", validators=[DataRequired()])

class name_form(FlaskForm):
    name = StringField("Name")
