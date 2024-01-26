import json
from flask import Flask, jsonify, request
import sqlite3
import logging as log

app = Flask(__name__)

class FileCollection():
    file_list = []

    def __init__(self, name):
        self.name = name
    
    def addFiles(self, file):
        self.file_list.append(file)

    def showAll(self):
        return self.file_list


class FileItem:
    def __init__(self, path, name, time, size):
        self.path = path
        self.name = name
        self.time = time
        self.size = size



class ModelManApp:

    def __init__(self):
        pass

    # Endpoint to get all files from the database
    @app.route('/files', methods=['GET'])
    def get_all_files():
        conn = sqlite3.connect('files.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files")
        data = cursor.fetchall()
        conn.close()
        log.info("Getting all files")

        file_list = FileCollection("newFile")
        for item in data:
            singleFile = (item[0], item[1], item[2],  item[3])
            file_list.addFiles(singleFile)

        return file_list.showAll()

    # Endpoint to get file path and name by filename
    @app.route('/file/<filename>', methods=['GET'])
    def get_file_info(filename):
        conn = sqlite3.connect('files.db')
        cursor = conn.cursor()
        cursor.execute("SELECT file_path, file_name, upload_time, file_size FROM files WHERE file_name=?", (filename,))
        data = cursor.fetchone()
        conn.close()
        log.info("returning %s", filename)
        if data:
            file_info = FileItem(data[0], data[1], data[2], data[3])
            return file_info.to_json()
        else:
            return jsonify({'error': 'File not found'}), 404

# Entry point for the Flask app
if __name__ == '__main__':
    log.info('Starting App')
    app.run(debug=True)
