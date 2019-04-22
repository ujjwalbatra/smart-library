import datetime

from util import google_calendar, gcp_database


class MasterApplication(object):

    def __init__(self):
        self.__database = gcp_database.GcpDatabase()

    def main(self):
        self.__database.create_tables()
        date_today = datetime.date.today().strftime('%Y-%m-%d')
        self.__database.add_book("abcdef", "123321123", date_today, "dkdkdkdk", 2)
        print(self.__database.search_book_by_isbn("123"))
        print(self.__database.search_book_by_author("dkd"))
        print(self.__database.search_book_by_title("abc"))


if __name__ == '__main__':
    master_application = MasterApplication()
    master_application.main()
