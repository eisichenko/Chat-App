from project import create_app, socketio, db
from project.models import *


app = create_app("config.DevelopmentConfig")
app.app_context().push()

if __name__ == '__main__':
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
