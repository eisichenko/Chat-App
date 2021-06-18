from project import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from werkzeug.security import generate_password_hash

collation = 'utf8_bin'


chats_table = db.Table('chats',
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.id'), primary_key=True),
    db.Column('chat_id', db.BigInteger, db.ForeignKey('chat.id'), primary_key=True),
    mysql_collate = collation
)


friends_table = db.Table('friends',
    db.Column('user_id', db.BigInteger, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.BigInteger, db.ForeignKey('user.id'), primary_key=True),
    mysql_collate = collation
)


class User(UserMixin, db.Model):
    __table_args__ = {'mysql_collate': collation}
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Unicode(15), nullable=False, unique=True)
    password = db.Column(db.Unicode(80), nullable=False)
    sid = db.Column(db.Unicode(50), nullable=True)
    
    messages = db.relationship('Message', backref='user', lazy=True)
    chats = db.relationship('Chat', secondary=chats_table, backref=db.backref('users', lazy=True), lazy=True)
    friends = db.relationship('User', 
                              secondary=friends_table,
                              primaryjoin = (friends_table.c.user_id == id),
                              secondaryjoin = (friends_table.c.friend_id == id),
                              lazy=True)
    
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f'<User(id = "{self.id}" username = "{self.username}")>'


@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    return generate_password_hash(value, method='sha256')


class Message(db.Model):
    __table_args__ = {'mysql_collate': collation}
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.UnicodeText, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.BigInteger, db.ForeignKey('chat.id'), nullable=False)
    unread = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self):
        return f'<Message(id = "{self.id}")>'


class Chat(db.Model):
    __table_args__ = {'mysql_collate': collation}
    id = db.Column(db.BigInteger, primary_key=True)
    unread_messages_number = db.Column(db.BigInteger, default=0, nullable=False)
    messages = db.relationship('Message', backref='chat', lazy=True)
