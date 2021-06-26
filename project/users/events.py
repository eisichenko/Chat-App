from project import socketio
from flask import request
from flask_login import current_user
from flask_socketio import join_room
from project.models import *
import config


@socketio.on('join')
def join(json):
    join_room(str(json['chat_id']), sid=json['user1_sid'])
    join_room(str(json['chat_id']), sid=json['user2_sid'])


@socketio.on('connect')
def connect():
    with config.db_semaphore:
        if current_user.is_anonymous:
            return False
            
        print(f'connected: {current_user.username}')
        
        for chat in current_user.chats:
            join_room(str(chat.id))
            
        current_user.sid = request.sid
        db.session.commit()
        
        socketio.emit('setup connection', { }, room=request.sid)

@socketio.on('disconnect')
def disconnect():
    with config.db_semaphore:
        print(f'disconnected: {current_user.username}')
        
        current_user.sid = None
        db.session.commit()
