import json
import MySQLdb
from datetime import date


class GcpDatabase:

    def __init__(self, connection=None):
        if connection is None:
            host, database, user, password = self.__get_database_details()
            connection = MySQLdb.connect(host, user, password, database)
        self.__connection = connection
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
                                    title TEXT UNIQUE, isbn VARCHAR(20), published_date DATE, author TEXT, 
                                    total_copies INT DEFAULT 1, copies_available INT DEFAULT 1);''')

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_record (id INT PRIMARY KEY AUTO_INCREMENT, 
                                    user_id INT NOT NULL, book_id INT NOT NULL, status enum ('borrowed', 'returned'), 
                                    issue_date DATE DEFAULT CURRENT_DATE NOT NULL, 
                                    return_date DATE, actual_return_date DATE DEFAULT NULL,
                                    FOREIGN KEY (book_id) REFERENCES book(id), 
                                    FOREIGN KEY (user_id) REFERENCES user(id));''')

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

    def add_book(self, title: str, isbn: str, published_date: date, author: str, total_copies: str):
        """
        Adds a book to the GCP database

        Args:
            title: title of the book
            isbn: isbn of the book
            published_date: date of publishing the book
            author: author of the book
            total_copies: total copies of the book being added to library
        """

        self.__cursor.execute('''INSERT INTO book(title, isbn, published_date, author, total_copies, copies_available) 
                                    VALUES(?, ?, ?, ?, ?, ?); ''',
                              (title, isbn, published_date, author, total_copies, total_copies))

        self.__connection.commit()
