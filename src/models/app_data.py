import logging
import os
import sqlite3

from resources.default import Columns
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
            start_time DATETIME,
            end_time DATETIME,
            duration INTEGER,
            task_name TEXT,
            reminders DATETIME,
            type TEXT,
            position INTEGER
        )
        """
        self.conn.execute(create_table_query)
        self.conn.commit()

    def get_all_entries(self):  # Called in TableModel and set to _data variable
        """
        Retrieve all entries from the 'daily_routine' table and return them as a list of dictionaries.
        """
        logging.debug(f"Fetching all entries from the SQLite database.")

        select_query = "SELECT * FROM daily_routine ORDER BY position ASC"
        cursor = self.conn.execute(select_query)

        if len(cursor.fetchall()) == 0:
            logging.debug(f"No data found in database file. Inserting default tasks from defaults.")
            for each_task_dict in default.DEFAULT_TASKS:
                self.insert_new_row(each_task_dict)
            cursor.close()

        logging.debug(f"Rows data fetched from SQLite. Converting them to datetime objects.")

        cursor = self.conn.execute(select_query)

        formatted_data = []  # to store formatted data after converting string from database to datetime
        for row_data in cursor.fetchall():
            # check data type of each value in the row

            if row_data[Columns.Type.value] == 'main':
                row_data[Columns.StartTime.value] = helper_fn.str_to_dt(
                    row_data[Columns.StartTime.value])

                row_data[Columns.EndTime.value] = helper_fn.str_to_dt(
                    row_data[Columns.EndTime.value])
                row_data[Columns.Reminder.value] = helper_fn.str_to_dt(
                    row_data[Columns.Reminder.value])

                formatted_data.append(row_data)

            else:
                logging.debug("row type is QuickTask")
                formatted_data.append(row_data)

        return formatted_data

    def insert_new_row(self, row_data):
        logging.debug(f"Inserting new task in the database.")
        insert_query = """
        INSERT INTO daily_routine (start_time, end_time, duration, task_name, reminders, type, position)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (row_data[Columns.StartTime.value], row_data[Columns.EndTime.value], row_data[Columns.Duration.value],
                  row_data[Columns.Name.value], row_data[Columns.Reminder.value], row_data[Columns.Type.value],
                  row_data[Columns.Position.value])

        cursor = self.conn.execute(insert_query, params)
        # Fetch the last inserted row ID
        inserted_row_id = cursor.lastrowid

        # Optionally, you can log the inserted row ID
        logging.debug(f"Inserted new task with ID: {inserted_row_id}. Name:{row_data[Columns.Name.value]}")

        return inserted_row_id

    def update_sqlite_data(self, row_data):
        task_name = row_data[Columns.Name.value]
        task_id = row_data[Columns.ID.value]
        task_type = row_data[Columns.Type.value]
        task_position = row_data[Columns.Position.value]

        logging.debug(f"row_data - {row_data}")
        logging.debug(f"Updating task 'Name:{task_name}' in the database. Task ID:{task_id}. Type"
                      f":{task_type}. Position:{task_position}.")

        update_query = """
        UPDATE daily_routine
        SET start_time = :start_time, 
            end_time = :end_time, 
            duration = :duration, 
            task_name = :task_name, 
            reminders = :reminders, 
            type = :type, 
            position = :position
        WHERE id = :id
        """
        try:
            self.conn.execute(update_query, row_data)
        except Exception as e:
            logging.error(f"Exception type: (type{e}). Error:{e}")

    def commit_sqlite_all(self):
        logging.debug(f"Committing all changes to the database.")
        self.conn.commit()

    def delete_sqlite_row(self, task_id):
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

    def delete_all(self):
        logging.debug(f"Deleting all rows from SQLite database.")
        delete_query = "DELETE FROM daily_routine"
        try:
            self.conn.execute(delete_query)
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")

    def get_default_entries(self):
        """
        Retrieves the default data from the predefined source.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the default data.
        """
        default_data = []
        for entry in default.DEFAULT_TASKS:
            self.insert_new_row(entry)
            default_data.append(entry)
        return default_data
