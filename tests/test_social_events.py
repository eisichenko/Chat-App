from .conftest import *
import random
import config
import tests.emoji_generator as emoji_generator
import tests.unicode_generator as unicode_generator


def test_send_read_messages():
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    other_username = user_data[1][0]
    other_password = user_data[1][1]
    
    current_user_id = 1
    other_user_id = 2
    
    with test_app.app_context():
        
        flask_test_client1 = test_app.test_client()
        flask_test_client2 = test_app.test_client()
        
        current_chat_user = User.query.get(current_user_id)
        other_chat_user = User.query.get(other_user_id)
        
        login(flask_test_client1, current_username, current_password)
        login(flask_test_client2, other_username, other_password)
        
        response = flask_test_client1.get('/start-chat/' + str(other_chat_user.id), follow_redirects=True)
        assert response.status_code == 200
        
        response = flask_test_client2.get('/messages/chat/' + str(other_chat_user.id), follow_redirects=True)
        assert response.status_code == 200
        
        chat = current_chat_user.chats[0]
        
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
            
        with flask_test_client2.session_transaction() as s:
            s['current_chat_id'] = chat_id

        socketio_test_client1 = socketio.test_client(test_app, flask_test_client=flask_test_client1)
        socketio_test_client2 = socketio.test_client(test_app, flask_test_client=flask_test_client2)
                
        socketio_test_client1.get_received()
        socketio_test_client2.get_received()
        
        current_user_messages = ([config.random_string() for _ in range(3)] + 
                                 [emoji_generator.random_emoji_string() for _ in range(3)] + 
                                 [unicode_generator.random_unicode_string() for _ in range(3)] +
                                 [config.random_string(1000), 
                                  emoji_generator.random_emoji_string(1000), 
                                  unicode_generator.random_unicode_string(1000),
                                  'F'])
        
        other_user_messages = ([config.random_string() for _ in range(3)] + 
                                 [emoji_generator.random_emoji_string() for _ in range(3)] + 
                                 [unicode_generator.random_unicode_string() for _ in range(3)] +
                                 [config.random_string(1000), 
                                  emoji_generator.random_emoji_string(1000), 
                                  unicode_generator.random_unicode_string(1000),
                                  'F'])
        
        all_messages = current_user_messages + other_user_messages
        
        index = 1
        
        while len(all_messages) > 0:
            message = random.choice(all_messages)
            
            all_messages.remove(message)
            
            if len(current_user_messages) > 0 and message in current_user_messages:
                name = current_username
                socketio_test_client1.emit('send message', { 'message': message })
                result = socketio_test_client2.get_received()
            else:
                name = other_username
                socketio_test_client2.emit('send message', { 'message': message })
                result = socketio_test_client1.get_received()
            
            assert socketio_test_client1.is_connected()
            assert socketio_test_client2.is_connected()
            assert result[0]['name'] == 'update messages'
            assert result[0]['args'][0]['message'] == message
            assert result[0]['args'][0]['sender_username'] == name
            assert result[0]['args'][0]['chat_id'] == 1
            assert result[0]['args'][0]['message_id'] == index
            index += 1
            
        large_messages = ['F' * 1001, 
                          '6' * 10_000, 
                          unicode_generator.random_unicode_string(10_000)]
        
        for message in large_messages:
            name = current_username
            socketio_test_client1.emit('send message', { 'message': message })
            result = socketio_test_client2.get_received()
            
            assert socketio_test_client1.is_connected()
            assert socketio_test_client2.is_connected()
            assert result[0]['name'] == 'update messages'
            assert result[0]['args'][0]['message'] != message
            assert len(result[0]['args'][0]['message']) != len(message)
            assert result[0]['args'][0]['sender_username'] == name
            assert result[0]['args'][0]['chat_id'] == 1
            assert result[0]['args'][0]['message_id'] == index
            index += 1
        
        logout(flask_test_client1)
        logout(flask_test_client2)
