import json
import uuid
from flask import Flask, render_template, Blueprint, url_for, redirect, session, request

from cinema_time_retry_in import socketio, redis_db
from . import forms

from flask_socketio import join_room, SocketIO

from .helper_functions import generate_room_name

general = Blueprint('general', __name__)


@general.route('/', methods=('GET', 'POST'))
def index():
    # Generate session id
    if '_id' not in session:
        session['_id'] = uuid.uuid1().hex

    print(session['_id'])

    # Username form
    form = forms.name_form()
    if form.validate_on_submit() and request.method == 'POST':
        session['username'] = form.name.data

    return render_template("Main.html", form=form)


@general.route('/room/<room_name>')
def room(room_name):
    print(json.loads(redis_db.get(room_name))['users'])
    if session['_id'] in json.loads(redis_db.get(room_name))['users']:
        link = json.loads(redis_db.get(room_name))['playlist'][0]
        password = json.loads(redis_db.get(room_name))['password']
        return render_template('room.html', video_link=link, source='youtube',
                               password=password,
                               room_name=room_name)
    else:
        return redirect(url_for('general.password_in', room_name=room_name))


@socketio.on('join_room')
def join_room(data):
    join_room(data['room_name'])


@general.route("/password", methods=('GET', 'POST'))
def password_in():
    room_name = request.args.get('room_name')
    form = forms.password_form()
    if form.validate_on_submit():
        if form.password.data == json.loads(redis_db.get(room_name))['password']:

            data = json.loads(redis_db.get(room_name))
            users = data['users']
            users.append(session['_id'])
            data = json.loads(redis_db.get(room_name))
            data['users'] = users

            redis_db.set(room_name, json.dumps(data))

            return redirect(url_for('general.room', room_name=room_name))

        else:
            return redirect(url_for('general.password_in', room_name=room_name))

    return render_template("password.html", form=form)


@socketio.on('create_room')
def create_room(data):
    room_name = generate_room_name()

    room = {
        'playlist': [data['videoLink']],
        'password': data['password'],
        'users': []
    }

    redis_db.set(room_name, json.dumps(room))
    socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)})


@socketio.on('sayHi')
def say_hi():
    socketio.emit('displaySayHi')
