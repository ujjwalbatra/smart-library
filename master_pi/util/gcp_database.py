import json
import MySQLdb


class GcpDatabase:
    HOST = "35.197.173.168"
    USER = "root"
    PASSWORD = "RmitUniversityPiot"
    DATABASE = "SmartLibrary"

    def __init__(self, connection=None):
        if connection is None:
            connection = MySQLdb.connect(GcpDatabase.HOST, GcpDatabase.USER,
                                         GcpDatabase.PASSWORD, GcpDatabase.DATABASE)
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
            string:
        """
        with open('./master_pi/config.json') as json_file:
            data = json.load(json_file)
            return data['gcp']['host'], data['gcp']['database'], data['gcp']['user'], data['gcp']['password']

    def create_tables(self):
        """
        creates tables user(id, username_email), book(is, title, isbn, published_date, author)
        and borrow_record(id, book_id, user_id, status, issue_date, returned_date)
        """
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS user (id INT PRIMARY KEY AUTO_INCREMENT, 
                            username VARCHAR(255) UNIQUE, email VARCHAR(320) UNIQUE);''')

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS book (id INT PRIMARY KEY AUTO_INCREMENT, 
                                    title TEXT, isbn VARCHAR(20), published_date DATE, author TEXT);''')

        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_record (id INT PRIMARY KEY AUTO_INCREMENT, user_id INT NOT NULL,
        book_id INT NOT NULL, status enum ('borrowed', 'returned'), issue_date DATE NOT NULL,returned_date DATE,
        FOREIGN KEY (book_id) REFERENCES book(id), 
        FOREIGN KEY (user_id) REFERENCES user(id));''')


if __name__ == '__main__':
    haha = GcpDatabase()
    haha.create_tables()
    haha.close()
