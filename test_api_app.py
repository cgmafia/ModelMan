import unittest
import json
from unittest.mock import patch
from api_app import app

class TestAPIApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_get_all_files_endpoint(self):
        response = self.client.get('/files')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)

    def test_get_file_by_filename_endpoint(self):
        filename = 'test_file.gltf'
        response = self.client.get(f'/file/{filename}')
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 404)  # Assuming the file is not present in the in-memory SQLite database

if __name__ == '__main__':
    unittest.main()
