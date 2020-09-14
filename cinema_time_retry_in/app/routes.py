import json

from flask import Flask, render_template, Blueprint, url_for

from cinema_time_retry_in import socketio, redis_db

from .helper_functions import generate_room_name

general = Blueprint('general', __name__)


@general.route('/')
def index():
    return render_template("Main.html")


@general.route('/room/<room_name>')
def room(room_name):
    link = json.loads(redis_db.get(room_name))['playlist'][0]
    print(link)
    return render_template('room.html', video_link=link)


@socketio.on('connection')
def connection(json):
    print('New user connected!' + str(json))


@socketio.on('create_room')
def create_room(data):
    room_name = generate_room_name()

    room = {
        'playlist': [data['videoLink']]
    }

    redis_db.set(room_name, json.dumps(room))

    socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)})
