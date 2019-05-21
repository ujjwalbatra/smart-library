from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def homepage():
    return redirect(url_for('dashboard'))


@app.route('/check-credentials/', methods=["POST"])
def check_credentials():
    error = None
    if request.method == 'POST':
        if request.form.get('username', None) != 'admin' or request.form.get('password', None) != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/login/')
def login():
    return render_template('login.html', error=None)


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


if __name__ == '__main__':
    app.run(host="0.0.0.0")
