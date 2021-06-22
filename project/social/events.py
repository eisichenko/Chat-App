from project import socketio
from flask import session
from flask_login import current_user
from project.models import *
import concurrent.futures


@socketio.on('send message')
def send_message_event(json):
    if json['message'] == None or len(json['message']) == 0:
        return
    
    json['message'] = json['message'][:min(1000, len(json['message']))]
    
    print('received data: ' + str(json))
    
    if 'current_chat_id' in session.keys():
        chat_id=session['current_chat_id']
    else:
        return
    
    message = Message(text=json['message'], 
                        user=current_user, 
                        date=datetime.now(), 
                        chat_id=chat_id, 
                        unread=True)

    json['time'] = message.date.strftime("%d/%m/%Y %H:%M:%S")
    json['username'] = current_user.username
    json['chat_id'] = chat_id
    
    chat = Chat.query.get(chat_id)
    
    chat.messages.append(message)
    chat.unread_messages_number += 1
    
    db.session.commit()
    
    json['current_unread'] = chat.unread_messages_number
    json['message_id'] = message.id
    
    socketio.emit('update messages', json, room=str(chat_id), include_self=False)


@socketio.on('read')
def read(json):
    try:
        if (json['username'] != current_user.username):
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                chat_future = executor.submit(Chat.query.get, json['chat_id'])
                message_future = executor.submit(Message.query.get, json['message_id'])
                
                chat = chat_future.result()
                message = message_future.result()
            
            message.unread = False
            
            chat.unread_messages_number -= 1
            
            db.session.commit()
    except:
        pass
