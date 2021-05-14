from .conftest import *


def test_send_message(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.get(1)
    other_user = User.query.get(2)
    
    login(flask_test_client, current_username, current_password)
    
    response = flask_test_client.get('/start-chat/' + str(other_user.id), follow_redirects=True)
    
    assert response.status_code == 200
    
    chat = current_user.chats[0]
    
    chat_id = chat.id
    
    with flask_test_client.session_transaction() as s:
        s.pop('current_chat_id')

    json = {'message': 'some message'}
    
    socketio_test_client = socketio.test_client(test_app, flask_test_client=flask_test_client)
    
    socketio_test_client.emit('send message', json)
    
    result = socketio_test_client.get_received()
        
    assert len(result) == 0
    
    with flask_test_client.session_transaction() as s:
        s['current_chat_id'] = chat_id

    json = {'message': 'some message'}
    
    socketio_test_client = socketio.test_client(test_app, flask_test_client=flask_test_client)
    
    socketio_test_client.emit('send message', json)
    
    result = socketio_test_client.get_received()
        
    assert socketio_test_client.is_connected()
    assert result[0]['name'] == 'update messages'
    assert result[0]['args'][0]['message'] == 'some message'
    assert result[0]['args'][0]['username'] == 'David'
    assert result[0]['args'][0]['chat_id'] == 1
    assert result[0]['args'][0]['current_unread'] == 1
    assert result[0]['args'][0]['message_id'] == 1
    
    logout(flask_test_client)


def test_read(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.get(1)
    other_user = User.query.get(2)
    
    login(flask_test_client, current_username, current_password)
    
    json = {}
    
    json['username'] = other_user.username
    json['chat_id'] = 1
    json['message_id'] = 1
    
    socketio_test_client = socketio.test_client(test_app, flask_test_client=flask_test_client)
    
    message = Message.query.get(1)
    chat = Chat.query.get(1)
    
    assert message.unread
    assert chat.unread_messages_number == 1
    
    socketio_test_client.emit('read', json)
    
    message = Message.query.get(1)
    chat = Chat.query.get(1)
    
    assert not message.unread
    assert chat.unread_messages_number == 0
    
    logout(flask_test_client)
