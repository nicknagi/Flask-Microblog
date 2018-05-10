from datetime import datetime
from app import db #variable defined in init.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login #The login manager object defined in init.py
from hashlib import md5
from time import time
import jwt
from app import application

########## File contains models and necessary systems needed for database operation ###############

#Auxillary table for followers in the system
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#Model for the Users database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #Linking posts associated with the author
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    #DB ralation for follow system
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    #Functions to abstract user following, unfollowing
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    #Function to return a url for the user avatar, generated using gravatar and email as md5 hash
    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

#Saving passwords as a hash for security
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    #Big query get get required information, join - gets all posts who have followers, filter - limits posts to only
    # the ones that user follows, and sort - sorts all given posts by time
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    # use jwt to get a password token
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            application.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # use jwt to verify given token
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, application.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

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

