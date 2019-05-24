"""
reception_application.py
====================================
The core module of my smart library's reception pi
"""

import getpass
import json
from datetime import datetime
from sqlite3 import Error
import logging
from passlib.hash import pbkdf2_sha256
from util import reception_database
from util import input_validation
from util import socket_client
from util import face_util

logging.basicConfig(filename="./reception_pi/logs/reception_application.log", filemode='a', level=logging.DEBUG)


class ReceptionApplication(object):
    """
    main controller for reception pi.
    """

    def __init__(self):
        self.__db_name = './reception_pi/' + self.__get_database_filename()
        self.__db_connection = reception_database.ReceptionDatabase(self.__db_name)
        self.__socket_client = socket_client.SocketClient()
        self.__face_util = face_util.FaceUtil()

    def __get_database_filename(self):
        """
        Gets name of database form config.json


        Returns:
            string: name of th database
        """
        with open('./reception_pi/config.json') as json_file:
            data = json.load(json_file)
            return data['database']['production']

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
                print("Logging in to master...")

                data_for_mp = {'action': 'login', 'user': user}
                json_data_for_mp = json.dumps(data_for_mp)

                status = self.__socket_client.send_message_and_wait(json_data_for_mp)
                print(status)

                if status == "logout":
                    try_login = 0
                    print("Logged out by master")
                elif status == "FAILURE":
                    print("Failed to connect to master")

            else:
                option_selected = input("\nInvalid username or password!"
                                        "\nEnter 1 to try again or any other key to go back to the previous menu\n")
                try:
                    try_login = int(option_selected)
                except ValueError:
                    try_login = 99

    def handle_login_with_face(self):
        """
        Captures the user's face and matches it against registered user's faces
        Also notifies MasterPi if user is logged in.
        """
        try_login = 1

        # multiple login trials
        while try_login == 1:
            print("\nLook at camera to login...")
            recognised_users = self.__face_util.identify_face()

            if not recognised_users:
                print("\nNo face detected! Please try again")
                return

            if len(recognised_users) > 1:
                print("\nMultiple faces detected! Please try again")
                return

            user = recognised_users[0]

            row = self.__db_connection.get_password_by_user(user)

            if row is None:
                print("\nUser no longer exists! Please try again")
                return

            print("Logging in to master...")

            data_for_mp = {'action': 'login', 'user': user}
            json_data_for_mp = json.dumps(data_for_mp)

            status = self.__socket_client.send_message_and_wait(json_data_for_mp)
            print(status)

            if status == "logout":
                try_login = 0
                print("Logged out by master")
            elif status == "FAILURE":
                print("Failed to connect to master")
                break

    def handle_register(self):
        """
        Registers a new user by taking in username, email address and password as input; performing input validation and
        checking for duplicate username or email address in database against already existing users.
        And notifies MP about the new registration
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

            print("\nPlease look at camera to register face")
            self.__face_util.register_face(username)

            password_hash = self.__hash_password(password)
            self.__db_connection.insert_user(username, email, password_hash)

            print("\nRegistering user...")

            user_id = self.__db_connection.get_user_id(username)

            data_for_mp = {'action': 'register', 'id': user_id, 'username': username, 'email': email}
            json_data_for_mp = json.dumps(data_for_mp)

            status = self.__socket_client.send_message(json_data_for_mp)

            if status == "SUCCESS":
                print("Registration successful\n")
            elif status == "FAILURE":
                print("Failed to connect to master\n")

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
                option_selected = input("\nPlease select one of the following option:\n"
                                        "\t1. Login\n"
                                        "\t2. Login with facial recognition\n"
                                        "\t3. Register a new account\n"
                                        "\t4. Quit\n"
                                        "\nSelect an option: ")

                # if user input is not an integer then ask for input again
                try:
                    option_selected = int(option_selected)
                except ValueError:
                    option_selected = 99

                if option_selected == 1:
                    self.handle_login()
                elif option_selected == 2:
                    self.handle_login_with_face()
                elif option_selected == 3:
                    self.handle_register()
                elif option_selected == 4:
                    quit_reception_application = True
                else:
                    print("\nInvalid Input! Try again.", end="\n")

        except Error as error:
            logging.warning("DB: " + error.__str__() + " " + datetime.now().__str__())
        finally:
            self.__db_connection.close_connection()


if __name__ == '__main__':
    try:
        ReceptionApplication().main()
    except Exception as e:
        logging.warning("RECEPTION_PI: " + e.__str__() + " " + datetime.now().__str__())
