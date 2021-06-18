from project import db, create_app, socketio
from project.models import *
import time
import config


if __name__ == '__main__' or config.ENV != config.LOCAL_ENV:
    if config.ENV == config.HEROKU_ENV:
        app = create_app("config.ProductionConfig")
    elif config.ENV == config.LOCAL_ENV or config.ENV == config.DOCKER_ENV:
        app = create_app("config.DevelopmentConfig")
    else:
        raise ValueError('No configuration')
    
    print('Waiting for db', flush=True)

    while True:
        try:
            with app.app_context():
                db.drop_all()
                db.create_all()
            break
        except Exception as e:
            print(e)
            time.sleep(1)

    print('Connection established', flush=True)

    with app.app_context():
        users = User.query.all()

        for user in users:
            user.sid = None
            
        admin = User.query.filter_by(is_admin=True).first()
        
        if admin == None:
            print('No admin user was found! Creating default admin...', flush=True)
            print('You can change data later', flush=True)
            username = 'admin'
            password = '123'
            admin = User(username=username, 
                        password=password,
                        is_admin=True)
            
            db.session.add(admin)

            db.session.commit()
            
            print('\nCreated admin:', flush=True)
            print(f'username: {username}', flush=True)
            print(f'password: {password}', flush=True)


        print('Server started!', flush=True)
        
        if config.ENV == config.DOCKER_ENV or config.ENV == config.LOCAL_ENV:
            socketio.run(app, debug=True, use_reloader=False)
