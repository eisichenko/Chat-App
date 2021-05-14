class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'qweqwe O_o 123321'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

    SESSION_COOKIE_SECURE = False
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://egor:UserPa$$123@localhost/flask_app'

class TestingConfig(Config):
    TESTING = True
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://egor:UserPa$$123@localhost/test_flask_app'

    SESSION_COOKIE_SECURE = False