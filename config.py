import os
import random
import string


def random_string(n=random.randint(100, 150)):
    symbols = string.digits + string.ascii_letters + string.punctuation + ' '
    return ''.join(random.choice(symbols) for _ in range(n))


def get_config_string():
    if ENV == HEROKU_ENV:
        return 'config.ProductionConfig'
    elif ENV == LOCAL_ENV or ENV == DOCKER_ENV:
        return 'config.DevelopmentConfig'
    raise ValueError('No configuration')


LOCAL_ENV = 'local'
HEROKU_ENV = 'heroku'
GITHUB_ENV = 'github'
DOCKER_ENV = 'docker-compose'

ENV = os.environ.get('ENV', LOCAL_ENV)

RECREATION_OF_DATABASE = False


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = random_string()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True


class ProductionConfig(Config):
    DEBUG = False
    
    url = os.environ.get('CLEARDB_DATABASE_URL', None)
    
    if url:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql' + url[5:-15]


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    if ENV == LOCAL_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/flask_app'
    elif ENV == DOCKER_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@db/flask_app'    


class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False
    
    if ENV == GITHUB_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/test_flask_app'
    elif ENV == LOCAL_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/test_flask_app'
