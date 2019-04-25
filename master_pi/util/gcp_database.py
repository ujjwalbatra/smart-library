import json
import MySQLdb
from datetime import date


# noinspection SqlDialectInspection
class GcpDatabase:

    def __init__(self):
        host, database, user, password = self.__get_database_details()
        self.__connection = MySQLdb.connect(host, user, password, database)
        self.__cursor = self.__connection.cursor()

    def close(self):
        """
        closes the database connection
        """

        self.__connection.close()

    def __get_database_details(self):
        """
        Gets details of database form config.json

        Returns:
            string: host IP address of DB
            string: Database name
            string: User name
            string: password
        """

        with open('./master_pi/config.json') as json_file:
            data = json.load(json_file)
            return data['gcp']['host'], data['gcp']['database'], data['gcp']['user'], data['gcp']['password']

    def create_tables(self):
        """
        creates tables user(id, username_email), book(is, title, isbn, published_date, author)
        and borrow_record(id, book_id, user_id, status, issue_date, returned_date)
        """
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS user (id INT PRIMARY KEY, 
                                    username VARCHAR(255) UNIQUE, email VARCHAR(320) UNIQUE);''')

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS book (id INT PRIMARY KEY AUTO_INCREMENT, 
                                    title VARCHAR(1000) UNIQUE, isbn VARCHAR(20), published_date DATE, 
                                    author VARCHAR(1000), total_copies INT DEFAULT 1, 
                                    copies_available INT DEFAULT 1);''')

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_record (id INT PRIMARY KEY AUTO_INCREMENT, 
                                    user_id INT NOT NULL, book_id INT NOT NULL, status enum ('borrowed', 'returned'), 
                                    issue_date DATE DEFAULT CURRENT_DATE ,
                                    return_date DATE, actual_return_date DATE DEFAULT NULL,
                                    FOREIGN KEY (book_id) REFERENCES book(id),
                                    FOREIGN KEY (user_id) REFERENCES user(id));''')

    def borrow_book(self, user_id: int, book_id: int, return_date: str):
        """
        adds a record for book being borrowed of a user

        Args:
            user_id: id of the user who is borrowing the book
            book_id: id of the book being issued
            return_date: expected return date
        """

        self.__cursor.execute('''INSERT INTO borrow_record (user_id, book_id, status, return_date) 
                                    VALUES (%s, %s, %s, %s); ''', (user_id, book_id, "borrowed", return_date))

        self.__connection.commit()

    def get_num_available_copies(self, book_id: int):
        """
        returns number of copies available for a book

        Args:
            book_id: id of the book to check copies available for

        Returns:
            int: number of copies available

        """

        self.__cursor.execute('''SELECT copies_available FROM book WHERE id = %s''', (book_id,))

        copies_available = self.__cursor.fetchone()
        return copies_available[0]

    def get_user_id_by_user(self, user: str):
        """
        returns user id by username or email address

        Args:
            user: Username or Email address of the user

        Returns:
            int: ID of the user

        """
        self.__cursor.execute('''SELECT id FROM user WHERE username = %s OR email = %s''',
                              (user, user))

        user_id = self.__cursor.fetchone()
        return user_id[0]

    def change_num_available_copies(self, book_id: int, copies_available: int):
        """
        update number of copies available for a book

        Args:
            book_id: id of the book to change number of copies for
            copies_available: new number of copies available
        """

        self.__cursor.execute('''UPDATE book SET copies_available = %s WHERE book_id = %s''',
                              (copies_available, book_id))

        self.__connection.commit()

    def add_user(self, id_: int, username: str, email: str):
        """
        Adds a user to the GCP database

        Args:
            id_: id of user, same as on RP
            username: username of the user, same as on RP
            email: email address of the user, same as on RP
        """

        self.__cursor.execute('''INSERT INTO user VALUES(?, ?, ?);''', (id_, username, email))
        self.__connection.commit()

    def search_book_by_title(self, title: str):
        """
        Searches database for partial match of title of the book

        Args:
            title: title to be searched

        Returns:
            result_set : result set containing id, title, published_date, copies_available of the matched books
        """

        title = "%" + title + "%"
        self.__cursor.execute('''SELECT id, title, author,  published_date, copies_available 
                                    FROM book WHERE title LIKE %s ORDER BY title ASC''', (title,))

        row = self.__cursor.fetchall()
        return row

    def search_book_by_isbn(self, isbn: str):
        """
        Searches database for partial match of isbn of the book

        Args:
            isbn: isbn of the book to be searched

         Returns:
            result_set : result set containing id, title, published_date, copies_available of the matched books
        """

        isbn = "%" + isbn + "%"
        self.__cursor.execute('''SELECT id, title, author, published_date, copies_available 
                                    FROM book WHERE isbn LIKE (%s) ORDER BY title ASC''', (isbn,))

        row = self.__cursor.fetchall()
        return row

    def search_book_by_author(self, author: str):
        """
        Searches database for partial match of author name of the book

        Args:
            author:  author name to be searched

         Returns:
            result_set : result set containing id, title, published_date, copies_available of the matched books
        """

        author = "%" + author + "%"

        self.__cursor.execute('''SELECT id, title, author, published_date, copies_available 
                                    FROM book WHERE author LIKE %s ORDER BY title ASC''', (author,))

        row = self.__cursor.fetchall()
        return row

    def add_book(self, title: str, isbn: str, published_date: str, author: str, total_copies: int):
        """
        Adds a book to the GCP database

        Args:
            title: title of the book
            isbn: isbn of the book
            published_date: date of publishing the book
            author: author of the book
            total_copies: total copies of the book being added to library
        """

        self.__cursor.execute('''INSERT INTO book (title, isbn, published_date, author, total_copies, copies_available) 
                                    VALUES (%s, %s, %s, %s, %s, %s); ''',
                              (title, isbn, published_date, author, total_copies, total_copies))

        self.__connection.commit()
