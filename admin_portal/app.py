import json

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
sess = Session()


@app.route('/')
def homepage():
    return redirect(url_for('login'))


@app.route('/check-credentials/', methods=["POST"])
def check_credentials():
    error = None
    if request.method == 'POST':
        if request.form.get('username', None) != 'admin' or request.form.get('password', None) != 'admin':
            error = 'Invalid Credentials! Please try again.'
        else:
            return redirect(url_for('dashboard'))

    flash(error, "danger")
    return redirect(url_for('login'))


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html")


@app.route('/add-book/')
def add():
    return render_template("add-book.html")


@app.route('/search-book/')
def search():
    return render_template("search-book.html")


@app.route('/list-books/')
def list_books():
    return render_template("list-books.html")


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0")
