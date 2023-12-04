import logging
from datetime import datetime, timedelta

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

from src.models.app_data import AppData
from src.resources.default import COLUMN_KEYS, VISIBLE_HEADERS
from src.utils import helper_fn


class TableModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()

        self.visible_headers = VISIBLE_HEADERS  # Visible headers for UI
        self.column_keys = COLUMN_KEYS  # Keys (str) used internally

        self.app_data = AppData()
        try:
            self._data = self.app_data.get_all_entries()
            logging.debug(f"Data in TableModel Constructor: '{self._data}'")
        except Exception as e:
            logging.error(f"Exception in TableModel init: {e}")
            self.app_data.close()  # Close the database connection on failure
            raise  # Re-raise the exception to signal the failure

    def add_new_task(self):
        logging.debug("Adding new task")

        # Initialize the new_id variable
        new_id = 1

        # Check if there are existing tasks in self._data
        if self._data:
            # Initialize max_id to a value that's lower than any expected ID (e.g., 0)
            max_id = 0

            # Iterate through each task in self._data to find the maximum ID
            for task in self._data:
                # Update max_id if the current task's ID is greater
                if task['id'] > max_id:
                    max_id = task['id']

            # Set new_id to be one greater than the maximum ID found
            new_id = max_id + 1

        # Calculate the new task's times based on the last task
        index_to_insert = len(self._data)
        row_above = index_to_insert - 1

        last_end = self._data[row_above]['to_time'] if index_to_insert > 0 else None
        new_end = last_end + timedelta(minutes=10) if last_end else None
        reminder = last_end - timedelta(minutes=5)

        # New task data
        data_to_insert = {
            'id': new_id,
            'from_time': last_end,
            'to_time': new_end,
            'duration': 10,
            'task_name': 'New Task',  # Change as needed
            'reminders': reminder
            }

        # Insert the new row
        self.beginInsertRows(QModelIndex(), index_to_insert, index_to_insert)
        self._data.append(data_to_insert)
        self.endInsertRows()

    def save_to_db_in_model(self):
        """Save the modified data back to the database."""
        logging.debug("Saving data in db file")
        self.app_data.save_all(self._data)

    def close_database(self):
        logging.debug("Closing the database.")
        self.app_data.close()  # Use the close method of AppData
        logging.debug("Database closed.")

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        This method is called by the view to retrieve the data for a given index. The role parameter specifies what kind of data is being requested (e.g., display data, tooltip data). It doesn't change data.

        """

        if not index.isValid() or role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        row_data = self._data[index.row()]
        column_key = self.column_keys[index.column()]

        if column_key in ["from_time", "to_time", "reminders"]:
            datetime_value = row_data.get(column_key, None)

            if datetime_value:

                try:
                    return_datetime_string = datetime_value.strftime("%I:%M %p")  # Datetime is converted to string for view
                    return return_datetime_string

                except Exception as e:
                    logging.error(f"Exception type:{type(e)}  (Error Description:{e}")
                    return None

            else:
                return None

        if column_key in ["duration"]:
            """Convert duration integer """
            duration_value = row_data.get(column_key, None)
            if duration_value:
                if isinstance(duration_value, int):
                    return_duration_string = f"{duration_value} Minutes"  # Integer is converted to string for view
                    return return_duration_string
                else:
                    logging.error(f"duration value isn't integer. value:{duration_value}")
                    return None
            else:
                return None

        return row_data.get(column_key, None)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        logging.debug(f"'setData' method called with value:'{value}'.")

        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        if value is None:
            return False

        row = index.row()
        column_key = self.column_keys[index.column()]

        if column_key in ['task_name']:
            return self.handle_task_name_input(index, row, value, role)

        if column_key in ['duration']:
            return self.handle_duration_input(index, row, value, role)

        if column_key in ["from_time", "to_time"]:
            return self.set_and_update_fields_and_notify(value, row, column_key)

    def handle_task_name_input(self, index, row, value, role):
        task_col_key = 'task_name'
        original_task_name = self._data[row][task_col_key]

        if original_task_name == value:
            logging.debug(f"Same value in 'Task' column. Returning without any changes.")
            return False

        else:
            return self.set_task_name_and_notify(index, row, value, role)

    def handle_duration_input(self, index, row, value, role):
        logging.debug(f"Change in duration")
        focus_widget = QApplication.focusWidget()

        original_duration = self._data[row]['duration']

        if value == "":
            logging.debug(f"Input value is empty:'{value}'")
            return False

        try:
            input_duration_int = helper_fn.strip_text(value)

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when striping input duration string (Error Description:{e}")
            return False

        if input_duration_int == 0 or input_duration_int < 0:
            QMessageBox.warning(focus_widget, "Can't be zero.", "The task has to be at least of one minute duration.")
            return False

        if original_duration != input_duration_int:  # If the input value is not equal to original
            if row == (len(self._data) - 1):
                logging.debug(f"Row edited is the last row. Index:'{row}'. Setting 'Duration' and updating 'to_time'.")
                return self.on_duration_input_same_row(index, row, input_duration_int, role)

            else:
                logging.debug(f"Next row exists. Calling methods to update its values.")
                return self.on_duration_input_next_row(index, row, input_duration_int, role)

        else:
            logging.debug(f"Same value in 'Duration'. Returning without any changes.")
            return False

    def on_duration_input_same_row(self, index, row, input_duration_int, role):

        try:
            original_from = self._data[row]['from_time']
            new_to = original_from + timedelta(minutes=input_duration_int)

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when updating 'from' after setting new duration (Error Description:{e}")
            return False

        try:
            self._data[row]['duration'] = input_duration_int  # Set the value to new_duration integer
            self._data[row]['to_time'] = new_to  # Set the 'To' value to new calculated one

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when setting input duration and calculated new 'to_time.' (Error Description:{e}")
            return False

        logging.debug(f"setData in 'duration'({input_duration_int} and 'to_time' {new_to}. Emitting dataChanged signals now.")
        self.dataChanged.emit(index, index, [role])  # Emit for 'From_time'

        to_time_index = self.createIndex(row, 1)  # to_time column index = 1
        self.dataChanged.emit(to_time_index, to_time_index, [role])  # Emit for 'to_time'

        return True

    def on_duration_input_next_row(self, index, row, input_duration_int, role):

        focus_widget = QApplication.focusWidget()

        next_row = row + 1
        original_from_next_row = self._data[next_row]['from_time']
        original_to_next_row = self._data[next_row]['to_time']
        original_duration_next_row = self._data[next_row]['duration']

        logging.debug(
            f"Next row values."
            f"start:'{original_from_next_row}'. To:{original_to_next_row}. Duration:{original_duration_next_row}"
            )

        try:
            original_duration = self._data[row]['duration']
            max_possible_duration = original_duration + original_duration_next_row

            if input_duration_int < max_possible_duration:
                # Duration same row

                # set
                logging.debug(f"Setting input duration ({input_duration_int}) in the same row.")
                self._data[row]['duration'] = input_duration_int  # Set the value to new_duration integer

                # Emit
                logging.debug(f"Emitting dataChanged for Duration in the same row.")
                self.dataChanged.emit(index, index, [role])

                # "To Time" same row

                # set
                logging.debug(f"Setting new 'to_time' in the same row.")
                original_from_same_row = self._data[row]['from_time']
                new_to_same_row = original_from_same_row + timedelta(minutes=input_duration_int)
                self._data[row]['to_time'] = new_to_same_row
                logging.debug(f"new 'to_time' same row:{new_to_same_row} set.")

                # Emit
                to_time_same_row_index = self.createIndex(row, 1)
                self.dataChanged.emit(to_time_same_row_index, to_time_same_row_index, [role])

                # "From Time" next row

                # set
                logging.debug(f"Setting new 'from_time' in the next row.")
                self._data[next_row]['from_time'] = new_to_same_row  # set same as 'to_time' of row above

                # Emit
                logging.debug(f"Emitting dataChanged for 'from_time' in the next row.")
                new_from_next_row_index = self.createIndex(row, 0)
                self.dataChanged.emit(new_from_next_row_index, new_from_next_row_index, [role])

                # 'Duration' next row

                # set
                logging.debug(f"Setting new 'duration' in the next row.")
                original_to_next_row = self._data[next_row]['to_time']
                new_time_diff_next_row = (original_to_next_row - new_to_same_row)  # This is in timedelta
                self._data[next_row]['duration'] = int(new_time_diff_next_row.total_seconds() / 60)

                # Emit
                logging.debug(f"Emitting dataChanged for 'duration' in the next row.")
                duration_next_row_index = self.createIndex(next_row, 2)  # duration column index = 2
                self.dataChanged.emit(duration_next_row_index, duration_next_row_index, [role])  # Emit for 'duration'

                return True

            else:
                logging.warning(f"Duration cannot be more than {max_possible_duration}")
                QMessageBox.warning(
                    focus_widget, f"Invalid. Input less than {max_possible_duration}",
                    "The task below has to be at least of one minute duration."
                    f"Therefore the duration for this task cannot be more than {max_possible_duration}."
                    )
                return False

        # Value isn't an integer
        except ValueError:
            QMessageBox.warning(focus_widget, "Invalid Duration", "Please input a valid number for duration.")
            logging.error(f"Input duration value isn't a valid integer. Input: {input_duration_int}")
            return False

        except Exception as e:
            QMessageBox.warning(focus_widget, "Unknown Exception", "Please restart.")
            logging.error(f"Exception type:{type(e)} after input in duration. Input value: {input_duration_int}. Error:{e}")
            return False

    def set_and_update_fields_and_notify(self, value, row, column_key):

        if column_key == 'duration':  # String input to Integer
            logging.debug(f"Change in duration")
            original_duration = self._data[row]['duration']

            try:
                input_duration_int = helper_fn.strip_text(value)

            except Exception as e:
                logging.error(f"Exception type:{type(e)} when striping input duration string (Error Description:{e}")
                return False

            if original_duration != input_duration_int:  # If the input value is not equal to original
                duration_input_handled = self.handle_duration_input(row, input_duration_int)
                return duration_input_handled

            else:
                logging.debug(f"Same value in 'Duration'. Returning without any changes.")
                return False

        if column_key == 'from_time':
            logging.debug(f"Change detected in 'from_time'. Input value:'{value}'")
            return self.handle_from_input(row, value)

        if column_key == 'to_time':
            logging.debug(f"Change detected in 'to_time'. Input value:'{value}'")
            return self.handle_to_input(row, value)

    def handle_from_input(self, row, user_input_value):
        focus_widget = QApplication.focusWidget()

        if row == 0:
            logging.debug(f"Cannot change the starting time of the day.")
            QMessageBox.warning(
                focus_widget, "START time of the first task cannot be changed.",
                "Cannot change the START time of the first task."
                "First task always begins from midnight. "
                )
            return False

        try:
            input_from_dt = self.parse_datetime(user_input_value)
            self._data[row]['from_time'] = input_from_dt

            return True

        # Value isn't an integer
        except ValueError:
            QMessageBox.warning(focus_widget, "Invalid 'START' time.", "Please input a valid START time for the task.")
            logging.error(f"Input value isn't a valid time in format: 09:00 am/pm. Input: {user_input_value}")
            return False

        except Exception as e:
            QMessageBox.warning(focus_widget, "Invalid Input", "Please input a valid START time for the task.")
            logging.error(f"Exception type:{type(e)} after input in duration. Input value: {user_input_value}. Error:{e}")
            return False

    def handle_to_input(self, row, user_input_value):
        focus_widget = QApplication.focusWidget()

        try:
            input_to_time = self.parse_datetime(user_input_value)
            self._data[row]['to_time'] = input_to_time
            return True

        # Value isn't an integer
        except ValueError:
            QMessageBox.warning(focus_widget, "Invalid 'END' time.", "Please input a valid END time for the task.")
            logging.error(f"Input value isn't a valid time in format: 09:00 am/pm. Input: {user_input_value}")
            return False

        except Exception as e:
            QMessageBox.warning(focus_widget, "Invalid Input", "Please input a valid END time for the task.")
            logging.error(f"Exception type:{type(e)} after input in duration. Input value: {user_input_value}. Error:{e}")
            return False

    def set_task_name_and_notify(self, index, row, value, role):
        column_key = 'task_name'

        try:
            self._data[row][column_key] = value  # Task Name Set
            self.dataChanged.emit(index, index, [role])
            logging.debug(f"Emitting dataChanged signal after updating task_name at row:{row}.")
            return True

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when setting task name. Error: {e}")
            return False

    def update_other_fields(self, row, column_key):

        if column_key in ['duration', 'from_time']:
            # Update to_time
            logging.debug(f"Change in 'Duration' or 'Start'. 'new_duration': '{new_duration}'")

            new_to_time = helper_fn.calculate_to_time(from_time, duration)
            logging.debug(f"Change in 'Duration' or 'Start'. 'new_duration': '{new_duration}'")

            self._data[row]['to_time'] = new_to_time
            to_time_index = self.index(row, self.column_keys.index('to_time'))
            self.dataChanged.emit(to_time_index, to_time_index, [Qt.ItemDataRole.EditRole])

            # Update the row below
            if len(self._data) > row + 1:
                from_time_row_below = self._data[row + 1]['from_time']
                duration_row_below = helper_fn.calculate_duration(new_to_time, from_time_row_below)

                if duration_row_below > 0:
                    self._data[row + 1]['from_time'] = new_to_time
                    self._data[row + 1]['duration'] = duration_row_below
                    from_time_index_row_below = self.index(row + 1, self.column_keys.index('from_time'))
                    duration_index_row_below = self.index(row + 1, self.column_keys.index('duration'))
                    self.dataChanged.emit(from_time_index_row_below, duration_index_row_below, [Qt.ItemDataRole.EditRole])
                else:
                    # Revert to maximum possible duration for the current row
                    max_duration_possible = helper_fn.calculate_duration(self._data[row]['from_time'], from_time_row_below)
                    new_to_time_max = helper_fn.calculate_to_time(self._data[row]['from_time'], max_duration_possible)
                    self._data[row]['to_time'] = new_to_time_max
                    self._data[row]['duration'] = max_duration_possible

                    to_time_index = self.index(row, self.column_keys.index('to_time'))
                    duration_index = self.index(row, self.column_keys.index('duration'))
                    self.dataChanged.emit(to_time_index, duration_index, [Qt.ItemDataRole.EditRole])
                    logging.debug(f"Duration is in negative {duration_row_below}. Reverting to maximum possible duration.")

        if column_key in ['from_time', 'to_time']:
            # Update duration
            pass
            # new_duration = helper_fn.calculate_duration(from_time, to_time)
            # logging.debug(f"Change in START or END time. new_duration would be: '{new_duration}'")
            #
            # self._data[row]['duration'] = new_duration  # Value Set
            #
            # logging.debug(f"New duration value {new_duration} set at row:{row}.")
            #
            # duration_index = self.index(row, self.column_keys.index('duration'))
            # self.dataChanged.emit(duration_index, duration_index, [Qt.ItemDataRole.EditRole])

        return True

    def parse_datetime(self, value):
        """Parse datetime fields from string."""
        try:
            format_str = "%I:%M %p, %Y-%m-%d"
            return datetime.strptime(f'{value}, 2023-01-01', format_str)

        except ValueError:
            QMessageBox.warning(self.parent_widget, "Invalid", "Please input a valid time in the format: 'HH:MM am/pm'.")
            logging.error(f"Input value isn't a valid integer. Input: {value}")
            return None
        except Exception as e:
            logging.error(f"Exception when parsing datetime in setData: {type(e)} - {e}")
            return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """
        This method provides the data for the header given the section (which is the column index for horizontal headers and row index for vertical headers), the orientation (horizontal or vertical), and the role.

        The view calls this method to get the text that should be displayed in the header of a particular column or row.
        """

        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            # Return the visible header label for the given section (column index)
            if 0 <= section < len(self.visible_headers):  # Section is like column index. 0 section means 'Start'
                return self.visible_headers[section]

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def index(self, row, column, parent=QModelIndex()):
        """When the view requests the data for a cell at a particular row and column, it calls this method to get an index that points to that cell's data."""
        if parent.isValid() or row >= len(self._data) or column >= len(self.column_keys):
            return QModelIndex()
        return self.createIndex(row, column, self._data[row])

    def parent(self, index):  # used for hierarchical models (ignored for models like table)
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data) if not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()):
        return len(self.column_keys) if not parent.isValid() else 0