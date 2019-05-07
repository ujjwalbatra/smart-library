import unittest

from reception_pi.util import input_validation


class TestInputValidation(unittest.TestCase):

    def test_validate_email(self):
        validate_input = input_validation.InputValidation

        # testing right format
        email = "fake@address.com"
        output = validate_input.validate_email(email)
        self.assertEqual(output, True)

        # testing wrong format
        email = "wrongaddress.com"
        output = validate_input.validate_email(email)
        self.assertEqual(output, False)

        # testing wrong format
        email = "wrongaddresscom"
        output = validate_input.validate_email(email)
        self.assertEqual(output, False)

        # testing wrong format
        email = "@wrong.com"
        output = validate_input.validate_email(email)
        self.assertEqual(output, False)

    def test_validate_username(self):
        validate_input = input_validation.InputValidation

        # testing right format
        username = "Jinzeng123"
        output = validate_input.validate_username(username)
        self.assertEqual(output, True)

        # testing minimum 5 length
        username = "Jin1"
        output = input_validation.InputValidation.validate_username(username)
        self.assertEqual(output, False)

        # testing space
        username = "Jin 1"
        output = validate_input.validate_username(username)
        self.assertEqual(output, False)

        # testing Special character
        username = "Jin1!"
        output = validate_input.validate_username(username)
        self.assertEqual(output, False)

    def test_validate_password(self):
        validate_input = input_validation.InputValidation

        # testing right format
        password = "Jinzeng123!"
        output = validate_input.validate_password(password)
        self.assertEqual(output, True)

        # testing space
        password = "Jinzeng 1"
        output = validate_input.validate_password(password)
        self.assertEqual(output, False)

        # testing min 6 length
        password = "Jin1"
        output = validate_input.validate_password(password)
        self.assertEqual(output, False)


if __name__ == '__main__':
    unittest.main()
