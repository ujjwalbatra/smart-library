import json
import unittest
import reception_database


class TestReceptionDatabase(unittest.TestCase):

    def setUp(self):
        with open('./reception_pi/config.json') as json_file:
            data = json.load(json_file)
            database_name = data['database']['test']
            database_name = './reception_pi/' + database_name

        self.database = reception_database.ReceptionDatabase(database_name)
        self.connection = self.database.get_connection()
        self.cursor = self.connection.cursor()

        self.cursor.execute("DROP TABLE IF EXISTS user;")
        self.connection.commit()

        self.database.create_table_user()

    def countUsers(self):
        self.cursor.execute("SELECT count(*) FROM user")
        return self.cursor.fetchone()[0]

    def tearDown(self):
        try:
            self.connection.close()
            self.database.close_connection()
        except Exception:
            pass
        finally:
            self.connection = None
            self.database = None

    def test_insert_user(self):

        num_of_users = self.countUsers()
        self.database.insert_user("test123", "test@test.com", "password")
        updated_num_of_users = self.countUsers()
        self.assertEqual(updated_num_of_users, num_of_users + 1)

    def test_check_username_already_exist(self):
        self.database.insert_user("test1234", "test1234@test.com", "password")
        result = self.database.check_username_already_exist("test1234")
        self.assertEqual(result, True)

        result = self.database.check_username_already_exist("123213331aas231231231231234")
        self.assertEqual(result, False)

    def test_check_email_already_exist(self):
        self.database.insert_user("test12345", "test12345@test.com", "password")
        result = self.database.check_email_already_exist("test12345@test.com")
        self.assertEqual(result, True)

        result = self.database.check_email_already_exist("test12avsdwefq233234231345@test.com")
        self.assertEqual(result, False)

    def test_get_password_by_user(self):
        self.database.insert_user("test1234569999", "test123456@test.com", "password")
        result = self.database.get_password_by_user("test1234569999")
        print(result[0])
        self.assertEqual(result[0], "password")

        result = self.database.get_password_by_user("test12avsdwefq233234231345@test.com")
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
