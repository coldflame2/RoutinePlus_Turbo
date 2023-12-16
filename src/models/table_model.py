import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

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
            self._data: List[Dict[str, Any]] = list(self.app_data.get_all_entries())

        except Exception as e:
            logging.error(f"Exception in TableModel init: {e}")
            self.app_data.close()  # Close the database connection on failure
            raise  # Re-raise the exception to signal the failure

    def get_row_data(self, row, column_key=None):
        if column_key is None:
            logging.debug(f"Returning entire row data for row:'{row}'")
            return self._data[row]
        else:
            logging.debug(f"Returning {column_key}'s value: ('{self._data[row][column_key]}') at row index:{row}")
            return self._data[row][column_key]

    def insert_new_row(self, index, data_to_insert):
        self.beginInsertRows(QModelIndex(), index, index)

        try:
            self._data.insert(index, data_to_insert)  # Inset in model's database
            self._data[index]['id'] = self.app_data.insert_new_row(data_to_insert)  # Insert in SQLite file and set ID

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when inserting new row (Error Description:{e}")

        self.endInsertRows()

    def set_row_data(self, row,
                     new_from=None, new_to=None,
                     new_duration=None, new_type=None,
                     new_task_sequence=None):

        logging.debug(f"Updating value/s of row: '{row}'.")

        if 0 <= row < self.rowCount():
            changed_indices = []

            if new_from is not None:
                logging.debug("Updating 'from_time'")
                self._data[row]['from_time'] = new_from
                from_col_index = self.createIndex(row, 0)  # Assuming 'from_time' is in column 0
                changed_indices.append(from_col_index)

            if new_to is not None:
                logging.debug("Updating 'to_time'")
                self._data[row]['to_time'] = new_to
                to_col_index = self.createIndex(row, 1)
                changed_indices.append(to_col_index)

            if new_duration is not None:
                logging.debug("Updating 'duration'")
                self._data[row]['duration'] = new_duration
                dur_col_index = self.createIndex(row, 1)  # Assuming 'duration' is in column 1
                changed_indices.append(dur_col_index)

            if new_type is not None:
                logging.debug("Updating 'type'")
                self._data[row]['type'] = new_type
                type_col_index = self.createIndex(row, 2)
                changed_indices.append(type_col_index)

            if new_task_sequence is not None:
                logging.debug("Updating 'task_sequence'")
                self._data[row]['task_sequence'] = new_task_sequence
                seq_col_index = self.createIndex(row, 2)  # Assuming 'task_sequence' is in column 2
                changed_indices.append(seq_col_index)

            # Notify views of data changes
            for index in changed_indices:
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])

            logging.debug("Values updated and dataChanged emitted.")

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
        logging.debug(f"Looping rows in model and calling update or insert in AppData.")
        print(self.rowCount())

        for row in range(self.rowCount()):
            row_data = self.get_row_data(row)
            self.app_data.update_sqlite_data(row_data)

        self.app_data.commit_sqlite_all()
        logging.debug(f"Saving to database file. {self._data}")

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

        if column_key in ["from_time", "to_time", "reminders"]:  # convert datetime to string for view
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

        if column_key in ["duration"]:  # convert duration integer to string and add "minutes"
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

        if column_key in ["id", "type", "task_sequence"]:
            value = row_data.get(column_key, None)

            value_str = str(value)
            return value_str

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
        if index.row() == 0 and index.column() == 0:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        total_rows = len(self._data)

        if index.row() == total_rows - 1 and index.column() == 1:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

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
