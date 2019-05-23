import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_session import Session
from configuration import db, ma, app, api, site
from models import Book, BookSchema
from sqlalchemy import or_

sess = Session()

db.init_app(app)

app.register_blueprint(api)
app.register_blueprint(site)


@app.route('/')
def homepage():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return redirect(url_for(dashboard))


@app.route('/check-credentials/', methods=["POST"])
def check_credentials():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

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
    session['authenticated'] = True
    return render_template('login.html')


@app.route('/dashboard/')
def dashboard():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("dashboard.html")


@app.route('/add-book/')
def add():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("add-book.html")


@app.route('/add-book-verification/', methods=["POST", "GET"])
def add_book_verification():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            isbn = request.form.get('isbn')
            published_date = int(request.form.get('publishedDate'))
            author = request.form.get('author')
            total_copies = int(request.form.get('totalCopies'))
        except ValueError:
            flash('Invalid Values! Please try again.', 'danger')
            return render_template("add-book.html")

        if title == '' \
                or isbn == '' \
                or author == '' \
                or total_copies < 0:

            flash('Invalid Values! Please try again.', 'danger')
        else:
            new_book = Book(title, isbn, published_date, author, total_copies)
            db.session.add(new_book)
            db.session.commit()
            flash('Book Added-- {}'.format(title), 'success')

    return render_template("add-book.html")


@app.route('/search-book/')
def search_book():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("search-book.html")


@app.route('/search/', methods=["POST", "GET"])
def search():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    if request.method == 'POST':
        query = request.form.get('query')
        result = Book.query.with_entities(Book.id, Book.title, Book.isbn, Book.author, Book.published_year,
                                          Book.total_copies, Book.copies_available). \
            filter(or_(Book.id.like("%" + query + "%"), Book.title.like("%" + query + "%"),
                       Book.author.like("%" + query + "%"), Book.isbn.like("%" + query + "%"))).all()

        book_schema = BookSchema(many=True)
        result = book_schema.dump(result).data

        flash(result)
    return redirect('/list-books/')


@app.route('/list-books/')
def list_books():
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("list-books.html")


@app.route('/logout/')
def logout():
    # end the session authentication
    session.pop('authenticated', None)

    return redirect(url_for("/"))


@app.route('/delete-book/<id>', methods=["POST"])
def delete_book(id):
    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    # remove triangular brackets that comes with the request
    id = id[1:-1]

    if request.method == 'POST':
        Book.query.filter(Book.id == id).delete()
        db.session.commit()


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html')


if __name__ == '__main__':
    app.run()
