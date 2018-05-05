from flask import render_template, flash, redirect, url_for
from app import application
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User

#Defining routes for different links
@application.route('/')
@application.route('/index')

def index():
    user = {'username': 'Nekhil'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',title = 'Home', user = user, posts = posts)

#Route for login, allows two way communication
@application.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    #If the form is valid -- Hurray!!
    if form.validate_on_submit():
        #Get the user info from the database
        user = User.query.filter_by(username = form.username.data).first()

        #If did not find valid information or password is invalid then go back to login ppage
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        #If everything good then login the user
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html',title = 'Sign In', form = form)
