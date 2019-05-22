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
        self.database.insert_user("test", "test@test.com", "password")
        updated_num_of_users = self.countUsers()

        self.assertEqual(updated_num_of_users, num_of_users + 1)


if __name__ == '__main__':
    unittest.main()
