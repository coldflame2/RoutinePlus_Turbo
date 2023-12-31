import logging
import re
from datetime import datetime

from PyQt6.QtCore import QModelIndex

from resources.default import Columns
from utils import helper_fn


class ModelUtilityService:
    def __init__(self, model):
        self.model = model

    def insert_row_with_data(self, row, data_to_insert):
        if row < 0 or row >= self.model.rowCount():
            logging.error(f"IndexError: Row index {row} is out of range")
            return False

        if data_to_insert is None:
            logging.warning(f"Null value not allowed for row {row}")
            return False

        try:
            logging.debug(f"Beginning to insert new row at index: '{row}'")
            self.model.beginInsertRows(QModelIndex(), row, row)
            self.model.set_row_data(row, data_to_insert)
            self.model.endInsertRows()

        except Exception as e:
            logging.error(f"Exception type: (type{e}). Error:{e}")
            return False

        try:
            self.insert_row_to_sqlite(row, data_to_insert)
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return False

        return True

    def insert_row_to_sqlite(self, row, data_to_insert):
        row_id = self.model.app_data.insert_new_row(data_to_insert)
        self.model.set_item_in_model(row, 'id', row_id)

    def delete_row_and_data(self, row):
        logging.debug(f"Deleting row: '{row}'")
        self.model.beginRemoveRows(QModelIndex(), row, row)

        try:
            row_id = self.model.get_item_from_model(row, 'id')
            self.model.delete_row_from_model(row)  # Delete from model
            self.model.app_data.delete_sqlite_row(row_id)  # Delete from SQLite file using row ID

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when deleting row (Error Description:{e}")
            return False

        self.model.endRemoveRows()
        logging.debug(f"Row {row} deleted from model and SQLite database.")
        return True

    def validate_and_format(self, value, row, column_key):
        """ Validate the user input for each column and return for the validated and formatted value. """
        if column_key in [Columns.ID.value, Columns.Type.value, Columns.Position.value]:
            logging.debug(f"Not supposed to change these columns' data by UI interaction.")
            return False
        elif column_key in [Columns.StartTime.value, Columns.EndTime.value, Columns.Reminder.value]:
            logging.debug(f"Validating input ('{value}') at '{column_key}' column.")
            return self.validate_time(value)
        elif column_key == Columns.Duration.value:
            logging.debug(f"Validating input ('{value}') at '{column_key}' column.")
            return self.validate_duration(value)
        elif column_key == Columns.Name.value:
            logging.debug(f"Validating input ('{value}') at '{column_key}' column.")
            return self.validate_task_name(value, row)
        else:
            # Handle other columns if needed
            logging.debug(f"Validating input ('{value}') at '{column_key}' column.")
            return False

    def validate_time(self, value):
        value = value.strip()  # Remove leading and trailing spaces

        if value == "":
            logging.debug(f"Time value is empty: '{value}'")
            raise ValueError(f"Time value is empty: '{value}'")

        # Regular expression pattern to match the specified formats
        pattern = r'^(0?[1-9]|1[0-2])([:/.;-]?([0-5][0-9]))?\s?(AM|PM)?$'

        # Match the input with the pattern
        match = re.match(pattern, value, re.IGNORECASE)

        if match:
            logging.debug(f"Time value input matches the regex pattern: '{value}'")

            hour = match.group(1)  # Capturing group for hours
            minute = match.group(3) if match.group(3) else "00"  # Capturing group for minutes, default to "00"

            # Get AM/PM and capitalize it. Default to 'AM' if not provided
            am_pm = match.group(4).upper() if match.group(4) else 'AM'

            # Format the time
            time_new = f"{hour}:{minute} {am_pm}"

            # Convert to datetime object
            format_str = "%I:%M %p, %Y-%m-%d"
            time_obj = datetime.strptime(f'{time_new}, 2023-01-01', format_str)

            logging.debug(f"Time value input validated and returning the formatted datetime object: '{time_obj}'")

            return time_obj

        else:
            logging.error(f"Time value input does not match the regex pattern: '{value}'")
            return False

    def validate_duration(self, value):
        value = value.strip()
        try:
            duration_value_int = helper_fn.duration_text_to_int(value)
            logging.debug(f"Duration value after stripping text: '{duration_value_int}'")
        except ValueError:
            logging.error(f"ValueError. While validating duration, could not convert string '{value}' to "
                          f"integer.")
            raise ValueError(f"Duration value is not numeric: '{value}'")
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            raise e

        if duration_value_int == "":
            logging.debug(f"Duration value is empty: '{duration_value_int}'")
            raise ValueError(f"Duration value is empty: '{duration_value_int}'")
        if not isinstance(duration_value_int, int):
            logging.debug(f"Duration value is not numeric: '{duration_value_int}'")
            raise ValueError(f"Duration value is not numeric: '{duration_value_int}'")
        if int(duration_value_int) < 0:
            logging.debug(f"Duration value is less than 0: '{duration_value_int}'")
            raise ValueError(f"Duration value is less than 0: '{duration_value_int}'")

        logging.debug(f"Duration value input is valid: '{duration_value_int}'")
        return duration_value_int

    def validate_task_name(self, value, row):
        value = value.strip()
        if value == "":
            logging.debug(f"Task name value is empty: '{value}'")
            raise ValueError(f"Task name value is empty: '{value}'")

        # Get task name value and update/append row info to it
        # return self.get_row_metadata(value, row)
        return value

    def get_row_metadata(self, value, row):
        logging.debug(f"Updating row info for row: '{row}'")
        task_id = self.model.get_item_from_model(row, Columns.ID.value)
        task_type = self.model.get_item_from_model(row, Columns.Type.value)
        position = self.model.get_item_from_model(row, Columns.Position.value)

        metadata_pattern = re.compile(r"\((\d+), (\d+), (\w+), (\w+)\)$")
        match = metadata_pattern.search(value)

        new_metadata = f" ({row}, {task_id}, {task_type}, {position})"
        if match:
            # Replace the old metadata with the new one
            value = metadata_pattern.sub(new_metadata, value)
        else:
            # Append the new metadata to the task name
            value += new_metadata

        return value

    def format_for_view(self, row, column_key, row_data):
        """ Format the data for view. """

        row_type = row_data.get(Columns.Type.value)
        if row_type == 'QuickTask':
            return self.format_quick_task(column_key, row_data)

        if column_key in [Columns.StartTime.value, Columns.EndTime.value, Columns.Reminder.value]:
            return helper_fn.dt_to_str(row_data.get(column_key))

        if column_key == Columns.Duration.value:
            return helper_fn.duration_int_to_text(row_data.get(column_key))

        return row_data.get(column_key)

    def format_quick_task(self, column_key, row_data):
        if column_key == Columns.EndTime.value:
            # Return Task Name in EndTime column (Because QuickTask column is spanned at this index)
            return row_data.get(Columns.Name.value)
        if column_key == Columns.StartTime.value:
            return row_data.get(Columns.Position.value)  # Return Position in StartTime column
        if column_key == Columns.Reminder.value:
            return "QT"  # Return QT in Reminder column
        return None

