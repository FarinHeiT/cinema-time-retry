from socket import socket

from flask import Flask, render_template, Blueprint

from cinema_time_retry_in import socketio, redis_db

from .helper_functions import generate_room_name

general = Blueprint('general', __name__)


@general.route('/')
def index():
    return render_template("Main.html")


@socketio.on('connection')
def connection(json):
    print('New user connected!' + str(json))


@socketio.on('create_room')
def create_room(json):
    room_name = generate_room_name()

    # redis_db.set()