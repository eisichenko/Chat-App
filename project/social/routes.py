from project.models import User, Chat
from flask import render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from project import db, socketio
import threading

from . import social_blueprint


@social_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        return render_template('home.html', username=current_user.username)

    username = request.form['search_field']
    
    if username == current_user.username:
        return redirect(url_for('users.my_profile'))
    
    user = User.query.filter_by(username=username).first()
    
    if (user is None):
        return render_template('home.html', 
                            username=current_user.username,
                            span_class='invalid', 
                            message='No user was found :(')
    
    return render_template('home.html', 
                            username=current_user.username,
                            found_username=user.username,
                            found_id=user.id,
                            is_friend=user in current_user.friends,
                            is_online=user.sid != None)


@social_blueprint.route('/messages/chat/<int:id>')
@login_required
def chat(id):
    chat = Chat.query.get(id)
    
    if chat == None or chat not in current_user.chats:
        return redirect(url_for('social.messages'))
    
    session['current_chat_id'] = id
    
    page = render_template('chat.html', messages=chat.messages, current_user=current_user)
    
    if (chat.unread_messages_number > 0):
        sent_user = False
        
        for message in chat.messages:
            if message.unread:
                if message.user_id != current_user.id:
                    message.unread = False
                else:
                    sent_user = True
                    break
        
        if not sent_user:
            chat.unread_messages_number = 0
            db.session.commit()
    
    return page


@social_blueprint.route('/messages')
@login_required
def messages():
    return render_template('messages.html', chats=current_user.chats, current_user=current_user)


@social_blueprint.route('/start-chat/<int:other_id>')
@login_required
def start_chat(other_id):
    other_user = User.query.get(other_id)
    
    if (other_user is None or other_id == current_user.id):
        return redirect(url_for('social.home'))
    
    for chat in current_user.chats:
        if chat.users[0].id == other_id or chat.users[1].id == other_id:
            return redirect(url_for('social.chat', id=chat.id))
    
    new_chat = Chat(unread_messages_number=0)
    
    threads = [threading.Thread(target=db.session.add(new_chat)),
               threading.Thread(target=new_chat.users.append(current_user)),
               threading.Thread(target=new_chat.users.append(other_user))]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    db.session.commit()
    
    socketio.emit('join', json={'chat_id': new_chat.id, 
                                'user1_sid': current_user.sid, 
                                'user2_sid':other_user.sid})
    
    return redirect(url_for('social.chat', id=new_chat.id))


@social_blueprint.route('/friends')
@login_required
def friends():
    return render_template('friends.html', current_user=current_user)


@social_blueprint.route('/add-friend/<int:friend_id>')
@login_required
def add_friend(friend_id):
    if (friend_id == current_user.id):
        return redirect(url_for('social.home'))
    
    friend_user = User.query.get(friend_id)
    
    if (friend_user == None or friend_user in current_user.friends):
        return redirect(url_for('social.friends'))
    
    threads = [threading.Thread(target=current_user.friends.append(friend_user)),
               threading.Thread(target=friend_user.friends.append(current_user))]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    db.session.commit()
    
    return render_template('friends.html', current_user=current_user)


@social_blueprint.route('/remove-friend/<int:friend_id>')
@login_required
def remove_friend(friend_id):
    if (friend_id == current_user.id):
        return redirect(url_for('social.home'))
    
    friend_user = User.query.get(friend_id)
    
    if (friend_user == None or not friend_user in current_user.friends):
        return redirect(url_for('social.friends'))
    
    threads = [threading.Thread(target=current_user.friends.remove(friend_user)),
               threading.Thread(target=friend_user.friends.remove(current_user))]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    db.session.commit()
    
    return render_template('friends.html', current_user=current_user)
