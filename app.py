from project import db, create_app, socketio
from project.models import *
import time
import config

app = create_app(config.get_config_string())

if (__name__ == '__main__' or config.ENV != config.LOCAL_ENV) and not config.RECREATION_OF_DATABASE:
    with app.app_context():
        print('Waiting for db...', flush=True)

        while True:
            try:
                db.create_all()
                break
            except Exception as e:
                print(e, flush=True)
                time.sleep(1)

        print('Connection established!', flush=True)

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
            
            print('\nCreated default admin user:', flush=True)
            print(f'USERNAME: {username}', flush=True)
            print(f'PASSWORD: {password}', flush=True)


        print('Server started!', flush=True)
        
        if config.ENV == config.DOCKER_ENV or config.ENV == config.LOCAL_ENV:
            socketio.run(app, debug=True, use_reloader=False)
