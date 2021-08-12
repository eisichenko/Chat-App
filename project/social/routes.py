from config import MAX_INACTIVE_MINS
from project.models import *
from flask import render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from project import db
from datetime import datetime, timedelta

from . import social_blueprint


def get_unread_messages():
    res = 0
    
    for chat in current_user.chats:
        timestamp = Timestamp.query.filter_by(user_id=current_user.id, chat_id=chat.id).first()
        if timestamp == None:
            res += len(chat.messages)
        else:
            unread_messages_number = Message.query.filter(Message.chat_id == chat.id, Message.date >= timestamp.timestamp).order_by(Message.date).count()
            res += unread_messages_number
    
    return res


@social_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    total_unread_messages = get_unread_messages()
    
    if request.method == 'GET':
        return render_template('home.html', 
                               username=current_user.username, 
                               total_unread_messages=total_unread_messages)

    username = request.form['search_field'][:min(15, len(request.form['search_field']))]
    
    if username == current_user.username:
        return redirect(url_for('users.my_profile'))
    
    user = User.query.filter_by(username=username).first()
    
    if user == None:
        return render_template('home.html', 
                            username=current_user.username,
                            span_class='invalid', 
                            message='No user was found :(',
                            total_unread_messages=total_unread_messages)
    
    return render_template('home.html', 
                            username=current_user.username,
                            found_username=user.username,
                            found_id=user.id,
                            is_friend=user in current_user.friends,
                            total_unread_messages=total_unread_messages,
                            is_online=((datetime.utcnow() - user.last_activity) < timedelta(minutes=MAX_INACTIVE_MINS)))


@social_blueprint.route('/messages/chat/<int:id>')
@login_required
def chat(id):
    total_unread_messages = get_unread_messages()
    
    chat = Chat.query.get(id)
    
    if chat == None or chat not in current_user.chats:
        return redirect(url_for('social.messages'))
    
    session['current_chat_id'] = id
    
    hours_delta = timedelta(hours=int(request.cookies.get('timezoneOffset', 0)))
    
    timestamp = Timestamp.query.filter_by(user_id=current_user.id, chat_id=id).first()
    
    if timestamp == None:
        seen_messages = []
        unread_messages = chat.messages
    else:
        seen_messages = Message.query.filter(Message.chat_id == id, Message.date < timestamp.timestamp).order_by(Message.date)
        unread_messages = Message.query.filter(Message.chat_id == id, Message.date >= timestamp.timestamp).order_by(Message.date)
    
    if chat.users[0].id == current_user.id:
        other_user = chat.users[1]
    else:
        other_user = chat.users[0]
    
    is_online = (datetime.utcnow() - other_user.last_activity) < timedelta(minutes=MAX_INACTIVE_MINS)
    
    page = render_template('chat.html', 
                        seen_messages=list(seen_messages), 
                        unread_messages=list(unread_messages),
                        current_user=current_user,
                        hours_delta=hours_delta,
                        is_online=is_online,
                        total_unread_messages=total_unread_messages)
    
    if timestamp == None:
        db.session.add(Timestamp(user_id=current_user.id, 
                                chat_id=chat.id,
                                timestamp=datetime.utcnow()))
    else:
        timestamp.timestamp = datetime.utcnow()

    db.session.commit()
    
    return page


@social_blueprint.route('/messages')
@login_required
def messages():   
    total_unread_messages = 0
     
    chats_with_unread_messages = []
    for chat in current_user.chats:
        if chat.users[0].id == current_user.id:
            other_user = chat.users[1]
        else:
            other_user = chat.users[0]
        
        is_online = (datetime.utcnow() - other_user.last_activity) < timedelta(minutes=MAX_INACTIVE_MINS)
        
        timestamp = Timestamp.query.filter_by(user_id=current_user.id, chat_id=chat.id).first()
        if timestamp == None:
            chats_with_unread_messages.append((chat, len(chat.messages), is_online))
            total_unread_messages += len(chat.messages)
        else:
            unread_messages_number = Message.query.filter(Message.chat_id == chat.id, Message.date >= timestamp.timestamp).order_by(Message.date).count()
            chats_with_unread_messages.append((chat, unread_messages_number, is_online))
            total_unread_messages += unread_messages_number
    
    return render_template('messages.html', 
                           chats_with_unread_messages=chats_with_unread_messages,
                           total_unread_messages=total_unread_messages)


@social_blueprint.route('/start-chat/<int:other_id>')
@login_required
def start_chat(other_id):
    other_user = User.query.get(other_id)
    
    if other_user == None or other_id == current_user.id:
        return redirect(url_for('social.home'))
    
    for chat in current_user.chats:
        if chat.users[0].id == other_id or chat.users[1].id == other_id:
            return redirect(url_for('social.chat', id=chat.id))
    
    new_chat = Chat()
    
    db.session.add(new_chat)
    new_chat.users.append(current_user)
    new_chat.users.append(other_user)
    
    db.session.commit()
    
    return redirect(url_for('social.chat', id=new_chat.id))


@social_blueprint.route('/friends')
@login_required
def friends():
    total_unread_messages = get_unread_messages()
    
    items = []
    
    for friend in current_user.friends:
        is_online = (datetime.utcnow() - friend.last_activity) < timedelta(minutes=MAX_INACTIVE_MINS)
        items.append((friend, is_online))
    
    return render_template('friends.html', 
                           items=items,
                           total_unread_messages=total_unread_messages)


@social_blueprint.route('/add-friend/<int:friend_id>')
@login_required
def add_friend(friend_id):
    if (friend_id == current_user.id):
        return redirect(url_for('social.home'))
    
    friend_user = User.query.get(friend_id)
    
    if (friend_user == None or friend_user in current_user.friends):
        return redirect(url_for('social.friends'))
    
    current_user.friends.append(friend_user)
    friend_user.friends.append(current_user)
    
    db.session.commit()
    
    return redirect(url_for('social.friends'))


@social_blueprint.route('/remove-friend/<int:friend_id>')
@login_required
def remove_friend(friend_id):
    if friend_id == current_user.id:
        return redirect(url_for('social.home'))
    
    friend_user = User.query.get(friend_id)
    
    if friend_user == None or not friend_user in current_user.friends:
        return redirect(url_for('social.friends'))
    
    current_user.friends.remove(friend_user)
    friend_user.friends.remove(current_user)
    
    db.session.commit()
    
    return redirect(url_for('social.friends'))
