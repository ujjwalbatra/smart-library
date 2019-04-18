import getpass

from reception_pi.util import input_validation


class ReceptionApplication(object):

    def handle_login(self):
        """
        gets username or email address from user and searches database for the user login credentials.
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

        validate_input = input_validation.InputValidation

        while True:
            email = input("\nEnter an Email Address: ")
            email = email.strip()  # remove leading and trailing spaces
            email_is_valid = validate_input.validate_email(email)

            if not email_is_valid:
                print("Invalid Email Address. Try again.")
                continue

            username = input("\nEnter Username (must be at-least 5 characters, no special characters allowed): ")
            username = username.strip()  # remove leading and trailing spaces
            username_is_valid = validate_input.validate_username(username)

            if not username_is_valid:
                print("Invalid username. Try again.")
                continue

            password = getpass.getpass(prompt='Password (must be at-least 5 characters, '
                                              'no other special characters apart from * # $ @ ! % ^ allowed): ')
            password = password.strip()  # remove leading and trailing spaces
            password_is_valid = validate_input.validate_password(password)

            if not password_is_valid:
                print("Invalid password. Try again.")
                continue

    def main(self):
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


if __name__ == '__main__':
    ReceptionApplication().main()
