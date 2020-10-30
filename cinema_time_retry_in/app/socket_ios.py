import json
import uuid
from flask import Flask, render_template, Blueprint, url_for, redirect, session, request
from flask_socketio import join_room as socket_join_room
from flask_socketio import close_room

from cinema_time_retry_in import socketio, redis_db
from . import forms

from flask_socketio import join_room, SocketIO

from .helper_functions import generate_room_name


@socketio.on('join_room')
def join_room(data):
    socket_join_room(data['room_name'])


@socketio.on('disconnect')
def online_disconnect():
    print("disconnect2")

    # getting room name
    room_name = session['current_room']

    # deleting user from online list
    room = json.loads(redis_db.get(str(room_name)))

    online = room['online']

    online.remove(session['_id'])
    room['online'] = online

    # deleting if room is empty
    if room['online'] == []:
        print(f"deleting {room_name}")

        # deleting room from socketio
        close_room(room_name)

        # deleting room from redis
        redis_db.delete(room_name)

        return



    # trnsfer admin to another user when admin leaves
    if session["_id"] == room['admin']:
        room['admin'] = room['online'][0]

    # saving all this crazy stuff
    redis_db.set(room_name, json.dumps(room))


@socketio.on("ban")
def ban_user(data):
    print('got ban')
    # getting room name
    roomname = session['current_room']
    room = json.loads(redis_db.get(roomname))

    # Username to ban
    target_user = data['user']

    # Get the SID of the user
    target_user_sid = list(room['names'].keys())[list(room['names'].values()).index(target_user)]


    # adding Sid To banned
    baned = room['baned']
    baned.append(target_user_sid)
    room['baned'] = baned

    # remove Sid from users
    users = room['users']
    users.remove(target_user_sid)
    room['users'] = users

    # saving all above
    redis_db.set(roomname, json.dumps(room))

    print('user banned')


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
        'names': {session['_id']: data['Name']},
        'baned': [],
        'admin': session['_id'],
        'creator': session['_id'],
        'room_name': room_name


    }

    redis_db.set(room_name, json.dumps(room))

    socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)}, room=request.sid)


@socketio.on('sayHi')
def say_hi(data):
    print(data)
    socketio.emit('displaySayHi', room=data['room'])

@socketio.on('new_room_name')
def new_room_name(data):
    # getting all data we need
    room_name = data['room_name']
    new_name = data['name']
    room = json.loads(redis_db.get(room_name))

    # changing name in radis
    room['room_name'] = new_name
    redis_db.set(room_name, json.dumps(room))

    # changing name in session
    print(f"new room name {new_name}")

