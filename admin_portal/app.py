import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from flask_session import Session
from configuration import db, ma, app, api, site
from models import Book, BookSchema, BorrowRecord

sess = Session()

db.init_app(app)

app.register_blueprint(api)
app.register_blueprint(site)


@app.route('/')
def homepage():
    """
    redirect to login page or dash board depending on whether the user has logged in or not

    Returns:
        redirect: redirect to login page or dash board depending on whether the user has logged in or not
    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return redirect(url_for('dashboard'))


@app.route('/check-credentials/', methods=["POST"])
def check_credentials():
    """
    redirect to login or dashboard depending if the credential matches. also authenticates the user

    Returns:
        redirect: redirect to login or dashboard

    """

    error = None
    if request.method == 'POST':
        if request.form.get('username', None) != 'jaqen' or request.form.get('password', None) != 'hghar':
            error = 'Invalid Credentials! Please try again.'
        else:
            session['authenticated'] = True

            return redirect(url_for('dashboard'))

    flash(error, 'danger')
    return redirect(url_for('login'))


@app.route('/login/')
def login():
    """
    loads html for login

    Returns:
        render_template: renders login.html
    """

    if 'authenticated' in session:
        session.pop('authenticated', None)

    return render_template('login.html')


@app.route('/dashboard/')
def dashboard():
    """
    redirect to login or dashboard depending if the user is logged in

    Returns:
        redirect: redirect to login or dashboard

    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    stats = BorrowRecord.get_stats()

    return render_template("dashboard.html", stats=stats)


@app.route('/add-book/')
def add():
    """
    redirect to login or rendering of Add Book page depending if the user is logged in

    Returns:
        render_template: renders Add Book
    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("add-book.html")


@app.route('/add-book-verification/', methods=["POST", "GET"])
def add_book_verification():
    """
    renders Add Book page if the user is logged in otherwise redirect to login

    Returns:
        render_template: renders Add Book page
    """

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
            new_book.add_book()
            flash('Book Added-- {}'.format(title), 'success')

    return render_template("add-book.html")


@app.route('/search-book/')
def search_book():
    """
    renders search book page if the user is logged in otherwise redirect to login

    Returns:
        render_template: renders Search Book page
    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("search-book.html")


@app.route('/search/', methods=["POST", "GET"])
def search():
    """
    searches for the query in database and shows a list

    Returns:
        redirect: redirects to list of books page

    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    if request.method == 'POST':
        query = request.form.get('query')
        result = Book.query_book(query)
        flash(result)
    return redirect('/list-books/')


@app.route('/list-books/', methods=["GET"])
def list_books():
    """
    renders list of books matched or redirects to login if user is not logged in

    Returns:
        render_template: renders list of books
    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    return render_template("list-books.html")


@app.route('/get-data/')
def get_data():
    """
    returns statistics (date vs count of books borrowed/returned) to generate bar chart

    Returns:
        json: json of statistics
    """

    result = BorrowRecord.get_graph_data()
    return json.dumps(result)


@app.route('/delete-book/<id>', methods=["POST"])
def delete_book(id):
    """
    deletes the book by id

    Args:
        id: id of book to be deleted
    """

    if "authenticated" not in session:
        return redirect(url_for('login'))
    elif session['authenticated'] is not True:
        return redirect(url_for('login'))

    # remove triangular brackets that comes with the request
    id = id[1:-1]

    if request.method == 'POST':
        Book.query.filter(Book.id == id).delete()
        db.session.commit()

    return redirect(url_for('dashboard'))


@app.errorhandler(404)
def page_not_found():
    """
    renders 404 page
    """
    return render_template('404.html')


if __name__ == '__main__':
    app.run()
