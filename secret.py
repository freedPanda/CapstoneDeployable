from flask_bcrypt import Bcrypt
from flask import Flask, request, redirect, render_template, session, flash
from models import db, connect_db, Admin
from sqlalchemy.exc import IntegrityError
import os

"""WHAT IS THIS? Secret.py has four functions, login(), register(), authenticate(), get_route()
If you are setting up the website then the first step is to register(username,password). 
Next, login() and choose 'cr' to create a random string that you will need to have in order to 
login to the admin portal. Login() again and choose 'a' to add an admin to the db."""

bcrypt = Bcrypt()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///capstone1')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"


def login():
    username = input('Username: ')
    password = input('password: ')
    authenticate(username,password)

#pass in what you want your username and password to be. These credentials are used to access
#admin table in the db as well as create or change the "back door" for admins to access the
#change or modify records in the db
def register(username,password):
        
        #editable = False
        username += '\n'
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        
        #if editable == False:
           # return '...'
        path = f'random.txt'
        admin = open(path,'w')
        admin.write(username)
        admin.write(hashed_utf8)
        admin.close()
        
def authenticate(username, password):
    path = f'random.txt'
    admin_file = open(path,'r')
    f_username = admin_file.readline()
    f_password = admin_file.readline()
    admin_file.close()
        #return u
    if bcrypt.check_password_hash(f_password, password):
        username += '\n'
        if f_username == username:
            change_route = input('Change route, add admin, delete admin, or cancel: cr, a, d or c?')
            if change_route == 'cr':
                path = f'secret.txt'
                route_file = open(path,'w')
                #need to mention what not to use in route
                new_route = input('Enter new route(avoid /\@): ')
                route_file.write(new_route)
                route_file.close()
                #last thing to do
            elif change_route == 'a':
                connect_db(app)
                #db.create_all()
                username = input('Username: ')
                password = input('Password: ')
                
                try:
                    admin = Admin.register(username=username,password=password)
                    db.session.commit()
                    print(f'Success. username={admin.username}')
                except IntegrityError:
                    print('Username already taken')
            elif change_route == 'c':
                print('canceled operation')
            elif change_route == 'd':
                connect_db(app)
                username = input('Username to delete: ')
                admin = Admin.query.filter_by(username = username).first()
                db.session.delete(admin)
                db.session.commit()
            else:
                print('invalid entry')
        else:
            print('incorrect password')
    else:
        print('invalid username')

def get_route():
    path = f'secret.txt'
    route_file = open(path,'r')
    route = route_file.readline()
    route_file.close()
    return route
