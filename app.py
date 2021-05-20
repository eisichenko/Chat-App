from project import db, create_app, socketio
from project.models import *
import time

# app = create_app("config.ProductionConfig")
# app = create_app("config.DevelopmentConfig")
app = create_app("config.HerokuConfig")

# to run from gunicorn
if __name__ == 'app':
    n = 0
    max_n = 100
    
    print('Waiting for db ', flush=True)
    
    exception = None

    while n < max_n or True:
        try:
            with app.app_context():
                # db.init_app(app)
                # db.drop_all()
                db.create_all()
            break
        except Exception as e:
            time.sleep(1)
            # print(f'Attempt to connect: {n + 1}/{max_n}', flush=True)
            n += 1
            exception = e
    
    if n == max_n:
        raise Exception(str(e))
    
    print('Connection established', flush=True)
    
    with app.app_context():
        users = User.query.all()

        for user in users:
            user.sid = None
            
        admin = User.query.filter_by(is_admin=True).first()
        
        if (admin == None):
            print('No admin user was found! Creating default admin...')
            print('You can change data later')
            username = 'admin'
            password = '123'
            admin = User(username=username, 
                        password=password,
                        is_admin=True)
            
            db.session.add(admin)

            db.session.commit()
            
            print('Created admin:')
            print(f'username: {username}', flush=True)
            print(f'password: {password}', flush=True)
            
    print('Server started!')

# to run from localhost
if __name__ == '__main__':
    
    with app.app_context():
        # db.drop_all()
        db.create_all()

        users = User.query.all()

        for user in users:
            user.sid = None
            
        admin = User.query.filter_by(is_admin=True).first()
        
        if (admin == None):
            print('\n\nNo admin user was found! Create new admin user:\n')
            username = input('Admin username: ')
            password = input('Admin password: ')
            admin = User(username=username, 
                        password=password,
                        is_admin=True)
            print('\n')
            
            existing_admin = User.query.filter_by(username=username).first()
            
            while existing_admin != None:
                print('\n\nUsername already exists!\n')
                username = input('Admin username: ')
                password = input('Admin password: ')
                admin = User(username=username, 
                            password=password,
                            is_admin=True)
                print('\n')
                existing_admin = User.query.filter_by(username=username).first()
            
            db.session.add(admin)

        db.session.commit()

    socketio.run(app, debug=True)
