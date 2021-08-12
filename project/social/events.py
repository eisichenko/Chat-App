from project import socketio
from flask import session, request
from flask_login import current_user
from project.models import *
import config
from contextlib import nullcontext
from sqlalchemy import func

if config.needs_redis():
    from project import high_queue, default_queue
    import app


def write_message_task(json, chat_id, user_id, sid):
    if config.needs_redis():
        app_context = app.app.app_context()
    else:
        app_context = nullcontext()
        
    with app_context:
        user = User.query.get(user_id)
        username = user.username
        
        message = Message(text=json['message'], 
                            user_id=user_id, 
                            date=datetime.utcnow(), 
                            chat_id=chat_id)

        json['time'] = message.date.isoformat()
        json['sender_username'] = username
        json['chat_id'] = chat_id
        
        chat = Chat.query.get(chat_id)
        
        chat.messages.append(message)
        
        timestamp = Timestamp.query.filter_by(user_id=user_id, chat_id=chat_id).first()
        
        if timestamp == None:
            db.session.add(Timestamp(user_id=user_id, chat_id=chat_id, timestamp=datetime.utcnow()))
        else:
            timestamp.timestamp = datetime.utcnow()
        
        user.last_activity = datetime.utcnow()

        db.session.commit()

        json['message_id'] = message.id
        
        if config.needs_redis():
            with app.app.test_request_context():
                request.sid = sid
                socketio.emit('update messages', json, room=str(chat_id), include_self=False)
        else:
            socketio.emit('update messages', json, room=str(chat_id), include_self=False)


@socketio.on('send message')
def send_message_event(json):
    if json['message'] == None or len(json['message']) == 0:
        return
    
    json['message'] = json['message'][:min(1000, len(json['message']))]
    
    if 'current_chat_id' in session.keys():
        chat_id=session['current_chat_id']
    else:
        return
    
    if config.needs_redis():
        default_queue.enqueue(write_message_task, json, chat_id, current_user.id, request.sid)
    else:
        write_message_task(json, chat_id, current_user.id, request.sid)


def mark_as_read_task(json, user_id):
    if config.needs_redis():
        app_context = app.app.app_context()
    else:
        app_context = nullcontext()
    
    with app_context:
        timestamp = Timestamp.query.filter_by(user_id=user_id, chat_id=json['chat_id']).first()
        if timestamp == None:
            db.session.add(Timestamp(user_id=user_id, chat_id=json['chat_id'], timestamp=datetime.utcnow()))
        else:
            timestamp.timestamp = datetime.utcnow()

        db.session.commit()


@socketio.on('mark as read')
def read(json):
    if (json['sender_username'] != current_user.username):
        if config.needs_redis():
            high_queue.enqueue(mark_as_read_task, json, current_user.id)
        else:
            mark_as_read_task(json, current_user.id)
            

def get_list_of_users_task(name, current_username):
    if config.needs_redis():
        app_context = app.app.app_context()
    else:
        app_context = nullcontext()
        
    with app_context:
        if len(name) == 0:
            users = User.query.filter(User.username != current_username).limit(10)
        else:
            users = User.query.filter(func.lower(User.username).startswith(func.lower(name)), User.username != current_username).limit(10)

        if config.needs_redis():
            with app.app.test_request_context():
                socketio.emit('update list of users', { 'users': [user.username for user in users] })
        else:
            socketio.emit('update list of users', { 'users': [user.username for user in users] })


@socketio.on('get list of users')
def get_list_of_users(json):
    name = json['name']
    if config.needs_redis():
        high_queue.enqueue(get_list_of_users_task, name, current_user.username)
    else:
        get_list_of_users_task(name, current_user.username)
