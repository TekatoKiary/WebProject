import os

from flask import Flask, render_template, redirect
from data.db import db_session

db_session.global_init("data/db/db_files/explorer.sqlite")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'


@app.route('/')
def index():
    return redirect('/profile')


@app.route('/profile')
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
