import json
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_session import Session
from configuration import db, ma, app, api, site
from models import Book

sess = Session()

db.init_app(app)

app.register_blueprint(api)
app.register_blueprint(site)


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
    books = Book.query.all()

    for book in books:
        print(book.title)
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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
