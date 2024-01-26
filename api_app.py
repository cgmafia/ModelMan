from flask import Flask, jsonify, request
import sqlite3
import logging as log

app = Flask(__name__)

# Endpoint to get all files from the database
@app.route('/files', methods=['GET'])
def get_all_files():
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files")
    data = cursor.fetchall()
    conn.close()
    log.info("Getting all files")

    file_list = []
    for item in data:
        file_list.append({
            'file_path': item[1],
            'file_name': item[2],
            'upload_time': item[3],
            'file_size': item[4]
        })

    return jsonify({'files': file_list})

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
        fname = data[1].split('.')[0]
        ext = data[1].split('.')[1]
        file_info = {'path': data[0] + '/' + data[1], 'extension': ext, 'createdAt': data[2], 'size': data[3],}
        return jsonify(file_info)
    else:
        return jsonify({'error': 'File not found'}), 404

# Entry point for the Flask app
if __name__ == '__main__':
    log.info('Starting App')
    app.run(debug=True)
