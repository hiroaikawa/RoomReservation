from flask import Flask, session
import os
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('testapp.config')
app.secret_key = 'super secret string'  # Change this!

#app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECRET_KEY'] = '{key string}'

# Set DB
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

#import testapp.user
import testapp.views
