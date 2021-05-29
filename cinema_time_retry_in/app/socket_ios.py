import json
import threading
import time
import uuid
import re
from flask import Flask, render_template, Blueprint, url_for, redirect, session, request, escape, jsonify
from flask_socketio import join_room as socket_join_room
from flask_socketio import close_room

from cinema_time_retry_in import socketio, redis_db
from . import forms

from flask_socketio import join_room, SocketIO

from .helper_functions import generate_room_name

@socketio.on('join_room')
def join_room(data):
    socket_join_room(data['room_name'])


def check_for_deletion(current_room, id):
    """ Waits for a 5 seconds for user to reconnect and if user fails - deletes the room """
    time.sleep(5)

    room_name = current_room
    room = json.loads(redis_db.get(str(room_name)))

    # deleting if room is empty
    if room['online'] == []:
        print(f"deleting {room_name}")

        # deleting room from redis
        redis_db.delete(room_name)

        return

    print('Deletion denied, someone is online.')

    # trnsfer admin to another user when admin leaves
    if id == room['admin']:
        room['admin'] = room['online'][0]

@socketio.on('disconnect')
def online_disconnect():
    print("Someone left, deleting from online users")

    # getting room name
    room_name = session['current_room']

    # deleting user from online list
    room = json.loads(redis_db.get(str(room_name)))

    online = room['online']
    if session['_id'] in online:
        online.remove(session['_id'])
        room['online'] = online

        # save the new online data
        redis_db.set(room_name, json.dumps(room))

    # check for a reconnection in 5 seconds
    threading.Thread(target=check_for_deletion, args=(session["current_room"], session["_id"])).start()
    print('Room deletion test initialized in 5 seconds...')

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

    # remove Sid from online users
    users = room['online']
    users.remove(target_user_sid)
    room['online'] = users

    # saving all above
    redis_db.set(roomname, json.dumps(room))

    print('user banned')

    
@socketio.on('create_room')
def create_room(data):
    # generating random room name
    room_name = generate_room_name()

    raw_link = re.search(r"(?<=https:\/\/www\.youtube\.com\/watch\?v=).+$", data['videoLink'])

    if raw_link:
        data['videoLink'] = raw_link.group()
        print(data['videoLink'])

        # main room settings
        room = {
            'playlist': [escape(data['videoLink'])],
            'password': escape(data['password']),
            'users': [session['_id']],
            'online': [],
            'names': {session['_id']: escape(data['Name'])},
            'baned': [],
            'admin': session['_id'],
            'creator': session['_id'],
            'room_name': room_name,
            'colors': {session['_id'] : "FFFF00"},
            'settings': {
                'admin_rules': True
            },
            'current_video_index': 0

        }

        redis_db.set(room_name, json.dumps(room))

        socketio.emit('redirect', {'url': url_for('general.room', room_name=room_name)}, room=request.sid)
    else:
        socketio.emit("error", {"title": "Invalid Link", "content": "Link to the video has to be from youtube"})


@socketio.on('player_state_handle')
def player_state_handle(data):
    player_state = data['action']

    # TODO Check if the request was sent by admin or whether checkbox "all users can modify player state was checked

    if player_state == 'play':
        socketio.emit('send_unpause', {'current_time': data['current_time'], 'initiator': data['username']}, room=data['room'])
    elif player_state == 'pause':
        socketio.emit('send_pause', {'current_time': data['current_time'], 'initiator': data['username']}, room=data['room'])
    else:
        raise Exception('Unhandled state detected:', player_state)


@socketio.on('playlist_handle')
def playlist_handle(data):
    room_name = data['room_name']
    room = json.loads(redis_db.get(room_name))
    action = data['action']

    try:
        # TODO Server-side validation of the provided link
        video_id = data['link'].split('watch?v=')[-1]

        if action == 'clear_playlist':
            room['playlist'] = []
            response = "Successfully cleared the playlist"
        elif action == 'add_video':
            if video_id not in room['playlist']:
                room['playlist'].append(escape(video_id))
                print(f'Successfully added video to playlist')
                response = "Successfully added video"
            else:
                response = "This video is already in playlist"
        elif action == 'remove_video':
            if video_id in room['playlist']:
                room['playlist'].remove(video_id)
                response = "Successfully removed video"
            else:
                response = "There is no such video in playlist"


        redis_db.set(room_name, json.dumps(room))
        socketio.emit('send_playlist_handled', {'response': response, 'playlist': room['playlist']}, room=data['room_name'])

    except Exception as e:
        print(e)


@socketio.on('change_video')
def change_video(data):
    room_name = data['room_name']
    room = json.loads(redis_db.get(room_name))
    room['current_video_index'] = data['next_video_index']
    redis_db.set(room_name, json.dumps(room))
    print(f"Current Video updated for room: {room_name}")
    print(data)
    socketio.emit('send_change_video', {'current_video_index': data['next_video_index']}, room=data['room_name'])


@socketio.on('new_room_name')
def new_room_name(data):
    # getting all data we need
    room_name = data['room_name']
    new_name = escape(data['name'])
    room = json.loads(redis_db.get(room_name))

    # changing name in radis
    room['room_name'] = new_name
    redis_db.set(room_name, json.dumps(room))

    print(f"new room name {new_name}")


@socketio.on('change_settings')
def change_settings(data):
    room_name = data['room_name']
    room = json.loads(redis_db.get(room_name))

    try:
        room['settings'][data['parameter']] = data['value']
        redis_db.set(room_name, json.dumps(room))
        print(f'Successfully changed parameter "{data["parameter"]}" to "{data["value"]}"')

        socketio.emit("send_new_settings", room['settings'])

    except Exception as e:
        print("Error while changing settigs: ", e)


@socketio.on('get_room_info')
def get_room_info(data):
    try:
        print(data)
        room_name = data['room_name']
        room = json.loads(redis_db.get(room_name))
        socketio.emit('send_room_info', {"room_info": room, "timing": data["timing"]}, room=room_name)
    except Exception as e:
        print("Error while trying to find room: ", room_name, e)

@socketio.on("message")
def handleMessage(msg):
    msg['msg'] = escape(msg["msg"])
    print(msg["msg"])
    socketio.emit("get_message", msg, broadcast=True)

@socketio.on("get_rooms_data")
def handleRoomsData():
    keys = redis_db.keys()

    if not keys == []:
        rooms = []
        for i in keys:
            room = json.loads(redis_db.get(i))
            name = room['room_name']
            rooms.append([name, i.decode()])
    else:
        rooms = keys

    socketio.emit("new_room_data", json.dumps(rooms))
