__author__ = 'nishitarao'

from flask import Flask, jsonify, render_template, request, g
import json
import sqlite3
from contextlib import closing

app = Flask(__name__)
app.debug = True

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# Getting Environment variables
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


#Initialize the DB
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def signin():
    return render_template('signin.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run()