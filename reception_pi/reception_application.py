import getpass
import json
from datetime import datetime
from sqlite3 import Error
import logging
from passlib.hash import pbkdf2_sha256

from util import reception_database, input_validation

logging.basicConfig(filename="./reception_pi/logs/reception-application.log", filemode='a', level=logging.DEBUG)


class ReceptionApplication(object):
    def __init__(self):
        self.__db_name = self.__get_database_filename()
        self.__db_connection = reception_database.ReceptionDatabase(self.__db_name)

    def __get_database_filename(self):
        """
        Gets name of database form config.json

        Returns: name of the database
        """
        with open('./reception_pi/config.json') as json_file:
            data = json.load(json_file)
            return data['database']['test']

    def handle_login(self):
        """
        Gets username or email address from user and searches database for the user login credentials.
        Also notifies MasterPi if user is logged in.
        """
        try_login = 1

        # multiple login trials
        while try_login == 1:
            user = input("\nUsername or Email Address: ")
            password = getpass.getpass(prompt='Password: ')

            row = self.__db_connection.get_password_by_user(user)

            if row is None:
                print("\nUser Not Found! Please try again")
                break

            hash_ = row[0]

            # check if hash is equal to the password
            valid_credentials = self.__verify_hash(password, hash_)

            if valid_credentials:
                print("Logged in....waiting for the sockets to work!")
                pass
            else:
                option_selected = input("\nInvalid username or password!"
                                        "\nEnter 1 to try again or any other key to go back to the previous menu\n")
                try:
                    try_login = int(option_selected)
                except ValueError:
                    try_login = 99

    def handle_register(self):
        """
        Registers a new user by taking in username, email address and password as input; performing input validation and
        checking for duplicate username or email address in database against already existing users.
        """

        validate_input = input_validation.InputValidation

        registration_unsuccessful = True

        while registration_unsuccessful:
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

            email = input("Enter an Email Address: ")
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

            password_hash = self.__hash_password(password)
            self.__db_connection.insert_user(username, email, password_hash)

            print("\nRegistration successful...\n")

            registration_unsuccessful = False

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

    def __verify_hash(self, password, hash_):
        """
        Takes in string passwords and checks if it matches the hash

        Acknowledgement: Copyright of https://www.cyberciti.biz/python-tutorials/securely-hash-passwords-in-python/
        used for educational learning only

        Args:
            hash_: hash of the password to be matched against
            password: readable string password of user

        Returns:
            boolean: True if hash matches the password, otherwise false
        """

        # rounds = amount of computations used... to slow down brute force on hack
        # salt_size = length of salt in bytes
        return pbkdf2_sha256.verify(password, hash_)

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
        except Error as e:
            logging.warning("DB: " + e.__str__() + " " + datetime.now().__str__())
        finally:
            self.__db_connection.close_connection()


if __name__ == '__main__':
    try:
        ReceptionApplication().main()
    except Exception as e:
        logging.warning("RECEPTION_PI: " + e.__str__() + " " + datetime.now().__str__())
