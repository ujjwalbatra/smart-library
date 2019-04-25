import datetime
from util import google_calendar, gcp_database


class MasterApplication(object):

    def __init__(self):
        self.__database = gcp_database.GcpDatabase()
        self.__database.create_tables()

    def __search_book(self):
        """
        Searches for book in the database for partial matches against Title, Author Name or ISBN.
        Returns maximum 5 matches and matches in the following order: title -> author -> isbn
        """

        search_limit = 5  # will return these many results only
        search_again = False

        while search_again:
            search_query = input("\nEnter search query:")

            if len(search_query) < 0:
                print("\nPlease enter a valid input.")
                continue

            partial_matches = None  # to keep all title, isbn and author matches
            title_matches = self.__database.search_book_by_title(search_query)

            num_title_matches = len(title_matches)

            # if title matches are 5 or more then return 5 title matches.
            # Otherwise fill search result with ISBN and Author name matches, until 5 results
            if num_title_matches < search_limit:
                partial_matches = title_matches

                isbn_matches = self.__database.search_book_by_isbn(search_query)

                for i in isbn_matches:
                    if len(partial_matches) < search_limit:
                        partial_matches = partial_matches.extend(isbn_matches[i])
                    else:
                        break

            if len(partial_matches) < search_limit:
                author_matches = self.__database.search_book_by_author(search_query)

                for i in author_matches:
                    if len(partial_matches) < search_limit:
                        partial_matches = partial_matches.extend(author_matches[i])
                    else:
                        break

            # print all the matches on the console
            for match in partial_matches:
                print("MATCHED RESULTS: \n\tID: {}  TITLE: {}  AUTHOR: {}  PUBLISHED DATE: {}  COPIES AVAILABLE:  {}"
                      .format(match[0], match[1], match[2], match[3], match[4])
                      )

            # ask user if want to search again...and repeat again if user presses 1
            user_input = input("\nEnter 1 to search again and any other key to go back to the previous menu.")

            try:
                user_input = int(user_input)
            except ValueError:
                user_input = 5

            search_again = True if user_input == 1 else False

    def __borrow_book(self, user: str):
        """
        Borrows a book for a user with expected return date as 1 week far from current date

        Args:
            user: username or email address of the user
        """

        user_id = self.__database.get_user_id_by_user(user)

        try_again = True

        # continue till user asks to stop
        while try_again:
            valid_input = False

            while not valid_input:
                book_id = input("\nEnter book id")

                try:
                    book_id = int(book_id.strip())
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
                    user_input = int(user_input.strip())
                except ValueError:
                    break

                try_again = True if (user_input == 1) else False

            else:
                # get date of 7 days from now
                return_date = datetime.date.today() + datetime.timedelta(days=7)
                return_date = return_date.strftime("%Y-%M-%D").__str__()

                self.__database.borrow_book(user_id, book_id, return_date)
                self.__database.change_num_available_copies(book_id, available_copies - 1)

                user_input = input("\nBook {} successfully borrowed. Press 1 to borrow "
                                   "another book or any other key to go to the previous menu.".format(book_id))

                try:
                    user_input = int(user_input.strip())
                except ValueError:
                    break

                try_again = True if (user_input == 1) else False

    def __return_book(self, user: str):
        pass

    def main(self):
        user = "coming from socket"
        # self.__database.add_book("abcdef", "123321123", date_today, "dkdkdkdk", 2)

        print("Welcome! {}".format(user))
        option_selected = 5
        while True and option_selected == 5:
            user_input = input("\nEnter the option number to choose the option:\n"
                               "\t1. Search a book\n"
                               "\t2. Borrow a book\n"
                               "\t3. Return a book\n"
                               "\t4. Logout")
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
                self.__return_book()
                option_selected = 5
            elif option_selected == 4:
                pass  # TODO: logout messages sent using socket
            elif option_selected == 5:
                print("\nWrong Input! Try Again...")


if __name__ == '__main__':
    master_application = MasterApplication()
    master_application.main()
