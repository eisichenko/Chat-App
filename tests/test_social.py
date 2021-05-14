from .conftest import *


@pytest.mark.parametrize('username, password', user_data)
def test_home_page(flask_test_client, socketio_test_client, username, password):
    
    assert not socketio_test_client.is_connected(), 'anonymous user is connected'
    
    login(flask_test_client, username, password)
    
    response = flask_test_client.get('/')
    
    assert response.status_code == 200, 'wrong status code'
    assert b'Home page' in response.data, 'wrong page'
    
    response = flask_test_client.post('/', data={'search_field': username})
    
    assert response.status_code == 302, 'no redirect'
    
    for name in existing_names:
        if name != username:
            response = flask_test_client.post('/', data={'search_field': name})
            assert response.status_code == 200
            assert name.encode('utf-8') in response.data
            
    for user in non_existent_user_data:
        response = flask_test_client.post('/', data={'search_field': user[0]})
        assert response.status_code == 200
        assert b'No user was found :(' in response.data
        
    logout(flask_test_client)


def test_add_friends(flask_test_client):
    
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.filter_by(username=current_username).first()
    
    login(flask_test_client, current_username, current_password)
    
    response = flask_test_client.get('/friends')
    
    assert len(current_user.friends) == 0
    assert response.status_code == 200
    assert b'Oh no, you have no friends :(' in response.data
    
    friend_number = 0
    
    for data in user_data:
        user = User.query.filter_by(username=data[0]).first()
        
        response = flask_test_client.get('/add-friend/' + str(user.id))
        
        if data[0] == current_username:
            assert len(current_user.friends) == 0
            assert response.status_code == 302
            assert b'<a href="/">/</a>' in response.data
        else:
            friend_number += 1
            assert len(current_user.friends) == friend_number
            assert response.status_code == 200
            assert data[0].encode('utf-8') in response.data
            assert len(user.friends) == 1
    
    logout(flask_test_client)
    
    
def test_invalid_friends(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.filter_by(username=current_username).first()
    
    login(flask_test_client, current_username, current_password)
    
    friend_number = len(current_user.friends)    
    
    for id in range(1000, 100000, 30123):
        response = flask_test_client.get('/add-friend/' + str(id))
        assert response.status_code == 302
        assert b'<a href="/friends">/friends</a>' in response.data
        assert len(current_user.friends) == friend_number
        
    logout(flask_test_client)


def test_remove_friends(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.filter_by(username=current_username).first()
    
    login(flask_test_client, current_username, current_password)
    
    friend_number = len(current_user.friends)  
    
    response = flask_test_client.get('/remove-friend/' + str(current_user.id))
    
    assert response.status_code == 302
    assert b'<a href="/">/</a>' in response.data
    assert friend_number == len(current_user.friends) 
    
    response = flask_test_client.get('/remove-friend/123123')
    assert response.status_code == 302
    assert friend_number == len(current_user.friends)
    
    for user in current_user.friends:
        response = flask_test_client.get('/remove-friend/' + str(user.id))
        assert len(user.friends) == 0
        assert len(current_user.friends) == friend_number - 1
        friend_number -= 1
        assert response.status_code == 200

    logout(flask_test_client)


def test_start_chat(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.filter_by(username=current_username).first()
    
    login(flask_test_client, current_username, current_password)
    
    chat_number = len(current_user.chats)
    
    response = flask_test_client.get('/start-chat/123123')
    assert response.status_code == 302
    assert chat_number == 0
    
    for data in user_data[1:]:
        user = User.query.filter_by(username=data[0]).first()
        
        response = flask_test_client.get('/start-chat/' + str(user.id))
        assert response.status_code == 302
        assert chat_number + 1 == len(current_user.chats)
        chat_number += 1
        assert len(user.chats) == 1
        
    response = flask_test_client.get('/start-chat/2')
    assert response.status_code == 302
    assert chat_number == len(current_user.chats)
    
    logout(flask_test_client)


def test_messages(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.filter_by(username=current_username).first()
    
    login(flask_test_client, current_username, current_password)
    
    response = flask_test_client.get('/messages')
    assert response.status_code == 200
    
    logout(flask_test_client)


def test_chat(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.filter_by(username=current_username).first()
    other_user = User.query.get(2)
    
    login(flask_test_client, current_username, current_password)
    
    response = flask_test_client.get('/messages/chat/123123')
    assert response.status_code == 302
    
    chat = current_user.chats[0]
    
    chat.unread_messages_number = 123
    db.session.commit()
    
    response = flask_test_client.get('/messages/chat/' + str(chat.id))
    assert response.status_code == 200
    
    other_user_msg = Message(text='some message', 
                                 user=other_user, 
                                 date=datetime.now(), 
                                 chat_id=chat.id, 
                                 unread=True)
    
    current_user_msg = Message(text='some user message', 
                                 user=current_user, 
                                 date=datetime.now(), 
                                 chat_id=chat.id, 
                                 unread=True)
    
    chat.messages.append(other_user_msg)
    chat.unread_messages_number = 1
    db.session.commit()
    
    response = flask_test_client.get('/messages/chat/' + str(chat.id))
    assert not other_user_msg.unread
    assert response.status_code == 200
    assert b'Unread Messages' in response.data
    
    chat.messages.append(current_user_msg)
    chat.unread_messages_number = 1
    db.session.commit()
    response = flask_test_client.get('/messages/chat/' + str(chat.id))
    assert response.status_code == 200
    assert not b'Unread Messages' in response.data
    
    logout(flask_test_client)
