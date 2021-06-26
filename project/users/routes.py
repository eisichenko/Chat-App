from project.models import User
from flask import render_template, request, redirect, url_for, session, make_response
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from project import db, socketio
import config

from . import users_blueprint


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    with config.db_semaphore:
        if request.method == 'POST':
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
                response = make_response(redirect(url_for('social.home')))
                response.set_cookie('username', username, max_age=60*60*24*365)
                return response
                
            return render_template('login.html',
                                span_class='invalid',
                                message='Invalid username or password')
        else:
            if ('message' in session.keys() and 'span_class' in session.keys() and 
                len(session['message']) > 0 and len(session['span_class']) > 0):
                
                message = session.pop('message', '')
                span_class = session.pop('span_class', '')
                
                return render_template('login.html', 
                    span_class=span_class, 
                    message=message)

            return render_template('login.html')


@users_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    with config.db_semaphore:
        if request.method == 'POST':
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
            
        return render_template('signup.html')


@users_blueprint.route('/logout')
@login_required
def logout():
    with config.db_semaphore:
        logout_user()
        return redirect(url_for('users.login'))


@users_blueprint.route('/my-profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    with config.db_semaphore:
        user = User.query.get(current_user.id)
        
        if request.method == 'GET':
            return render_template('my_profile.html', user=user)
        else:
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
                
                response = make_response(redirect(url_for('users.my_profile')))
                response.set_cookie('username', username, max_age=60*60*24*365)
                
                return response
                        
            return render_template('my_profile.html',
                            span_class='invalid',
                            message='Invalid username',
                            user=user)


@users_blueprint.route('/delete')
@login_required
def delete():
    with config.db_semaphore:
        user = User.query.get(current_user.id)
        
        logout_user()
        
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('users.login'))
