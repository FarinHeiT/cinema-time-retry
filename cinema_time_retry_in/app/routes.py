import json

from flask import Flask, render_template, Blueprint, url_for,redirect

from cinema_time_retry_in import socketio, redis_db
from . import forms

from .helper_functions import generate_room_name

general = Blueprint('general', __name__)


@general.route('/')
def index():
    return render_template("Main.html")


@general.route('/room/<room_name>')
def room(room_name):
    link = json.loads(redis_db.get(room_name))['playlist'][0]
    print(link)
    password = json.loads(redis_db.get(room_name)["password"])
    return render_template('room.html', video_link=link, source='youtube', password=password)

@general.route("/password")
def password_in(data):
    form = forms.password_form()
    if form.validate_on_submit():
        if form.password.data == data['password']:
            socketio.emit("create_room")
        else:
            return redirect(url_for('password_in', data=data))
    return render_template("password.html", form=form)


@socketio.on('connection')
def connection(json):
    print('New user connected!' + str(json))


@socketio.on("t_password")
def type_in_password(data):
    return redirect(url_for('general.password_in', data=data))



@socketio.on('create_room')
def create_room(data):
    room_name = generate_room_name()

    room = {
        'playlist': [data['videoLink']],
        'password': [data['password']]
    }

    redis_db.set(room_name, json.dumps(room))

    socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)})


