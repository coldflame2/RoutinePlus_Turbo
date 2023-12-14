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

            """
            By default, SQLite3 returns each row as a tuple. sqlite3.row row_factory returns the special 'Row' object.

            But after assigning row_factory to custom dict_factory, fetchall() returns a list of dictionaries.
            Also note, dict_factory returns a dictionary for one row, but fetchall compiles all dictionaries into a list.
            """

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
            duration INTEGER,
            task_name TEXT,
            reminders DATETIME
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
        logging.debug(f"Fetching all entries from the SQLite database.")

        select_query = "SELECT * FROM daily_routine"
        cursor = self.conn.execute(select_query)

        try:
            rows_data = cursor.fetchall()  # List of dictionaries. Data type of 'Value' for each pair fetched from SQLite as string.
        except Exception as e:
            logging.error(f"Error fetching data: {type(e)}. {e}")
            return []  # Called in TableModel

        if len(rows_data) == 0:
            logging.debug(f"No data found in database file. Inserting default task: {default.default_tasks}")
            for each_task_dict in default.default_tasks:
                self.insert_row_data(each_task_dict)
            return default.default_tasks

        logging.debug(f"Rows data fetched from SQLite. Converting them to datetime objects.")

        existing_data_formatted = []  # to store formatted data after converting string from database to datetime
        for each_row_data in rows_data:
            each_row_data['from_time'] = helper_fn.string_to_datetime(each_row_data['from_time'])
            each_row_data['to_time'] = helper_fn.string_to_datetime(each_row_data['to_time'])
            each_row_data['reminders'] = helper_fn.string_to_datetime(each_row_data['reminders'])

            existing_data_formatted.append(each_row_data)
        logging.debug(f"Data found in database file. Returning existing data.")
        return existing_data_formatted

    def save_all(self, data_from_model):
        """ Update or insert entries in the database based on provided data. """
        logging.debug(f"Saving entire data from model to database.")

        try:
            row = 0  # Only for logging
            for each_row_data in data_from_model:
                logging.debug(f"---Data in row {row} from the model:'{each_row_data}'")

                if self.does_row_exist(each_row_data['id']):  # Check if record exists by checking the unique ID
                    logging.debug(f"Same ID found, thus the row exists already. Updating the row with the new data.")

                    try:
                        self.update_row(each_row_data)  # Update the row with the data

                    except Exception as e:
                        logging.error(f"Exception type:{type(e)} when updating a row. (Error Description:{e}")

                else:
                    logging.debug(f"New row. Inserting row data.")

                    try:
                        self.insert_row_data(each_row_data)  # Insert the data in the row

                    except Exception as e:
                        logging.error(f"Exception type:{type(e)} when inserting row data. (Error Description:{e}")

                row += 1  # Only for logging

        except Exception as e:
            logging.error(f" Exception type:{type(e)} while saving (Error Description:{e}")

    def does_row_exist(self, record_id):
        """ Check if a record exists in the database.

        This query selects a constant value (1) from the daily_routine table but only for the row where the id column matches the record_id passed to the method.

        """

        query = "SELECT 1 FROM daily_routine WHERE id = ?"
        cursor = self.conn.execute(query, (record_id,))  # the trailing comma is necessary to make it a tuple even with a single element.
        return cursor.fetchone() is not None

    def update_row(self, row_data):
        logging.debug(f"Updating data in a row in the SQLite file. Input type:{type(row_data)}.")

        update_query = """
        UPDATE daily_routine
        SET from_time = ?, to_time = ?, duration = ?, task_name = ?, reminders = ?
        WHERE id = ?
        """

        self.conn.execute(
            update_query, (
                row_data['from_time'], row_data['to_time'], row_data['duration'],
                row_data['task_name'], row_data['reminders'],
                row_data['id'])
            )

        self.conn.commit()

    def insert_row_data(self, row_data):
        logging.debug(f"Inserting data in a row in the SQLite file. Input type:{type(row_data)}.")

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