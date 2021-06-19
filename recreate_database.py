from app import app
from project.models import *
import time
import os

if __name__ == '__main__':
    os.environ['recreation_db'] = 'true'
    
    with app.app_context():
        print('Waiting for db...', flush=True)

        while True:
            try:
                db.drop_all()
                db.create_all()
                break
            except Exception as e:
                print(e, flush=True)
                time.sleep(1)

        print('Database recreated!', flush=True)

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

    os.environ['recreation_db'] = 'false'
