from .conftest import *


def test_disconnect(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.get(1)
    
    login(flask_test_client, current_username, current_password)
    
    socketio_test_client = socketio.test_client(test_app, flask_test_client=flask_test_client)
    
    current_user = User.query.get(1)
    
    assert socketio_test_client.is_connected()
    assert current_user.sid != None
    
    socketio_test_client.emit('disconnect')
    
    current_user = User.query.get(1)
    
    assert current_user.sid == None
    
    logout(flask_test_client)
    
    
def test_join_room():
    flask_test_client1 = test_app.test_client()
    flask_test_client2 = test_app.test_client()
    flask_test_client3 = test_app.test_client()
    
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    other_username = user_data[1][0]
    other_password = user_data[1][1]
    
    user3_username = user_data[2][0]
    user3_password = user_data[2][1]
    
    current_user = User.query.get(1)
    other_user = User.query.get(2)
    
    login(flask_test_client1, current_username, current_password)
    login(flask_test_client2, other_username, other_password)
    login(flask_test_client3, user3_username, user3_password)
    
    response = flask_test_client1.get('/start-chat/' + str(other_user.id), follow_redirects=True)
    
    assert response.status_code == 200
    
    chat = current_user.chats[0]
    
    chat_id = chat.id
    
    json={'chat_id': chat.id, 'user1_sid': current_user.sid, 'user2_sid':other_user.sid}
    
    socketio_test_client1 = socketio.test_client(test_app, flask_test_client=flask_test_client1)
    socketio_test_client2 = socketio.test_client(test_app, flask_test_client=flask_test_client2)
    socketio_test_client3 = socketio.test_client(test_app, flask_test_client=flask_test_client3)
    
    socketio_test_client1.get_received()
    socketio_test_client2.get_received()
    socketio_test_client3.get_received()
    
    socketio_test_client1.emit('join', json)
    
    socketio_test_client1.emit('send message', { 'message': 'some message for room' }, room=str(chat_id))
    
    room_result = socketio_test_client2.get_received()
    
    not_room_result = socketio_test_client3.get_received()
    
    assert room_result[0]['args'][0]['message'] == 'some message for room'
    assert len(not_room_result) == 0
    
    logout(flask_test_client1)
    logout(flask_test_client2)
    logout(flask_test_client3)
