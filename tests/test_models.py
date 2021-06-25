from .conftest import *

def test_models_repr():
    user = User(id = 1, username='name', password='password')
    
    msg = Message(id = 1, text='some user message', 
                                 user=user, 
                                 date=datetime.now(), 
                                 chat_id=1)
    
    assert '<User(id = "1" username = "name")>' == repr(user)
    assert '<Message(id = "1")>' == repr(msg)
