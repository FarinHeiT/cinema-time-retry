from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class password_form(FlaskForm):
    password = StringField("Password")

class name_form(FlaskForm):
    name = StringField("Name")

