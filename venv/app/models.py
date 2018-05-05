from datetime import datetime
from app import db #variable defined in init.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login #The login manager object defined in init.py

#Model for the Users database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    #Linking posts associated with the author
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

#Saving passwords as a hash for security
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_passwords(self,password):
        return check_password_hash(self.password_hash, password)

#Database for storing posts each post is linked backed to a user
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

#Returning a user when loggin in
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

