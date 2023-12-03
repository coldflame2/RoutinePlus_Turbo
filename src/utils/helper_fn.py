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
    logging.debug(f"Returning 'column_name_value_dict': '{column_name_value_dict}'")
    return column_name_value_dict


def parse_datetime(datetime_str):
    format = "%I:%M %p, %Y-%m-%d"
    return datetime.strptime(datetime_str, format)

def format_datetime(datetime):
    format_str = "%I:%M %p, %Y-%m-%d"
    return datetime.strftime(format_str)


def lighten_color(color, factor=0.1):
    color = QColor(color)
    light_factor = int(100 + factor * 100)
    lightened_color = color.lighter(light_factor)
    return lightened_color.name()


def get_main_window():
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None


def is_value_current(time_to_check):  # Return true if input time matches current time
    if time_to_check == "":
        # logging.debug(f"No time set: {time_to_check}. Empty string. Returning False")
        return False

    try:
        if_time_in_format = if_string_in_am_pm_format(time_to_check)
    except Exception as e:
        logging.error(f" Exception type:{type(e)} while checking if time matches current. (Error Description:{e}")
        return False

    if if_time_in_format:  # If the format is correct (AM/PM)
        # logging.debug(" The input time value is in proper AM/PM format")
        current_time_str = QTime.currentTime().toString('hh:mm AP')  # Get the current time in "01:00 AM/PM"
        if time_to_check == current_time_str:
            # If time matches current time
            # logging.debug(" -The input time matches the current time. Returning TRUE.")
            return True
        else:
            # Current time is not equal to input time
            # logging.debug("The input time value does not match the current time. Returning False.")
            return False
    else:
        # Input time is not in correct format
        logging.debug("The input time value is not in the correct AM/PM format. Returning False")
        return False


def if_string_in_am_pm_format(time_string):
    try:
        # Try to parse the string using the given format
        datetime.strptime(time_string, '%I:%M %p')
        return True
    except ValueError:
        # If parsing fails, the format does not match
        return False


def show_toast(title="", message="", duration=3000):
    try:
        main_win = get_main_window()
        toast = Toast(main_win)
        toast.show_toast(title, message, duration)
        return toast
    except Exception as e:
        logging.error(f" Exception type:{type(e)} in utils.show_toast. (Description:{e}")


def get_qsettings_object(limit_logs, caller=None):
    app_env = os.getenv('APP_ENV')
    q_settings_obj = environment_cls.SETTINGS_VALUES
    return q_settings_obj


def is_input_valid(value, row, col):
    if col == 1:  # Input in second 'End' time column
        try:
            input_format = re.match(r'^\d{1,2}:\d{2}$', value)
            if input_format:
                hour, minute = map(int, value.split(":"))
                if hour < 24 and 0 <= minute < 60:
                    logging.debug(f" Input value is valid and can be split into Hour, Minute")
                    return True
                else:
                    logging.error(f" Input value cannot be split into Hour, Minute")
                    return False
            else:
                logging.error(f" Input value is not in HH:MM Format")

                return False
        except ValueError:
            logging.error(f" ValueError with new input value {value} in r:c={row}:{col}")
            return False

    elif col == 2:  # Input in 'Duration' column
        duration = int(value)
        if duration >= 0:
            return True
        else:
            return False

    elif col == 3:  # Input in 'Task' column
        logging.debug(f" Task Name entered in row {row}")
        return True

    elif col == 4:  # Input in 'Reminder' column
        if value.strip() == '':  # Check for empty string (including strings with only spaces)
            return False
        else:
            try:
                reminder_time = datetime.strptime(value, '%I:%M %p')
                return True
            except ValueError:
                logging.error(f" VALUE ERROR when change in 'Reminder' detected. Input:{value} in r:c={row}:{col}")
                return False


    elif col == 0:
        logging.debug(f" Change detected in 'Start' column (index=0). Input value:{value}. Row:{row}")

    else:
        logging.error(f" Change detected but in some unexpected place. Input:{value} in r:c={row}:{col}")


def hex_to_rgb(input_hex, caller=None):
    if not isinstance(input_hex, str):
        # logging.error(f"ERROR: input_hex must be a string")
        return None

    if len(input_hex) < 7:  # 7 characters including the '#'
        # logging.error(f" input_hex is too short for an RGB color")
        return None

    try:
        hex_color = input_hex.lstrip('#')  # get rid of #
        # Split the hex color into its components. Arguments inside refer to index of characters
        red_hex = hex_color[0:2]  # get from index 0 to 2, not including 2.
        green_hex = hex_color[2:4]
        blue_hex = hex_color[4:6]
    except Exception as e:
        # logging.error(f" Exception during {e}")
        return None

    try:
        # Convert each 'red/blue/green' hex value of base 16 to integer
        red = int(red_hex, 16)
        green = int(green_hex, 16)
        blue = int(blue_hex, 16)
    except ValueError:
        # logging.error(f" input_hex contains invalid characters")
        return None

    except Exception as e:
        logging.error(f" Exception during {e}")
        return None

    color_tuple = (red, green, blue)
    return color_tuple


def testing_method(parent=None, argument=None):
    logging.debug(f" Testing method executed with argument : {argument}")


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in bundled mode (either --onedir or --onefile)
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment, return base path of file that calls the method
        base_path = os.path.abspath('../src')
    return os.path.join(base_path, relative_path)


def task_or_subtask(table, row, qt_itemdatarole_userrole):
    # user_role_constant is Qt.ItemDataRole.UserRole when calling this method.
    task_or_subtask_item = table.item(row, 0)
    if not task_or_subtask_item:
        return None  # or return an appropriate default value or indicator

    task_type = 'task'  # Default value
    if task_or_subtask_item.data(qt_itemdatarole_userrole) == 'subtask':
        task_type = 'subtask'

    return task_type


def add_minutes(data):
    original_time_dt = datetime.strptime(data, "%H:%M")
    new_time_dt = original_time_dt + timedelta(minutes=10)
    new_time_string = new_time_dt.strftime("%H:%M")
    return new_time_string


def ordinal_suffix(n):
    """Return the ordinal suffix of an integer."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix