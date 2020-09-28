import json
import uuid
from flask import Flask, render_template, Blueprint, url_for, redirect, session, request
from flask_socketio import join_room as socket_join_room
from flask_socketio import close_room

from cinema_time_retry_in import socketio, redis_db
from . import forms

from flask_socketio import join_room, SocketIO

from .helper_functions import generate_room_name

general = Blueprint('general', __name__)


@general.route('/', methods=('GET', 'POST'))
def index():
    print(session['_id'])

    return render_template("Main.html")


@general.route('/room/<room_name>')
def room(room_name):
    # output user lists
    print(json.loads(redis_db.get(room_name))['users'])
    print(json.loads(redis_db.get(room_name))['names'])
    print(json.loads(redis_db.get(room_name))['online'])

    if session['_id'] in json.loads(redis_db.get(room_name))['users']:

        # adding user in online list
        data = json.loads(redis_db.get(room_name))
        online = data['online']
        if session['_id'] not in online:
            online.append(session['_id'])
            data['online'] = online
            redis_db.set(room_name, json.dumps(data))

        # data from redis
        link = json.loads(redis_db.get(room_name))['playlist'][0]
        password = json.loads(redis_db.get(room_name))['password']
        online = json.loads(redis_db.get(room_name))['online']
        names = json.loads(redis_db.get(room_name))['names']

        session['current_room'] = room_name

        return render_template('room.html',
                               video_link=link,
                               source='youtube',
                               password=password,
                               room_name=room_name,
                               online=online,
                               names=names)
    else:
        return redirect(url_for('general.password_in', room_name=room_name))


@socketio.on('join_room')
def join_room(data):
    socket_join_room(data['room_name'])


@socketio.on('disconnect')
def online_disconnect():
    print("disconnect2")

    # getting room name
    room_name = session['current_room']

    # deleting user from online list
    room = json.loads(redis_db.get(room_name))

    online = room['online']

    online.remove(session['_id'])
    room['online'] = online
    redis_db.set(room_name, json.dumps(room))

    # deleting if room is empty
    if json.loads(redis_db.get(room_name))['online'] == []:
        print("deleting")

        # deleting room from socketio
        close_room(room_name)

        # deleting room from redis
        redis_db.delete(room_name)




@general.route("/password", methods=('GET', 'POST'))
def password_in():
    room_name = request.args.get('room_name')
    form = forms.password_form()

    error = None
    if form.validate_on_submit():
        if form.password.data == json.loads(redis_db.get(room_name))['password']:
            # seting username and checking if its already in
            if not form.name.data in (json.loads(redis_db.get(room_name))['names']).values():
                data = json.loads(redis_db.get(room_name))
                session['username'] = form.name.data
                names = data['names']
                names[session['_id']] = form.name.data
                data['names'] = names
                redis_db.set(room_name, json.dumps(data))
            else:
                # making error
                error = "*Name Is Taken"
                return redirect(url_for('general.password_in', room_name=room_name, error=error))

            # adding sid in users list
            data = json.loads(redis_db.get(room_name))
            users = data['users']
            users.append(session['_id'])
            data['users'] = users
            redis_db.set(room_name, json.dumps(data))

            return redirect(url_for('general.room', room_name=room_name))

        else:
            # making error
            error = "*Wrong Password"
            return redirect(url_for('general.password_in', room_name=room_name, error=error))

    return render_template("password.html", form=form)


@socketio.on('create_room')
def create_room(data):
    # generating random room name
    room_name = generate_room_name()

    # main room settings
    room = {
        'playlist': [data['videoLink']],
        'password': data['password'],
        'users': [session['_id']],
        'online': [],
        'names': {session['_id']: 'admin'}
    }

    redis_db.set(room_name, json.dumps(room))

    socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)}, room=request.sid)


@socketio.on('sayHi')
def say_hi(data):
    print(data)
    socketio.emit('displaySayHi', room=data['room'])


# making session id
@general.before_request
def add_sid():
    if '_id' not in session:
        session['_id'] = uuid.uuid1().hex
