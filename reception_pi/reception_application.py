import getpass


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
        pass

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
