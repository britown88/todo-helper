import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,  template_folder='../templates', static_folder='../media', static_url_path='/media', )

options = {
    'dev': os.path.exists(os.path.join(app.root_path, 'dev.py'))
    }

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', '..', 'derp.db')
app.config.from_object(__name__)

print app.config.keys()
# get database
db = SQLAlchemy(app)

access_token = open(os.path.join(
    basedir, 'access_token.txt'), 'r').read().strip()

from flaskapp import views, models
