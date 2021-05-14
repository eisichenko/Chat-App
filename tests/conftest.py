import pytest
from .data import *
from project import *
from project.models import *


test_app = create_app("config.TestingConfig")
test_app.app_context().push()


@pytest.fixture(scope='session', autouse=True)
def init_db():
    db.drop_all()
    db.create_all()
        
    for data in user_data:
        new_test_user = User(username=data[0], password=data[1])
        db.session.add(new_test_user)

    db.session.commit()


@pytest.fixture()
def flask_test_client():
    with test_app.test_client() as test_client:
        with test_app.app_context():
            yield test_client


@pytest.fixture()
def socketio_test_client(flask_test_client):
    with test_app.app_context():
        yield socketio.test_client(test_app, flask_test_client=flask_test_client)


def signup(flask_test_client, username, password):
    return flask_test_client.post('/signup', data={'username': username,
                                        'password': password}, 
                       follow_redirects=True)


def login(flask_test_client, username, password):
    return flask_test_client.post('/login', data={'username': username,
                                       'password': password}, 
                       follow_redirects=True)


def logout(flask_test_client):
    return flask_test_client.get('/logout', follow_redirects=True)
