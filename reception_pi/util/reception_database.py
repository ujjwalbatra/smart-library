import sqlite3


class ReceptionDatabase(object):
    def __init__(self, db_name):
        self.__db_conn = sqlite3.connect(db_name)
        self.__db_cursor = self.__db_conn.cursor()

    def close_connection(self):
        """
        Releases database resources by closing db cursor and connection.
        """
        self.__db_cursor.close()
        self.__db_conn.close()

    def create_table_user(self):
        """
        Creates a new table user if it doesn't exist.
        """
        self.__db_cursor.execute('''CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username VARCHAR(255) UNIQUE, email VARCHAR(320) UNIQUE, password VARCHAR(255));''')

    def insert_user(self, username: str, email: str, password: str):
        """
        Registers the user into the system.

        Args:
            username: Username of the user.
            email: Email address of the user.
            password: Password of the user
        """

        self.__db_cursor.execute('''INSERT INTO user(username, email, password) VALUES(?, ?, ?)''',
                                 (username, email, password))
        self.__db_conn.commit()

    def check_username_already_exist(self, username: str):
        """
        Checks if a username already exists in the database.

        Args:
            username: Username of the user

        Returns:
            boolean: True if the username already exist, otherwise false

        """
        self.__db_cursor.execute('''SELECT * FROM user WHERE username = ?''', (username,))
        row = self.__db_cursor.fetchall()

        if row:
            return True
        else:
            return False

    def check_email_already_exist(self, email: str):
        """
        Checks if an email address already exists in the database.

        Args:
            email: Email Address of the user

        Returns:
            boolean: True if the username already exist, otherwise false

        """
        self.__db_cursor.execute('''SELECT * FROM user WHERE email = ?''', (email,))
        row = self.__db_cursor.fetchall()

        if row:
            return True
        else:
            return False

    def get_password_by_user(self, user: str):
        """
        Check login credentials of a user by matching user or email address with password.

        Args:
            user: Email Address or username of the user
            password: Password of the user

        Returns:
            boolean: True if user and password matched, otherwise false
        """
        self.__db_cursor.execute('''SELECT password FROM user WHERE (email = ? OR username = ?)''',
                                 (user, user))
        row = self.__db_cursor.fetchone()

        return row
