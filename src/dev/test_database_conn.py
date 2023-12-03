import sqlite3

from src.models.app_data import AppData


def test_db_connection(file_path):
    try:
        conn = sqlite3.connect(file_path)
        print("Successfully connected to the database.")
        conn.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")

file_path = AppData().data_file_path
print(file_path)
# Replace 'your_database_file.db' with your actual database file path
test_db_connection(file_path)