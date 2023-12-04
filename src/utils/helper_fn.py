import re
import sys
import os
import logging
from datetime import datetime, timedelta

from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import QApplication, QMainWindow

from src.dev.environment import environment_cls


def get_environment_cls(limit_logs=True, caller=None):
    class_name = environment_cls.__class__.__name__  # Get the class name as a string
    logging.debug(f"Returning Env_Config Class:{class_name} from caller:{caller}.")
    return environment_cls


def dict_factory(cursor, row):
    """
    Convert a database row to a dictionary using two for loops for clarity.
    This is called whenever rows are fetched after executing 'SELECT' query.

    Parameters:
    cursor (Cursor): A database cursor object that provides metadata about the columns.
    row (Row): A single row from the database query results.

    Returns:
    dict: A dictionary where keys are column names and values are row data.
    """

    # Initialize an empty dictionary to hold the column name-value pairs.
    column_name_value_dict = {}

    # Initialize an empty list to store column names.
    column_names = []

    # First loop: Extract column names from the cursor description.
    for column_metadata in cursor.description:  # cursor.description object is tuple = metadata for all columns
        # Extract the column name from the column metadata (first element).
        column_name = column_metadata[0]

        # Append the column name to the list.
        column_names.append(column_name)

    # Second loop: Iterate over the column names and corresponding row data.
    for column_index, column_name in enumerate(column_names):
        # Retrieve the corresponding value from the row using the column index.
        column_value = row[column_index]

        # Assign the value to the respective column name in our dictionary.
        column_name_value_dict[column_name] = column_value

    # Return the dictionary containing column names and their corresponding values.
    return column_name_value_dict


def string_to_datetime(input_string):
    format_of_string = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(input_string, format_of_string)


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in bundled mode (either --onedir or --onefile)
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment, return base path of file that calls the method
        base_path = os.path.abspath('../src')
    return os.path.join(base_path, relative_path)


def calculate_duration(from_time, to_time):
    """Calculate duration between from_time and to_time in minutes."""
    if from_time and to_time:
        duration = (to_time - from_time).total_seconds() / 60
        return int(duration)  # Return duration as integer minutes
    return 0


def calculate_to_time(from_time, duration):
    """Calculate to_time based on from_time and duration."""
    if from_time and duration:
        to_time = from_time + timedelta(minutes=duration)
        return to_time
    return from_time

def calculate_from_time(to_time, duration):
    if to_time and duration:
        from_time = to_time - timedelta(minutes=duration)
        return from_time
    return to_time