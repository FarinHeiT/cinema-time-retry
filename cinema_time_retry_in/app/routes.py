import json

from flask import Flask, render_template, Blueprint, url_for,redirect, session, request

from cinema_time_retry_in import socketio, redis_db
from . import forms

from flask_socketio import join_room, SocketIO

from .helper_functions import generate_room_name

general = Blueprint('general', __name__)


@general.route('/')
def index():
    form = forms.name_form()
    if form.validate_on_submit():
        session['username'] = form.name.data
    return render_template("Main.html", form=form)


@general.route('/room/<room_name>')
def room(room_name):
    if request.sid in json.loads(redis_db.get(room_name))['users']:
        join_room(room_name)
        link = json.loads(redis_db.get(room_name))['playlist'][0]
        print(link)
        password = json.loads(redis_db.get(room_name))['password']
        return render_template('room.html', video_link=link, source='youtube', password=password)
    else:
        socketio.emit('redirect', {'url': url_for('general.password',room_name=room_name)})


@general.route("/password")
def password_in(room_name):
    if json.loads(redis_db.get(room_name))['password'] == '':
        users = json.loads(redis_db.get(room_name))['users']
        print(users)
        users.append(request.sid)
        print(users)
        data = {
            'playlist': [json.loads(redis_db.get(room_name))['playlist']],
            'password': json.loads(redis_db.get(room_name))['password'],
            'users': [json.loads(redis_db.get(room_name))['users']]
        }
        redis_db.set(room_name, json.dumps(data))
        return redirect(url_for('general.room', room_name=room_name))

    form = forms.password_form()
    if form.validate_on_submit():
        if form.password.data == json.loads(redis_db.get(room_name))['password']:
            users = json.loads(redis_db.get(room_name))['users']
            print(users)
            users.append(request.sid)
            print(users)
            data = {
                'playlist': [json.loads(redis_db.get(room_name))['playlist']],
                'password': json.loads(redis_db.get(room_name))['password'],
                'users': [json.loads(redis_db.get(room_name))['users']]
            }
            redis_db.set(room_name, json.dumps(data))
            return redirect(url_for('general.room', room_name=room_name))

        else:
            return redirect(url_for('password_in', room_name=room_name))
    return render_template("password.html", form=form)


@socketio.on('connection')
def connection(json):
    print('New user connected!' + str(json))


#@socketio.on("t_password")
#def type_in_password(data):
#    socketio.emit('redirect', {'url': url_for('general.password', data=data)})



@socketio.on('create_room')
def create_room(data):
    room_name = generate_room_name()

    room = {
        'playlist': [data['videoLink']],
        'password': data['password'],
        'users' : []
    }


    redis_db.set(room_name, json.dumps(room))
    socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)})


