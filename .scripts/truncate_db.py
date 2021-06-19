import sys
import os

if os.getcwd().endswith('.scripts'):
    sys.path.append('..')
else:
    sys.path.append(os.getcwd())

from project.models import *
import time
import config


if __name__ == '__main__':
    print('Are you sure to truncate all tables in database? (y/n) ', flush=True)
    ans = input()
    
    if ans == 'y':
        config.RECREATION_OF_DATABASE = True
        
        from app import app
        
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
                
        config.RECREATION_OF_DATABASE = False
    else:
        print('Operation was interrupted.')
