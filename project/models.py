from project import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash
from sqlalchemy.dialects.mysql import DATETIME

args = { 'mysql_collate': 'utf8mb4_bin', 'mysql_charset': 'utf8mb4' }

collation = 'utf8mb4_bin'
charset = 'utf8mb4'


chats_table = db.Table('chats',
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.id'), primary_key=True),
    db.Column('chat_id', db.BigInteger, db.ForeignKey('chat.id'), primary_key=True),
    mysql_collate = collation,
    mysql_charset = charset
)


friends_table = db.Table('friends',
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.BigInteger, db.ForeignKey('user.id'), primary_key=True),
    mysql_collate = collation,
    mysql_charset = charset
)

class Timestamp(db.Model):
    __table_args__ = args
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    chat_id = db.Column(db.BigInteger, db.ForeignKey('chat.id'), nullable=False, primary_key=True)
    timestamp = db.Column(DATETIME(fsp=6))
    
    def __repr__(self):
        return f'<Timestamp(user_id = "{self.user_id}" chat_id = "{self.chat_id}")>'


class User(UserMixin, db.Model):
    __table_args__ = args
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Unicode(15), nullable=False, unique=True)
    password = db.Column(db.Unicode(100), nullable=False)
    sid = db.Column(db.Unicode(50), nullable=True)
    
    messages = db.relationship('Message', backref='user', lazy=True)
    chats = db.relationship('Chat', secondary=chats_table, backref=db.backref('users', lazy=True), lazy=True)
    friends = db.relationship('User', 
                              secondary=friends_table,
                              primaryjoin = (friends_table.c.user_id == id),
                              secondaryjoin = (friends_table.c.friend_id == id),
                              lazy=True)
    timestamps = db.relationship('Timestamp', backref='user', lazy=True)
    
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f'<User(id = "{self.id}" username = "{self.username}")>'


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    return generate_password_hash(value, method='sha256')


class Message(db.Model):
    __table_args__ = args
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.BigInteger, db.ForeignKey('chat.id'), nullable=False)
    date = db.Column(DATETIME(fsp=6), default=datetime.utcnow())
    
    def __repr__(self):
        return f'<Message(id = "{self.id}")>'


class Chat(db.Model):
    __table_args__ = args
    id = db.Column(db.BigInteger, primary_key=True)
    messages = db.relationship('Message', order_by='Message.date', backref='chat', lazy=True)
    timestamps = db.relationship('Timestamp', backref='chat', lazy=True)
