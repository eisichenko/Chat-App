import os
import random
import string


def random_string(n=random.randint(100, 150)):
    symbols = string.digits + string.ascii_letters + string.punctuation + ' '
    return ''.join(random.choice(symbols) for _ in range(n))


def get_config_string():
    if ENV == HEROKU_ENV:
        return 'config.ProductionConfig'
    elif ENV == LOCAL_ENV or ENV == DOCKER_ENV or ENV == RQ_ENV:
        return 'config.DevelopmentConfig'
    raise ValueError('No configuration')


LOCAL_ENV = 'local'
HEROKU_ENV = 'heroku'
GITHUB_ENV = 'github-actions'
DOCKER_ENV = 'docker-compose'
RQ_ENV = 'rq'

ENV = os.environ.get('ENV', LOCAL_ENV)

RECREATION_OF_DATABASE = False

if ENV == LOCAL_ENV:
    REDIS_URL = None
elif ENV == DOCKER_ENV or ENV == RQ_ENV:
    REDIS_URL = 'redis://redis:6379'
elif ENV == HEROKU_ENV:
    REDIS_URL = os.environ.get('REDISTOGO_URL', None)
    if REDIS_URL == None:
        raise Exception('No redis url')
    
def needs_redis():
    return ENV != LOCAL_ENV and ENV != GITHUB_ENV

MAX_INACTIVE_MINS = 5

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
    elif ENV == DOCKER_ENV or ENV == RQ_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@db/flask_app'    


class TestingConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False
    
    if ENV == GITHUB_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/test_flask_app'
    elif ENV == LOCAL_ENV:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost/test_flask_app'
