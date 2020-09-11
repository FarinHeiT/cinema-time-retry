from flask import Flask, render_template, Blueprint

from cinema_time_retry_in import socketio

general = Blueprint('general', __name__)

@general.route('/')
def index():
    return render_template("Main.html")

@socketio.on('connection')
def connection(json):
    print('New user connected!' + str(json))