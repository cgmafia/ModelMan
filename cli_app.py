import os
import sqlite3
import zipfile
import subprocess
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import click

# Function to process files and update SQLite database
def process_files(folder_path, db_connection):
    cursor = db_connection.cursor()

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.gltf', '.glb', '.zip')):
                compress_gltf_glb(os.path.join(root, file), os.path.join(root, 'compressed_' + file))
                time.sleep(3)

                if os.path.exists(os.path.join(root, 'compressed_' + file)):
                    file_path = os.path.join(root, 'compressed_' + file)
                else:
                    file_path = os.path.join(root, file)

                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    if file.endswith('.zip'):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            for zip_file in zip_ref.namelist():
                                if zip_file.endswith(('.gltf', '.glb')):
                                    extracted_path = os.path.join(root, zip_file)
                                    zip_ref.extract(zip_file, extracted_path)
                                    compress_gltf_glb(os.path.join(extracted_path, zip_file), os.path.join(extracted_path, 'compressed_' + zip_file))
                                    size = os.path.getsize(extracted_path)
                                    cursor.execute(
                                        "INSERT INTO files (file_path, file_name, upload_time, file_size) VALUES (?, ?, ?, ?)",
                                        (extracted_path, zip_file, timestamp, size)
                                    )
                    else:
                        size = os.path.getsize(file_path)
                        cursor.execute(
                            "INSERT INTO files (file_path, file_name, upload_time, file_size) VALUES (?, ?, ?, ?)",
                            (file_path, file, timestamp, size)
                        )
                    

    db_connection.commit()


def compress_gltf_glb(input_file_path, output_file_path):
    cmd = "gltfpack -i " + input_file_path + " -o " + output_file_path
    result = subprocess.run(cmd)

# Event handler to detect changes in the folder
class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        process_files(folder_path, db_connection)


@click.command()
@click.option('--folder', prompt='Enter the folder path:', help='Path of the folder to monitor.')
def cli_app(folder):
    global folder_path, db_connection
    folder_path = folder

    # Initialize SQLite database
    db_connection = sqlite3.connect('files.db')
    cursor = db_connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, file_name TEXT, "
        "upload_time TEXT, file_size INTEGER)"
    )

    # Process existing files
    process_files(folder_path, db_connection)

    # Set up folder monitoring
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=True)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    cli_app()
