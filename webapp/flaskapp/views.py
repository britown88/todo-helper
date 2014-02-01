import json
import os
import sys
import urllib2

from flask import ( Flask,
                    jsonify,
                    make_response,
                    redirect,
                    render_template,
                    request,
                    send_from_directory,
                    url_for)
from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import Environment

from flaskapp import app, options, basedir, access_token
# from models import Derp

env = Environment()

from functools import wraps
from flask import current_app

def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        print callback
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            print content
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

def load_views(webapp, authdb):

    @webapp.route('/')
    @authdb.requires_auth
    def index(jsondata=None):
        # grab stuff and render them
        dev = options['dev']
        return render_template('base.html', **locals())

    @webapp.route('/favicon.ico')
    def favicon():
        #print "found favicon.ico"
        #print os.path.join(webapp.root_path, '..', 'media', 'favicon.ico')
        return send_from_directory(os.path.join(webapp.root_path, '..', 'media'), 'favicon.ico')

    @webapp.route('/bower_components/<path:filename>')
    def bower_components(filename):
        print os.path.join(webapp.root_path, '..', 'bower_components'), filename
        return send_from_directory(os.path.join(webapp.root_path, '..', 'bower_components'), filename)

    @webapp.route('/build/<path:filename>')
    def build(filename):
        print os.path.join(webapp.root_path, '..', 'build'), filename
        return send_from_directory(os.path.join(webapp.root_path, '..', 'build'), filename)

    @webapp.route('/api/<path:apipath>', methods=['GET', 'POST'])
    @authdb.requires_auth
    @jsonp
    def api(apipath):
        githubApiUrl = 'https://api.github.com/'

        req = urllib2.Request(
            "%s%s?access_token=%s" % (githubApiUrl, apipath, access_token)
            )

        if request.method == 'POST':
            req.add_data(json.dumps(request.form.to_dict()))

        response = urllib2.urlopen(req)
        data = json.loads(response.read())

        return jsonify(
            data = data
            )

    return webapp

