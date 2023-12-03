import logging
import os
import sqlite3

from src.resources import default
from src.utils import helper_fn


class AppData:
    instance_count_data = 0

    def __init__(self):
        logging.debug(f"AppData class constructor starting.")
        self.make_directories()
        self.conn = None
        self.connect()
        self.create_table()

        logging.debug(f"AppData class constructor successfully initialized.")

    def make_directories(self):
        env_config = helper_fn.get_environment_cls(False, caller='AppData')
        self.data_folder_path = os.path.join(env_config.APP_FOLDER_PATH, env_config.DATA_FOLDER_NAME)
        os.makedirs(self.data_folder_path, exist_ok=True)
        self.data_file_path = os.path.join(self.data_folder_path, env_config.DATA_FILE_NAME)

        self.backup_folder = os.path.join(self.data_folder_path, env_config.BACKUP_FOLDER_NAME)
        os.makedirs(self.backup_folder, exist_ok=True)

    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.data_file_path)
            self.conn.row_factory = helper_fn.dict_factory  # Set custom row factory that returns dictionary
            logging.info(f"Successfully connected to the database at {self.data_file_path}.")
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to the database. Error: {e}")

    def create_table(self):
        """Create the 'daily_routine' table if it doesn't exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_routine (
            id INTEGER PRIMARY KEY,
            from_time DATETIME,
            to_time DATETIME,
            duration TEXT,
            task_name TEXT,
            reminders TEXT
        )
        """
        self.conn.execute(create_table_query)
        self.conn.commit()

    def get_all_entries(self):  # Called in TableModel and set to _data variable
        """
        Retrieve all entries from the 'daily_routine' table.

        :Return:
        All data in a list of dictionaries.
        """
        logging.debug(f"Getting all entries.")
        select_query = "SELECT * FROM daily_routine"

        try:
            cursor = self.conn.execute(select_query)
            """
            fetchall() is a list of dictionaries.
            row_factory returns a dictionary for one row, but fetchall compiles all dictionaries into a list.
            """
            rows_data = cursor.fetchall()  # List of dictionaries

        except Exception as e:
            logging.error(f"Error fetching data: {type(e)}. {e}")
            return []  # Called in TableModel

        if len(rows_data) == 0:
            logging.debug(f"No data found in database file. Inserting default task: {default.default_tasks}")
            for each_task_dict in default.default_tasks:
                self.insert_row_data(each_task_dict)
            return default.default_tasks

        existing_data_formatted = []  # to store formatted data after converting string from database to datetime
        for each_row_data in rows_data:
            each_row_data['from_time'] = helper_fn.string_to_datetime(each_row_data['from_time'])
            each_row_data['to_time'] = helper_fn.string_to_datetime(each_row_data['to_time'])

            existing_data_formatted.append(each_row_data)
        logging.debug(f"Data found in database file. Returning existing data: {existing_data_formatted}")
        return existing_data_formatted

    def save_all(self, data_to_save):
        """ Update or insert entries in the database based on provided data. """

        try:
            string_formatted = []  # to store textual data from database after converting to DateTime
            for each_row_data in data_to_save:
                string_formatted.append(each_row_data)

            for entry in string_formatted:

                if self.record_exists(entry['id']):
                    self.update_record(entry)
                else:

                    self.insert_row_data(entry)
        except Exception as e:
            logging.error(f" Exception type:{type(e)} while saving (Error Description:{e}")

    def record_exists(self, record_id):
        """ Check if a record exists in the database. """
        query = "SELECT 1 FROM daily_routine WHERE id = ?"
        cursor = self.conn.execute(query, (record_id,))
        return cursor.fetchone() is not None

    def update_record(self, record):
        """ Update a specific record in the database. """
        update_query = """
        UPDATE daily_routine
        SET from_time = ?, to_time = ?, duration = ?, task_name = ?, reminders = ?
        WHERE id = ?
        """
        self.conn.execute(update_query, (
        record['from_time'], record['to_time'], record['duration'], record['task_name'], record['reminders'],
        record['id']))

        self.conn.commit()

    def insert_row_data(self, row_data):
        """ Write method to save to the file """
        logging.debug(f"Inserting row data to SQLite file. Input type:{type(row_data)}. Data:{row_data}")
        # Assuming updated_data is a dictionary with the required keys
        insert_query = """
        INSERT INTO daily_routine (id, from_time, to_time, duration, task_name, reminders)
        VALUES (:id, :from_time, :to_time, :duration, :task_name, :reminders)
        """
        self.conn.execute(insert_query, row_data)
        self.conn.commit()


    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        self.close()
