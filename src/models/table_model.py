import logging
from typing import Any, Dict, List

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSignal

from models.auto_time_updater import AutoTimeUpdater
from models.tasker_model import TaskerModel
from src.models.app_data import AppData
from src.resources.default import VISIBLE_HEADERS, Columns


class TableModel(QAbstractItemModel):
    test_signal_from_model = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.visible_headers = VISIBLE_HEADERS  # Visible headers for UI
        self.column_keys = [column.value for column in Columns]

        self.tasker_model = TaskerModel(self)

        self.initiate_data()

    def initiate_data(self):
        self.app_data = AppData()

        try:
            self._data: List[Dict[str, Any]] = list(self.app_data.get_all_entries())

        except Exception as e:
            logging.error(f"Exception in TableModel init: {e}")
            self.app_data.close()  # Close the database connection on failure
            raise  # Re-raise the exception to signal the failure

    def get_item_from_model(self, row, column_key):
        try:
            value = self._data[row][column_key]
            return value
        except KeyError:
            logging.error(f"KeyError: Column key '{column_key}' not found in row {row}")
            return None
        except IndexError:
            logging.error(f"IndexError: Row index {row} is out of range")
            return None

    def set_item_in_model(self, row, column_key, value):
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
            return True
        except Exception as e:
            logging.error(f"Exception when updating row {row}, column '{column_key}': {e}")
            return False

    def set_row_data(self, row, data):
        """
        Updates the data for a specified row.

        Args:
            row (int): The row index.
            data (Dict[str, Any]): The new data to set.

        Returns:
            bool: True if the update was successful, False otherwise.
        """

        if row < 0 or row >= len(self._data):
            logging.error(f"IndexError: Row index {row} is out of range")
            return False

        if data is None:
            logging.warning(f"Null value not allowed for row {row}")
            return False

        try:
            self._data.insert(row, data)
            self.dataChanged.emit(QModelIndex(), QModelIndex(), [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
            self.layoutChanged.emit()

            return True

        except Exception as e:
            logging.error(f"Exception when updating row {row}: {e}")
            return False

    def delete_row_from_model(self, row):
        self._data.pop(row)
        self.dataChanged.emit(QModelIndex(), QModelIndex(), [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
        self.layoutChanged.emit()
        logging.debug(f"Row {row} deleted from model.")

    def save_to_database_file(self):
        logging.debug("Looping rows in model and calling update method in AppData.")

        for row in range(self.rowCount()):
            row_data = {}
            for column_key in self.column_keys:
                row_data[column_key] = self._data[row][column_key]

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

        try:
            # retrieve the formatted value from TaskerModel's method for view
            formatted_value = self.tasker_model.format_for_view(index.row(), column_key, row_data)
            return formatted_value

        except Exception as e:
            # Input is invalid, return None
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        self.test_signal_from_model.emit("setData called")

        if role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        column_key = self.column_keys[index.column()]

        # validate input and format it for model
        try:
            # get formatted value
            formatted_value = self.tasker_model.validate_and_format(value, row, column_key)
        except Exception as e:
            # Input is invalid, return False
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return False

        if formatted_value is False:
            # Input is invalid, return False
            logging.error(f"Formatted value is None.")
            return False

        # retrieve the other data to update from TableSyncManager's method
        try:
            auto_time_updater = AutoTimeUpdater(self)
            other_data_to_update = auto_time_updater.get_data_to_update(row, column_key, formatted_value)
            logging.debug(f"Other data to update: {other_data_to_update}")

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return False

        if other_data_to_update is False:
            logging.error(f"Error while preparing data for other cells to update.")
            return False

        logging.debug(f"Data prepared for edited cell and other cells.")

        # update the model
        try:
            # Set the formatted output to the model and emit dataChanged signal
            logging.debug(f"Updating value of edited cell.")
            self.set_item_in_model(row, column_key, formatted_value)

            # update other values in the model
            logging.debug(f"Updating values of other cells.")
            if other_data_to_update:
                for change_row, column, value in other_data_to_update:
                    self.set_item_in_model(change_row, column, value)
            else:
                logging.debug(f"No other values to update.")

            logging.debug(f"Values successfully updated.")
            return True

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if 0 <= section <= len(self.visible_headers):
                    return self.visible_headers[section-1]

            elif orientation == Qt.Orientation.Vertical:
                # Return the row number for the given section (row index)
                return section + 1
        return None

    def flags(self, index):
        if index.row() == 0 and index.column() == 1:  # column 0 is ID
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        if index.row() == len(self._data) - 1 and index.column() == 2:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return super().flags(index) | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

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
