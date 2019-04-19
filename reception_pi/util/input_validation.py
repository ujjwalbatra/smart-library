from validate_email import validate_email
import re


class InputValidation(object):

    @staticmethod
    def validate_email(email: str):
        """
        checks whether the email address is valid or not. Accepted email format is _______@______._________

        Args:
            email: email address to be validated

        Returns:
            boolean: a boolean specifying whether the email is valid or not
        """

        is_valid = validate_email(email)

        return is_valid

    @staticmethod
    def validate_username(username: str):
        """
        checks whether the username is of length 5 minimum, and contains only a-z (lowercase characters)
        or A-Z (uppercase characters) or 0-9 (digits). **no special characters and space allowed**

        Args:
            username: username to be validated

        Returns:
            boolean: a boolean specifying whether the username is valid or not
        """

        is_valid = re.search("\s+", username)
        if is_valid:
            return False

        is_valid = re.search("[0-9a-zA-Z]{5,}", username)

        if is_valid:
            return True

        return False

    @staticmethod
    def validate_password(password: str):
        """
        checks whether the username is of length 6 minimum, and contains only a-z (lowercase characters),
        A-Z (uppercase characters), 0-9 (digits) or special characters (supports only: * # $ @ ! % ^).
        **no spaces allowed**

        Args:
            password: password to be validated

        Returns:
            boolean: a boolean specifying whether the username is valid or not
        """

        is_valid = re.search("\s+", password)
        if is_valid:
            return False

        is_valid = re.search("[0-9a-zA-Z*#$@!%^]{6,}", password)

        if is_valid:
            return True

        return False
