import datetime
import json
import logging
from util import google_calendar
from util import gcp_database
from util import socket_host

logging.basicConfig(filename="./master_pi/logs/master_application.log", filemode='a', level=logging.DEBUG)


class MasterApplication(object):

    def __init__(self):
        self.__database = gcp_database.GcpDatabase()
        self.__calendar = google_calendar.GoogleCalendar()
        self.__database.create_tables()
        self.__socket = socket_host.SocketHost()

    def __search_book(self):
        """
        Searches for book in the database for partial matches against Title, Author Name or ISBN.
        Returns maximum 5 matches and matches in the following order: title -> author -> isbn
        """

        search_limit = 5  # will return these many results only
        search_again = True

        while search_again:
            search_query = input("\nEnter search query: ")

            if len(search_query) < 1:
                print("\nPlease enter a valid input.")
                continue

            title_matches = self.__database.search_book_by_title(search_query)

            num_title_matches = len(title_matches)
            title_matches = list(title_matches)

            partial_matches = []

            # if title matches are 5 or more then return 5 title matches.
            # Otherwise fill search result with ISBN and Author name matches, until 5 results
            if num_title_matches < search_limit:
                
                if len(title_matches) is not 0:
                    partial_matches = title_matches
                else:
                    partial_matches = [[]]
                
                if len(partial_matches) <= search_limit:

                    author_matches = self.__database.search_book_by_author(search_query)
                    author_matches = list(author_matches)

                    limit = 5 if len(author_matches) > 5 else len(author_matches)

                    for i in range(0, limit):
                        if 0 < len(partial_matches) <= search_limit:
                            partial_matches.append(author_matches[i])
                        else:
                            break

                isbn_matches = self.__database.search_book_by_isbn(search_query)
                isbn_matches = list(isbn_matches)

                limit = 5 if len(isbn_matches) > 5 else len(isbn_matches)

                for i in range(0, limit):
                    if 0 < len(partial_matches) <= search_limit:
                        partial_matches.append(isbn_matches[i])
                    else:
                        break

            else:
                for i in range(0, 5):
                    if 0 < len(partial_matches) <= search_limit:
                        partial_matches.append(title_matches[i])
                    else:
                        break

            if len(partial_matches) > 0:
                print("\n\nMATCHED RESULTS: ")
            else:
                print("\n\nNo Matches found\n\n")

            limit = 5 if len(partial_matches) > 5 else len(partial_matches)

            # print all the matches on the console
            for i in range(0, limit):
                if len(partial_matches[i]) < 6:
                    continue
                print("\n\n\t\tID: {}  \n\tTITLE: {}  \n\tAUTHOR: {} "
                      "\n\tISBN: {} \n\tPUBLISHED DATE: {}  \n\tCOPIES AVAILABLE:  {}"
                      .format(partial_matches[i][0], partial_matches[i][1], partial_matches[i][2],
                              partial_matches[i][3], partial_matches[i][4], partial_matches[i][5])
                      )

            # ask user if want to search again...and repeat again if user presses 1
            user_input = input("\nEnter 1 to search again and any other key to go back to the previous menu: ")

            try:
                user_input = int(user_input)
            except ValueError:
                user_input = 5

            search_again = True if user_input == 1 else False

    def __borrow_book(self, user: str):
        """
        Borrows a book for a user with expected return date as 1 week far from current date
        and adds 2 calender events for issue date and expected return date with information of book and user

        Args:
            user: username or email address of the user
        """

        user_id = self.__database.get_user_id_by_user(user)

        try_again = True

        # continue till user asks to stop
        while try_again:
            valid_input = False
            book_id = 0

            while not valid_input:
                book_id = input("\nEnter book id: ")

                try:
                    book_id = int(book_id)
                except ValueError:
                    print("Invalid Input try again")
                    continue
                valid_input = True

            available_copies = self.__database.get_num_available_copies(book_id)

            # if book is not available, ask if user wants to try to borrow another book
            if available_copies < 0:

                user_input = input("Book not available. Press 1 to continue or "
                                   "any other key to go to the previous menu.")
                try:
                    user_input = int(user_input)
                except ValueError:
                    print("Invaid input try again")
                    user_input = 1

                try_again = True if (user_input == 1) else False

            else:
                # get date of 7 days from now
                issue_date = datetime.date.today().__str__()
                return_date = datetime.date.today() + datetime.timedelta(days=7)
                return_date = return_date.__str__()

                self.__database.borrow_book(user_id, book_id, issue_date, return_date)
                self.__database.update_num_available_copies(book_id, available_copies - 1)

                todays_date = datetime.date.today().__str__()

                # create issue and return date calendar events
                self.__calendar.create_event(user, book_id, "borrowed", todays_date, "Australia/Melbourne")
                self.__calendar.create_event(user, book_id, "expected return", return_date, "Australia/Melbourne")

                user_input = input("\nBook {} successfully borrowed. "
                                   "\nPress 1 to borrow another book or any other key to go to the previous menu: ".format(book_id))

                try:
                    user_input = int(user_input)
                except ValueError:
                    print("Invalid input try again")
                    user_input = 1

                try_again = True if (user_input == 1) else False

    def __return_book(self, user: str):
        """
        Returns the book for the user and make the book available for another issue

        Args:
            user: username or email address of the user
        """

        user_id = self.__database.get_user_id_by_user(user)

        try_again = True

        books_borrowed = self.__database.get_borrowed_book_id_by_user(user_id)

        if len(books_borrowed) is 0:
            print("\nNo books borrowed\n")
            return

        print("\nFollowing books have been borrowed from the library: \n")
        for id_ in books_borrowed:
            book = self.__database.get_book_by_id(id_)
            print("\n\tID: {}  TITLE: {}  ISBN: {} AUTHOR: {}"
                  .format(book[0], book[1], book[2], book[3])
                  )

        # continue till user asks to stop
        while try_again:
            valid_input = False
            borrow_id = 0
            book_id = None

            while not valid_input:
                book_id = input("\nEnter book id to return: ")

                try:
                    book_id = int(book_id)
                except ValueError:
                    print("Invalid Input try again")
                    continue
                valid_input = True

            borrow_id = self.__database.get_borrow_id_by_book_and_user(book_id, user_id)

            book_borrowed = self.__database.confirm_borrow_status(borrow_id, user_id)

            # if book is not borrowed or not borrowed by this user.. then report invalid to the user
            if book_borrowed is False:
                user_input = input("\nInvalid borrow id. Press 1 to try again or "
                                   "anything else to go to the previous menu: ")

                try:
                    user_input = int(user_input)
                except ValueError:
                    print("Invalid Input try again")
                    continue

                if user_input == 1:
                    continue
                else:
                    break

            available_copies = self.__database.get_num_available_copies(book_id)
            self.__database.update_num_available_copies(book_id, available_copies + 1)

            todays_date = datetime.date.today().__str__()

            self.__database.return_book(borrow_id, todays_date)

            user_input = input("\nBook {} successfully returned. "
                               "Press 1 to return another book or any other key to go to the previous menu.: "
                               .format(book_id, borrow_id))

            try:
                user_input = int(user_input)
            except ValueError:
                print("Invalid input try again")
                continue

            try_again = True if (user_input == 1) else False

    def __show_login_menu(self, user):

        print("Welcome! {}\n".format(user))
        option_selected = 5
        while True and option_selected == 5:
            user_input = input("\nEnter the option number to choose the option:\n"
                               "\t1. Search a book\n"
                               "\t2. Borrow a book\n"
                               "\t3. Return a book\n"
                               "\t4. Logout\n\n"
                               "\nSelect an option: ")
            try:
                option_selected = int(user_input)
            except ValueError:
                option_selected = 5

            if option_selected == 1:
                self.__search_book()
                option_selected = 5
            elif option_selected == 2:
                self.__borrow_book(user)
                option_selected = 5
            elif option_selected == 3:
                self.__return_book(user)
                option_selected = 5
            elif option_selected == 4:
                print("Logging out...")
                break
            elif option_selected == 5:
                print("\nWrong Input! Try Again...")

    def close_connection(self):
        """
        releases all database and sockets resources
        """
        self.__socket.close()
        self.__database.close()

    def main(self):
        while True:
            print("Waiting for client...")
            action_string = self.__socket.wait_for_message()
            action_json = json.loads(action_string)
            action_type = action_json["action"]

            if action_type == "register":
                user_id = action_json["id"]
                username = action_json["username"]
                email = action_json["email"]

                self.__database.add_user(user_id, username, email)

            elif action_type == "login":
                self.__show_login_menu(action_json["user"])
                self.__socket.send_message("logout")


if __name__ == '__main__':
    master_application = None
    
    master_application = MasterApplication()
    master_application.main()
    master_application.close_connection()
