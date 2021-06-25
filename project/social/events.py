from project import socketio
from flask import session
from flask_login import current_user
from project.models import *


@socketio.on('send message')
def send_message_event(json):
    if json['message'] == None or len(json['message']) == 0:
        return
    
    json['message'] = json['message'][:min(1000, len(json['message']))]
    
    if 'current_chat_id' in session.keys():
        chat_id=session['current_chat_id']
    else:
        return
    
    message = Message(text=json['message'], 
                        user=current_user, 
                        date=datetime.utcnow(), 
                        chat_id=chat_id)

    json['time'] = message.date.isoformat()
    json['sender_username'] = current_user.username
    json['chat_id'] = chat_id
    
    chat = Chat.query.get(chat_id)
    
    chat.messages.append(message)
    
    timestamp = Timestamp.query.filter_by(user_id=current_user.id, chat_id=chat_id).first()
    
    if timestamp == None:
        db.session.add(Timestamp(user=current_user, chat=chat, timestamp=datetime.utcnow()))
    else:
        timestamp.timestamp = datetime.utcnow()
    
    db.session.commit()
    
    json['message_id'] = message.id
    
    socketio.emit('update messages', json, room=str(chat_id), include_self=False)


@socketio.on('mark as read')
def read(json):
    if (json['sender_username'] != current_user.username):
        timestamp = Timestamp.query.filter_by(user_id=current_user.id, chat_id=json['chat_id']).first()
        
        if timestamp == None:
            db.session.add(Timestamp(user_id=current_user.id, chat_id=json['chat_id'], timestamp=datetime.utcnow()))
        else:
            timestamp.timestamp = datetime.utcnow()
        
        db.session.commit()
