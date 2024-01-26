import unittest
import os
import sqlite3
from unittest.mock import patch
from cli_app import process_files, MyHandler, cli_app

class TestCLIApp(unittest.TestCase):
    def setUp(self):
        self.db_connection = sqlite3.connect(':memory:')
        cursor = self.db_connection.cursor()
        cursor.execute(
            "CREATE TABLE files (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, file_name TEXT, "
            "upload_time TEXT, file_size INTEGER)"
        )
        self.db_connection.commit()

    def tearDown(self):
        self.db_connection.close()

    def test_process_files(self):
        folder_path = '/path/to/test_folder'
        os.makedirs(folder_path, exist_ok=True)
        file1_path = os.path.join(folder_path, 'test1.gltf')
        file2_path = os.path.join(folder_path, 'test2.zip')
        with open(file1_path, 'w') as file1:
            file1.write('Test GLTF content')
        with open(file2_path, 'w') as file2:
            file2.write('Test ZIP content')

        process_files(folder_path, self.db_connection)

        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM files")
        result = cursor.fetchall()

        self.assertEqual(len(result), 2)

    @patch('cli_app.Observer')
    @patch('cli_app.MyHandler', side_effect=MyHandler)
    def test_cli_app(self, mock_handler, mock_observer):
        with patch('builtins.input', return_value='/path/to/test_folder'):
            cli_app()

        mock_observer.assert_called_once()
        mock_observer.return_value.schedule.assert_called_once()

if __name__ == '__main__':
    unittest.main()
