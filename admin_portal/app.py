import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from flask_api import api, db
from flask_site import site
from configuration import db, ma, app
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
    print(books)
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
    app.run()
