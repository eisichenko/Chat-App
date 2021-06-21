from project.models import User
from flask import render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from project import db, socketio

from . import users_blueprint


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            valid_username = not username is None and len(username) > 2 and len(username) < 16
            valid_password = not password is None and len(password) > 2 and len(username) < 81
            
            if valid_username and valid_password:
                
                db_user = User.query.filter_by(username=username).first()
                
                if db_user == None or not check_password_hash(db_user.password, password):
                    return render_template('login.html', 
                                        span_class='invalid', 
                                        message='Wrong username or password',
                                        prev_username=username)
                login_user(db_user)
                return redirect(url_for('social.home'))
                
            return render_template('login.html',
                                span_class='invalid',
                                message='Invalid username or password')
        except:
            return redirect('/login')
    else:
        try:
            if ('message' in session.keys() and 'span_class' in session.keys() and 
                len(session['message']) > 0 and len(session['span_class']) > 0):
                
                message = session.pop('message', '')
                span_class = session.pop('span_class', '')
                
                return render_template('login.html', 
                    span_class=span_class, 
                    message=message)
        except:
            pass

        return render_template('login.html')


@users_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            valid_username = not username is None and len(username) > 2 and len(username) < 16
            valid_password = not password is None and len(password) > 2 and len(username) < 81
            
            if valid_username and valid_password:
                new_user = User(username=username, 
                                password=password)
                
                existing_user = User.query.filter_by(username=username).first()
                
                if existing_user:
                    return render_template('signup.html', 
                                        span_class='invalid', 
                                        message='Username already exists',
                                        prev_username=username)
                    
                db.session.add(new_user)
                db.session.commit()
                session['message'] = "You've registered account successfully"
                session['span_class'] = 'valid'
                return redirect(url_for('users.login'))
                
            return render_template('signup.html',
                                span_class='invalid',
                                message='Invalid username or password')
        except:
            pass
        
    return render_template('signup.html')


@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users_blueprint.route('/my-profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    user = User.query.get(current_user.id)
    
    if request.method == 'GET':
        return render_template('my_profile.html', user=user)
    else:
        try:
            username = request.form['username']
            valid_username = not username is None and len(username) > 2 and len(username) < 16
            
            existing_username = User.query.filter_by(username=username).first()
            
            if existing_username:
                return render_template('my_profile.html', 
                                    span_class='invalid', 
                                    message='Username already exists',
                                    user=user)
            
            if valid_username:
                user.username = username
                db.session.commit()
                socketio.emit('setup connection', { "username": current_user.username }, room=request.sid)
                return redirect(url_for('users.my_profile'))
                        
            return render_template('my_profile.html',
                            span_class='invalid',
                            message='Invalid username',
                            user=user)
        except:
            return redirect('/my-profile')


@users_blueprint.route('/delete')
@login_required
def delete():
    try:
        user = User.query.get(current_user.id)
        
        logout_user()
        
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('users.login'))
    except:
        return redirect('/my-profile')
