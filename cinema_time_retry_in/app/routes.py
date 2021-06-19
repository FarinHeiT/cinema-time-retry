import json
import uuid
from flask import Flask, render_template, Blueprint, url_for, redirect, session, request, jsonify
from flask_socketio import join_room as socket_join_room
from flask_socketio import close_room

from cinema_time_retry_in import socketio, redis_db
from . import forms

from . import socket_ios

from flask_socketio import join_room, SocketIO

from .helper_functions import *

general = Blueprint('general', __name__)


@general.route('/', methods=('GET', 'POST'))
def index():
    print(session['_id'])
    keys = redis_db.keys()
    print(keys)

    if not keys == []:
        rooms = []
        for i in keys:
            room = json.loads(redis_db.get(i))
            name = room['room_name']
            rooms.append((name.encode(), i))
    else:
        rooms = keys

    return render_template("Main.html", rooms=rooms)


def add_online(room_name):
    """
    Adds user to the online list
    Code 200 - successfully added
    Code 0 - user is already on the list
    """
    room = json.loads(redis_db.get(room_name))
    online = room['online']
    if session['_id'] not in online:
        online.append(session['_id'])
        room['online'] = online

        redis_db.set(room_name, json.dumps(room))
        return 200
    return 0


@general.route('/room/<room_name>/ping_online')
def ping_online(room_name):
    """ Helper route for the frontend to receive pings """
    return jsonify(add_online(room_name))


@general.route('/room/<room_name>', methods=('GET', 'POST'))
def room(room_name):
    # Check whether the user is banned or requires admin role
    room = json.loads(redis_db.get(room_name))
    if session['_id'] in room['users']:

        # If the user is banned - redirect him to index
        if session['_id'] in room['baned']:
            return redirect(url_for('general.index'))

        # giving the creator admin rights
        if session['_id'] == room['creator']:
            room['admin'] = room['creator']

        # saving all that
        redis_db.set(room_name, json.dumps(room))

        # adding the user to online list
        add_online(room_name)

        # data from redis
        link = room['playlist'][room['current_video_index']]
        password = room['password']
        online = room['online']
        names = room['names']
        name = room['names'][session['_id']]
        session['current_room'] = room_name
        color = room['colors'][session['_id']]
        settings = room['settings']
        custom_room_name = room['room_name']
        role = None
        if session['_id'] == room['creator']:
            role = "Creator"
        elif session['_id'] == room['admin']:
            role = "Admin"
        else:
            role = "User"

        form = forms.Message_form()
        return render_template('room.html',
                               video_link=link,
                               source='youtube',
                               password=password,
                               room_name=room_name,
                               online=online,
                               names=names,
                               form=form,
                               name=name,
                               color=color,
                               role=role,
                               settings=settings,
                               current_video_index=room['current_video_index'],
                               playlist=room['playlist'],
                               playlist_titles=room['playlist_titles'],
                               custom_room_name=custom_room_name)
    else:
        return redirect(url_for('general.password_in', room_name=room_name))


@general.route("/password", methods=('GET', 'POST'))
def password_in():
    room_name = request.args.get('room_name')
    form = forms.Password_form()

    if form.validate_on_submit():
        # global room variable for seting add geting
        room = json.loads(redis_db.get(str(room_name)))

        # checking password
        if form.password.data == room['password']:
            # adding sid in users list
            users = room['users']
            users.append(session['_id'])
            room['users'] = users
            redis_db.set(room_name, json.dumps(room))
        else:
            # making error
            form.password.errors.append("Wrong Password")
            # return redirect(url_for('general.password_in', room_name=room_name))

        # seting username and checking if its already in
        if form.password.data == room['password']:
            if not form.name.data in (room['names']).values():
                session['username'] = form.name.data
                names = room['names']
                names[session['_id']] = form.name.data
                room['names'] = names

                colors = room['colors']
                colors[session['_id']] = random_color()
                room['colors'] = colors

                redis_db.set(room_name, json.dumps(room))

                return redirect(url_for('general.room', room_name=room_name))
            else:
                form.name.errors.append("Name is Taken")

    password_check = '' if json.loads(redis_db.get(room_name))['password'] == '' else None
    return render_template("password.html", form=form, password_check=password_check)


@general.route('/get_rooms_data')
def get_rooms_data():
    keys = redis_db.keys()

    if not keys == []:
        rooms = []
        for i in keys:
            room = json.loads(redis_db.get(i))
            name = f'<a href="/room/{i.decode()}">{room["room_name"]}</a>'
            users = len(room["users"])
            privacy = False if room["password"] == "" else True
            current_video = room['playlist_titles'][room['current_video_index']]
            rooms.append([name, users, privacy, current_video])
    else:
        rooms = keys

    return json.dumps({'data': rooms})


# making session id
@general.before_request
def add_sid():
    if '_id' not in session:
        session['_id'] = uuid.uuid1().hex
