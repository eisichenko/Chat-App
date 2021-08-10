from project import db, create_app, socketio, admin
from project.models import *
import time
import config

if config.needs_redis():
    import eventlet
    print('Monkey patching')
    eventlet.monkey_patch()

app = create_app(config.get_config_string())

if (__name__ == '__main__' or config.ENV != config.LOCAL_ENV) and not config.RECREATION_OF_DATABASE:
    with app.app_context():
        print('Waiting for db...')
        
        while True:
            try:
                db.create_all()
                break
            except Exception as e:
                print(e, flush=True)
                time.sleep(1)

        print('Connection established!')

        users = User.query.all()

        for user in users:
            user.sid = None
            
        admin = User.query.filter_by(is_admin=True).first()
        
        if admin == None:
            print('No admin user was found! Creating default admin...')
            print('You can change data later')
            username = 'admin'
            password = '123'
            admin = User(username=username, 
                        password=password,
                        is_admin=True)
            
            db.session.add(admin)

            print('\nCreated default admin user:')
            print(f'USERNAME: {username}')
            print(f'PASSWORD: {password}')
        
        db.session.commit()

    print('Server started!')

    if config.ENV == config.LOCAL_ENV:
        socketio.run(app, use_reloader=False)
