import logging
import os
import sqlite3

from src.resources import default
from src.utils import helper_fn


class AppData:

    def __init__(self):
        self.create_dirs()
        self.conn = None
        self.connect()
        self.create_table()

    def create_dirs(self):
        env_config = helper_fn.get_environment_cls(False, caller='AppData')
        self.data_file_path = os.path.join(env_config.DATA_FOLDER_PATH, f'{env_config.DATA_FILE_NAME}.db')
        self.backup_folder_path = env_config.BACKUP_FOLDER_PATH

    def connect(self):
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
        logging.debug("Creating the 'daily_routine' table if it doesn't exist.")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_routine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_time DATETIME,
            to_time DATETIME,
            duration INTEGER,
            task_name TEXT,
            reminders DATETIME,
            type TEXT,
            task_sequence INTEGER
        )
        """
        self.conn.execute(create_table_query)
        self.conn.commit()

    def get_all_entries(self):  # Called in TableModel and set to _data variable
        """
        Retrieve all entries from the 'daily_routine' table and return them as a list of dictionaries.
        """
        logging.debug(f"Fetching all entries from the SQLite database.")

        select_query = "SELECT * FROM daily_routine ORDER BY task_sequence ASC"
        cursor = self.conn.execute(select_query)

        if len(cursor.fetchall()) == 0:
            logging.debug(f"No data found in database file. Inserting default tasks from defaults.")
            for each_task_dict in default.default_tasks:
                self.insert_new_row(each_task_dict)
            cursor.close()

        logging.debug(f"Rows data fetched from SQLite. Converting them to datetime objects.")

        cursor = self.conn.execute(select_query)

        data_dt_format = []  # to store formatted data after converting string from database to datetime
        for each_row_data in cursor.fetchall():
            each_row_data['from_time'] = helper_fn.string_to_datetime(each_row_data['from_time'])
            each_row_data['to_time'] = helper_fn.string_to_datetime(each_row_data['to_time'])
            each_row_data['reminders'] = helper_fn.string_to_datetime(each_row_data['reminders'])
            data_dt_format.append(each_row_data)

        return data_dt_format

    def insert_new_row(self, row_data):
        logging.debug(f"Inserting new task in the database.")
        insert_query = """
        INSERT INTO daily_routine (from_time, to_time, duration, task_name, reminders, type, task_sequence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (row_data['from_time'], row_data['to_time'], row_data['duration'],
                  row_data['task_name'], row_data['reminders'], row_data['type'],
                  row_data['task_sequence'])

        cursor = self.conn.execute(insert_query, params)

        # Fetch the last inserted row ID
        inserted_row_id = cursor.lastrowid

        # Optionally, you can log the inserted row ID
        logging.debug(f"Inserted new task with ID: {inserted_row_id}")

        return inserted_row_id

    def update_sqlite_data(self, task_data):
        logging.debug(f"Updating task in the database.")
        update_query = """
        UPDATE daily_routine
        SET from_time = ?, to_time = ?, duration = ?, task_name = ?, reminders = ?, type = ?, task_sequence = ?
        WHERE id = ?
        """
        params = (task_data['from_time'], task_data['to_time'], task_data['duration'],
                  task_data['task_name'], task_data['reminders'], task_data['type'],
                  task_data['task_sequence'], task_data['id'])
        self.conn.execute(update_query, params)

    def commit_sqlite_all(self):
        logging.debug(f"Committing all changes to the database.")
        self.conn.commit()

    def delete_task(self, task_id):
        logging.debug(f"Deleting task from the database.")
        delete_query = "DELETE FROM daily_routine WHERE id = ?"
        self.conn.execute(delete_query, (task_id,))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        self.close()


"""
Sequence of events for AppData class analysis:

1. Directories are created.

2. Connection to database is established.

3. Table 'daily routine' is created if it doesn't exist. (This table is created only once when the app is run for the first time.)

4. Data is fetched from the database, sorted by task_sequence, and returned to the TableModel class. In case of no data, default tasks are inserted in the database by inserting default task dict to the sqlite data. In case of data, the string data in ISO format from sqlite is converted to datetime objects and returned to the TableModel class.

5. When the user clicks 'Save' button, the data is either updated or inserted in the database. If the task has a valid ID, it is updated. If the task doesn't have a valid ID, it is inserted as a new task.

"""