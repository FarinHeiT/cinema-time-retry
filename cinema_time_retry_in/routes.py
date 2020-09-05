from flask import Flask, render_template, Blueprint

general = Blueprint('general', __name__)

@general.route('/')
def index():
    return render_template("main.html")
