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

    flash(error, 'danger')
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


@app.route('/add-book/', methods=["POST", "GET"])
def add():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            isbn = request.form.get('isbn')
            published_date = int(request.form.get('publishedDate'))
            author = request.form.get('author')
            total_copies = int(request.form.get('totalCopies'))
        except ValueError:
            flash('Invalid Values! Please try again.', 'danger')
            print("value error")
            return render_template("add-book.html")

        if title == '' \
                or isbn == '' \
                or author == '' \
                or total_copies < 0:

            flash('Invalid Values! Please try again.', 'danger')
            print("invalid values")
            return render_template("add-book.html")
        else:
            new_book = Book(title, isbn, published_date, author, total_copies)
            db.session.add(new_book)
            db.session.commit()
            print("success")
            flash('Book {} added'.format(title), 'success')
            return render_template("add-book.html")
    else:
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
