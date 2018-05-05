from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

#INITIALIZING DIFFERENT ADDONS USED IN APP

application = Flask(__name__)
application.config.from_object(Config)
db = SQLAlchemy(application)
migrate = Migrate(application,db)
login = LoginManager(application)

from app import routes,models
