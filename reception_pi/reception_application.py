import getpass
import json
from datetime import datetime
from sqlite3 import Error
import logging
from passlib.hash import pbkdf2_sha256

from reception_pi.util import reception_database, input_validation

logging.basicConfig(filename="/logs/reception-application.log", filemode='a', level=logging.DEBUG)


class ReceptionApplication(object):
    def __init__(self):
        self.__db_name = self.__get_database_filename()
        self.__db_connection = reception_database.ReceptionDatabase(self.__db_name)

    def __get_database_filename(self):
        """
        Gets name of database form config.json

        Returns: name of the database
        """
        with open('config.json') as json_file:
            data = json.load(json_file)
            return data['db_name']

    def handle_login(self):
        """
        Gets username or email address from user and searches database for the user login credentials.
        Also notifies MasterPi if user is logged in.
        """
        try_login = 1

        # multiple login trials
        while try_login == 1:
            username = input("\nUsername or Email Address: ")
            password = getpass.getpass(prompt='Password: ')

            valid_credentials = False
            # todo: confirm credentials from db
            if valid_credentials:
                # todo: send socket message to MP
                pass
            else:
                option_selected = input("\nInvalid username or password!"
                                        "\nEnter 1 to try again or any other key to go back to the previous menu\n")
                try:
                    try_login = int(option_selected)
                except ValueError:
                    try_login = 1

    def handle_register(self):
        """
        Registers a new user by taking in username, email address and password as input; performing input validation and
        checking for duplicate username or email address in database against already existing users.
        """

        validate_input = input_validation.InputValidation

        while True:
            username = input("\nEnter Username (must be at-least 5 characters, no special characters allowed): ")
            username = username.strip()  # remove leading and trailing spaces
            username_is_valid = validate_input.validate_username(username)

            if not username_is_valid:
                print("Invalid username. Try again.")
                continue

            username_already_exist = self.__db_connection.check_username_already_exist(username)

            if username_already_exist:
                print("Username already exists. Try again.")
                continue

            email = input("\nEnter an Email Address: ")
            email = email.strip()  # remove leading and trailing spaces
            email_is_valid = validate_input.validate_email(email)

            if not email_is_valid:
                print("Invalid Email Address. Try again.")
                continue

            email_already_exit = self.__db_connection.check_email_already_exist(email)

            if email_already_exit:
                print("Email Address already exists. Try again.")
                continue

            password = getpass.getpass(prompt='Password (must be at-least 5 characters, '
                                              'no other special characters apart from * # $ @ ! % ^ allowed): ')
            password = password.strip()  # remove leading and trailing spaces
            password_is_valid = validate_input.validate_password(password)

            if not password_is_valid:
                print("Invalid password. Try again.")
                continue

            password_hash = self.__hash_password()
            self.__db_connection.insert_user(username, email, password_hash)

            print("\nRegistration successful...\n")

    def __hash_password(self, password):
        """
        Takes in string passwords and returns a salted hash

        Acknowledgement: Copyright of https://www.cyberciti.biz/python-tutorials/securely-hash-passwords-in-python/
        used for educational learning only

        Args:
            password: readable string password of user

        Returns:
            string: salted hash of the password
        """

        # rounds = amount of computations used... to slow down brute force on hack
        # salt_size = length of salt in bytes
        password_hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

        return password_hash

    def main(self):
        try:
            self.__db_connection.create_table_user()

            quit_reception_application = False

            # wait for a valid input from user
            while not quit_reception_application:
                option_selected = input("\nPlease select one of the following option: "
                                        "\n\t1. Login\n\t2. Register a new account\n\t3. Quit\n")

                # if user input is not an integer then ask for input again
                try:
                    option_selected = int(option_selected)
                except ValueError:
                    option_selected = 99

                if option_selected == 1:
                    self.handle_login()
                elif option_selected == 2:
                    self.handle_register()
                elif option_selected == 3:
                    quit_reception_application = True
                else:
                    print("\nInvalid Input! Try again.", end="\n")
        except Error:
            logging.warning(e.__str__() + " " + datetime.now().__str__())
        finally:
            self.__db_connection.close_connection()


if __name__ == '__main__':
    ReceptionApplication().main()
