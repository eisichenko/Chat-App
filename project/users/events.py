from project import socketio
from flask import request
from flask_login import current_user
from flask_socketio import join_room
from project.models import *


@socketio.on('connect')
def connect():
    if current_user.is_anonymous:
        return False
        
    print(f'connected: {current_user.username}')
    
    for chat in current_user.chats:
        join_room(str(chat.id))
        
    current_user.sid = request.sid
    current_user.last_activity = datetime.utcnow()
    db.session.commit()
    
    socketio.emit('setup connection', { }, room=request.sid)


@socketio.on('disconnect')
def disconnect():
    print(f'disconnected: {current_user.username}')
    
    current_user.sid = None
    db.session.commit()
