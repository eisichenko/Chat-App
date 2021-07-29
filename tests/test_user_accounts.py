from .conftest import *


@pytest.mark.parametrize('username, password', user_data)
def test_existing_user_login(flask_test_client, socketio_test_client, username, password):
    assert not socketio_test_client.is_connected(), 'anonymous user is connected'
    
    response = flask_test_client.get('/login')
    
    assert response.status_code == 200, 'wrong status code'
    assert b'LOGIN' in response.data, 'wrong page'
    
    print('aahahah')
    
    response = flask_test_client.post('/login', data={'username': username,
                                                     'password': password})
    
    assert response.status_code == 302, 'no redirect'
    assert b'<a href="/">/</a>' in response.data and b'Redirecting...' in response.data, 'wrong page'
    

@pytest.mark.parametrize('username, password', non_existent_user_data)
def test_not_existing_user_login(flask_test_client, socketio_test_client, username, password):
    response = flask_test_client.post('/login', data={'username': username,
                                                     'password': password})
    
    assert response.status_code == 200, 'wrong status code'
    assert b'LOGIN' in response.data, 'wrong page'
    

@pytest.mark.parametrize('username, password', invalid_user_data)
def test_invalid_user_login(flask_test_client, username, password):
    response = flask_test_client.post('/login', data={'username': username,
                                                     'password': password})
    
    assert response.status_code == 200, 'wrong status code'
    assert b'Invalid username or password' in response.data, 'wrong page'
    

@pytest.mark.parametrize('message, span_class', [('msg', 'span'), ('ahahah', 'lol'), ('nooo', '$$$$')])
def test_session_login(flask_test_client, message, span_class):
    with flask_test_client.session_transaction() as s:
        s['message'] = message
        s['span_class'] = span_class
        
    response = flask_test_client.get('/login')
    
    with flask_test_client.session_transaction() as s:
        assert not 'message' in s.keys()
        assert not 'span_class' in s.keys()
        
    assert message.encode('utf-8') in response.data
    assert span_class.encode('utf-8') in response.data


@pytest.mark.parametrize('username, password', non_existent_user_data)
def test_signup(flask_test_client, username, password):
    response = flask_test_client.get('/signup')
    
    assert response.status_code == 200, 'wrong status code'
    assert b'Sign Up' in response.data, 'wrong page'
    
    response = flask_test_client.post('/signup', data={'username': username,
                                                     'password': password})
    
    assert response.status_code == 302, 'no redirect'
    assert b'<a href="/login">/login</a>' in response.data and b'Redirecting...' in response.data, 'wrong page'


@pytest.mark.parametrize('username, password', user_data)
def test_duplicate_signup(flask_test_client, username, password):
    response = flask_test_client.post('/signup', data={'username': username,
                                                     'password': password})
    
    assert response.status_code == 200, 'wrong status code'
    assert b'Username already exists' in response.data


@pytest.mark.parametrize('username, password', invalid_user_data)
def test_invalid_user_signup(flask_test_client, username, password):
    response = flask_test_client.post('/signup', data={'username': username,
                                                     'password': password})
    
    assert response.status_code == 200, 'wrong status code'
    assert b'Invalid username or password' in response.data, 'wrong page' and b'Sign Up' in response.data


@pytest.mark.parametrize('username, password', user_data)
def test_logout(flask_test_client, username, password):
    login(flask_test_client, username, password)
    
    response = flask_test_client.get('/logout')
    
    assert response.status_code == 302, 'no redirect'
    assert b'<a href="/login">/login</a>' in response.data


@pytest.mark.parametrize('username, password', user_data)
def test_profile(flask_test_client, username, password):
    login(flask_test_client, username, password)
    
    response = flask_test_client.get('/my-profile')
    
    assert response.status_code == 200
    assert username.encode('utf-8') in response.data
    
    temp = username

    response = flask_test_client.post('/my-profile', data={'username': 'SoMe_NaMe%$'}, 
                                      follow_redirects = True)
    
    assert response.status_code == 200
    assert b'SoMe_NaMe%$' in response.data
    
    response = flask_test_client.post('/my-profile', data={'username': temp}, 
                                      follow_redirects = True)
    
    assert response.status_code == 200
    assert temp.encode('utf-8') in response.data
    

@pytest.mark.parametrize('new_name', invalid_names)
def test_invalid_rename(flask_test_client, new_name):
    login(flask_test_client, user_data[0][0], user_data[0][1])
    
    response = flask_test_client.get('/my-profile')
    
    
    response = flask_test_client.post('/my-profile', data={'username': new_name}, 
                                      follow_redirects = True)
    
    assert response.status_code == 200
    assert b'Invalid username' in response.data
    

@pytest.mark.parametrize('new_name', existing_names)
def test_existing_rename(flask_test_client, new_name):
    login(flask_test_client, user_data[0][0], user_data[0][1])
    
    response = flask_test_client.get('/my-profile')
    
    
    response = flask_test_client.post('/my-profile', data={'username': new_name}, 
                                      follow_redirects = True)
    
    assert response.status_code == 200
    assert b'Username already exists' in response.data
    
    
@pytest.mark.parametrize('username, password', users_to_delete[:1])
def test_deleting_users(flask_test_client, username, password):
    signup(flask_test_client, username, password)
    login(flask_test_client, username, password)
    
    response = flask_test_client.get('/delete', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'LOGIN' in response.data
    assert User.query.filter_by(username=username).first() == None, "not deleted"
