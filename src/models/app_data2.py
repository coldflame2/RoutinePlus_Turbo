import logging
import os
import sqlite3

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

    def execute_query(self, query, params=()):
        """Execute a given SQL query with optional parameters."""
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute(query, params)
            except Exception as e:
                logging.error(f" Exception type:{type(e)} in execute_query method (Error Description:{e}")

            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                return cursor.rowcount  # return number of rows for update/insert/delete operations

    def connect(self):
        """Establish a connection to the SQLite database."""
        if not os.path.exists(os.path.dirname(self.data_file_path)):
            os.makedirs(os.path.dirname(self.data_file_path))
        self.conn = sqlite3.connect(self.data_file_path)

    def update_routine_entry(self, updated_data):
        logging.debug("Updating data and saving to file.")
        query = """
        UPDATE daily_routine
        SET from_time = ?, to_time = ?, duration = ?, task_name = ?, reminders = ?
        WHERE id = ?
        """
        try:
            self.execute_query(
                query, (
                    updated_data['from_time'],
                    updated_data['to_time'],
                    updated_data['duration'],
                    updated_data['task_name'],
                    updated_data['reminders'],
                    updated_data['id'],  # Assuming 'id' is the unique identifier
                    )
                )
            self.conn.commit()  # Commit the changes to the database

        except Exception as e:
            logging.error(f"Exception type: {type(e)} while updating routine entry (Error Description: {e})")

    def create_table(self):
        """Create the 'daily_routine' table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS daily_routine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            from_time TEXT NOT NULL,
            to_time TEXT NOT NULL,
            duration TEXT,
            task_name TEXT,
            reminders TEXT
        )
        """
        self.execute_query(query)

    def get_all_entries(self):
        """Retrieve all entries from the 'daily_routine' table."""
        try:
            routine_data = self.execute_query("SELECT * FROM daily_routine")
            if not routine_data:
                logging.debug("No Routine Data. Filling sample data.")
                return []

            else:
                logging.debug("Routine data available")
                logging.debug(f" 'Routine Data': '{routine_data}'")

                return routine_data
        except Exception as e:
            logging.error(f"Exception while retrieving entries: {e}")
            return []

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

