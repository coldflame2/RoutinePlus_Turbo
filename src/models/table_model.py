import logging
from datetime import datetime
from typing import Any, Dict, List

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from src.models.app_data import AppData
from src.resources.default import VISIBLE_HEADERS, Columns


class TableModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()

        self.visible_headers = VISIBLE_HEADERS  # Visible headers for UI
        self.column_keys = [column.value for column in Columns]

        self.initiate_data()

    def initiate_data(self):
        self.app_data = AppData()

        try:
            self._data: List[Dict[str, Any]] = list(self.app_data.get_all_entries())

        except Exception as e:
            logging.error(f"Exception in TableModel init: {e}")
            self.app_data.close()  # Close the database connection on failure
            raise  # Re-raise the exception to signal the failure

    def get_item(self, row, column_key):
        try:
            logging.debug(f"Retrieving '{column_key}' value at row index: {row}")
            return self._data[row][column_key]
        except KeyError:
            logging.error(f"KeyError: Column key '{column_key}' not found in row {row}")
            return None
        except IndexError:
            logging.error(f"IndexError: Row index {row} is out of range")
            return None

    def set_item(self, row, column_key, value):
        """
        Updates the value for a specified row and column.

        Args:
            row (int): The row index.
            column_key (str): The key for the column.
            value (Any): The new value to set.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        if row < 0 or row >= len(self._data):
            logging.error(f"IndexError: Row index {row} is out of range")
            return False

        if column_key not in self.column_keys:
            logging.error(f"KeyError: Column key '{column_key}' is invalid")
            return False

        if value is None:
            logging.warning(f"Null value not allowed for row {row}, column '{column_key}'")
            return False

        try:
            self._data[row][column_key] = value
            column_index = self.column_keys.index(column_key)
            item_index = self.createIndex(row, column_index)
            self.dataChanged.emit(item_index, item_index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
            logging.debug(f"Updated row {row}, column '{column_key}' with value '{value}'")
            return True
        except Exception as e:
            logging.error(f"Exception when updating row {row}, column '{column_key}': {e}")
            return False

    def insert_new_row(self, index, data_to_insert):
        self.beginInsertRows(QModelIndex(), index, index)

        try:
            self._data.insert(index, data_to_insert)  # Inset in model's database

            # Set returned ID after the method to insert new row in sqlite file
            self._data[index][Columns.ID.value] = self.app_data.insert_new_row(data_to_insert)

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when inserting new row (Error Description:{e}")

        self.endInsertRows()

    def delete_row_and_data(self, row):
        logging.debug(f"Deleting row: '{row}'")
        self.beginRemoveRows(QModelIndex(), row, row)

        try:
            row_id = self._data[row]['id']  # Get the row ID before deleting
            self._data.pop(row)  # Delete from model's database
            self.app_data.delete_task(row_id)  # Delete from SQLite file using row ID

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when deleting row (Error Description:{e}")
            return False

        self.endRemoveRows()
        logging.debug(f"Row {row} deleted from model and SQLite database.")
        return True

    def save_to_database_file(self):
        logging.debug("Looping rows in model and calling update method in AppData.")

        for row in range(self.rowCount()):
            row_data = {}
            for column_key in self.column_keys:
                row_data[column_key] = self._data[row][column_key]
                logging.debug(f" -- Collecting data: {column_key} = {self._data[row][column_key]}.")

            logging.debug(f" -- Updating row {row} data: {row_data} inside SQlite database.")
            self.app_data.update_sqlite_data(row_data)

        self.app_data.commit_sqlite_all()
        logging.debug("SUCCESS: Date updated and saved on SQLite database file.")

    def close_database(self):
        logging.debug("Closing the database.")
        self.app_data.close()  # Use the close method of AppData
        logging.debug("Database closed.")

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if not index.isValid() or role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        row_data = self._data[index.row()]
        column_key = self.column_keys[index.column()]

        if row_data.get(Columns.Type.value) == 'QuickTask':
            # Return values for ID, type, and sequence
            columns_only_in_dev = [Columns.ID.value, Columns.Type.value, Columns.Position.value]
            if column_key in columns_only_in_dev:
                value = row_data.get(column_key, None)
                return value
            else:
                # Return name for all other fields like from, end, duration, etc.
                QuickTask_name = row_data.get(Columns.Name.value, None)
                return QuickTask_name

        time_col_keys = [Columns.StartTime.value, Columns.EndTime.value, Columns.Reminder.value]
        if column_key in time_col_keys:  # convert datetime to string for view
            datetime_value = row_data.get(column_key, None)

            if datetime_value:
                try:
                    return_datetime_string = datetime_value.strftime("%I:%M %p")  # Datetime is converted to string for view
                    return return_datetime_string

                except Exception as e:
                    print(f"datetime value:{datetime_value}")
                    logging.error(f"Exception type:{type(e)}  (Error Description:{e}")
                    return None

            else:
                return None

        if column_key in Columns.Duration.value:  # convert duration integer to string and add "minutes"
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

        if column_key == Columns.Name.value:
            return self.handle_task_name_input(index, row, value, role)

        if column_key == Columns.Duration.value:
            return self.handle_duration_input(index, row, value, role)

        if column_key in [Columns.StartTime.value, Columns.EndTime.value, Columns.Reminder.value]:
            return self.handle_time_inputs(value, row, column_key)

        col_keys_only_dev = [Columns.ID.value, Columns.Type.value, Columns.Position.value]
        if column_key in col_keys_only_dev:
            logging.debug(f"Not supposed to change these columns' data by UI interaction.")
            return False

    def handle_task_name_input(self, index, row, value, role):
        self._data[row]['task_name'] = value
        self.dataChanged.emit(index, index, [role])
        return True

    def handle_duration_input(self, index, row, value, role):
        try:
            new_duration = int(value)
            self._data[row][Columns.Duration.value] = new_duration
            self.dataChanged.emit(index, index, [role])
            return True
        except ValueError:
            logging.error(f" VALUE ERROR with new input value {value} in r:c={row}:{index.column()}")
            return False

    def handle_time_inputs(self, value, row, column_key):
        try:
            # Save as datetime object in format: 12:00 AM, 2023-01-01
            new_time = datetime.strptime(f'{value}, 2023-01-01', '%I:%M %p, %Y-%m-%d')
            self._data[row][column_key] = new_time
            return True
        except ValueError:
            logging.error(f" VALUE ERROR with new input value {value} in r:c={row}:{column_key}")
            return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Return the visible header label for the given section (column index)
                if 0 <= section < len(self.visible_headers):  # Section is like column index. 0 section means 'Start'
                    return self.visible_headers[section]
            elif orientation == Qt.Orientation.Vertical:
                # Return the row number for the given section (row index)
                return section + 1
        return None

    def flags(self, index):
        if index.row() == 0 and index.column() == 0:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        total_rows = len(self._data)

        if index.row() == total_rows - 1 and index.column() == 1:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() or row >= len(self._data) or column >= len(self.column_keys):
            return QModelIndex()
        return self.createIndex(row, column, self._data[row])

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data) if not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()):
        return len(self.column_keys) if not parent.isValid() else 0
