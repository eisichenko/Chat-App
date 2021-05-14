from .conftest import *


def test_admin(flask_test_client):
    current_username = user_data[0][0]
    current_password = user_data[0][1]
    
    current_user = User.query.get(1)
    
    login(flask_test_client, current_username, current_password)
    
    response = flask_test_client.get('/admin', follow_redirects = True)
    
    assert response.status_code == 404, 'wrong user access'
    
    response = flask_test_client.get('/admin/user', follow_redirects = True)
    
    assert response.status_code == 404, 'wrong user access'
