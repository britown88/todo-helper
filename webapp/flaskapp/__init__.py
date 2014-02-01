import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,  template_folder='../templates', static_folder='../media', static_url_path='/media', )
app.debug = True

options = {
    'dev': os.path.exists(os.path.join(app.root_path, 'dev.py'))
    }

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', '..', 'derp.db')
app.config.from_object(__name__)

print app.config.keys()

access_token = open(os.path.join(
    basedir, 'access_token.txt'), 'r').read().strip()

from flaskapp.views import load_views
from flaskapp.auth import FlaskRealmDigestDB

password = open(os.path.join(
    basedir, 'password.txt'), 'r').read().strip()

authDB = FlaskRealmDigestDB('MyAuthRealm')
authDB.add_user('admin', password)


app = load_views(app, authDB) 
