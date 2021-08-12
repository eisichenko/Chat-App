from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import QueuePool
from flask_socketio import SocketIO
from flask_login import LoginManager, login_manager, current_user
from werkzeug import debug
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import redis
import rq
import config


db = SQLAlchemy(engine_options={"pool_size": 10, "poolclass":QueuePool, "pool_pre_ping":True})

from project.models import *

login_manager = LoginManager()

socketio = SocketIO()

login_manager.login_view = "users.login"

admin = Admin()

if config.needs_redis():
    redis_connection = redis.from_url(config.REDIS_URL)
    high_queue = rq.Queue(name='high', connection=redis_connection)
    default_queue = rq.Queue(name='default', connection=redis_connection)
    low_queue = rq.Queue(name='low', connection=redis_connection)

class UserView(ModelView):
    column_list = ['id', 'username', 'password', 'sid', 'last_activity', 'is_admin']


class ChatView(ModelView):
    column_list = ['id']
    

class MessageView(ModelView):
    column_list = ['id', 'text', 'date', 'user', 'chat']
    

class TimestampView(ModelView):
    column_list = ['user', 'chat', 'timestamp']

    

class HomeAdminView(AdminIndexView):
    def is_accessible(self):
        return not current_user.is_anonymous and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        abort(404)


def create_app(config_string):
    app = Flask(__name__)
    app.config.from_object(config_string)
    
    register_blueprints(app)
    initialize_extensions(app)
    
    admin.init_app(app, url='/', index_view=HomeAdminView(name='Home'))
    admin.add_view(UserView(User, db.session))
    admin.add_view(ChatView(Chat, db.session))
    admin.add_view(MessageView(Message, db.session))
    admin.add_view(TimestampView(Timestamp, db.session))
    
    if config.needs_redis():
        socketio.init_app(app, cors_allowed_origins="*", message_queue=config.REDIS_URL)
    else:
        socketio.init_app(app, cors_allowed_origins="*")
    
    return app


def initialize_extensions(app):
    db.init_app(app)
        
    login_manager.init_app(app)

    from project.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

def register_blueprints(app):
    from project.social import social_blueprint
    from project.users import users_blueprint

    app.register_blueprint(social_blueprint)
    app.register_blueprint(users_blueprint)
