import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'qweqwe O_o 123321'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    DEBUG = False
    
    url = os.environ.get('CLEARDB_DATABASE_URL', None)
    if url:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql' + url[5:-15]
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@db/flask_app'


class DevelopmentConfig(Config):
    DEBUG = True

    SESSION_COOKIE_SECURE = False
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/flask_app'


class TestingConfig(Config):
    TESTING = True
    
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/test_flask_app'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:''@localhost/travis'

    SESSION_COOKIE_SECURE = False