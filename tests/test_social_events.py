from .conftest import *


def test_send_message():
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    other_username = user_data[1][0]
    other_password = user_data[1][1]
    
    flask_test_client1 = test_app.test_client()
    flask_test_client2 = test_app.test_client()
    
    current_user = User.query.get(1)
    other_user = User.query.get(2)
    
    login(flask_test_client1, current_username, current_password)
    login(flask_test_client2, other_username, other_password)
    
    response = flask_test_client1.get('/start-chat/' + str(other_user.id), follow_redirects=True)
    
    assert response.status_code == 200
    
    chat = current_user.chats[0]
    
    chat_id = chat.id
    
    with flask_test_client1.session_transaction() as s:
        s.pop('current_chat_id')

    json = {'message': 'some message'}
    
    socketio_test_client1 = socketio.test_client(test_app, flask_test_client=flask_test_client1)
    socketio_test_client2 = socketio.test_client(test_app, flask_test_client=flask_test_client2)
    
    socketio_test_client1.get_received()
    socketio_test_client2.get_received()
    
    socketio_test_client1.emit('send message', json)
    
    result = socketio_test_client2.get_received()
        
    assert len(result) == 0
    
    with flask_test_client1.session_transaction() as s:
        s['current_chat_id'] = chat_id

    json = {'message': 'some message'}
    
    socketio_test_client1 = socketio.test_client(test_app, flask_test_client=flask_test_client1)
    socketio_test_client2 = socketio.test_client(test_app, flask_test_client=flask_test_client2)
    
    socketio_test_client1.get_received()
    socketio_test_client2.get_received()
    
    socketio_test_client1.emit('send message', json)
    
    result = socketio_test_client2.get_received()
    
    print(result)
        
    assert socketio_test_client1.is_connected()
    assert socketio_test_client2.is_connected()
    assert result[0]['name'] == 'update messages'
    assert result[0]['args'][0]['message'] == 'some message'
    assert result[0]['args'][0]['username'] == 'David'
    assert result[0]['args'][0]['chat_id'] == 1
    assert result[0]['args'][0]['current_unread'] == 1
    assert result[0]['args'][0]['message_id'] == 1
    
    logout(flask_test_client1)
    logout(flask_test_client2)


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
