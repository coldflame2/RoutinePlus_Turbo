import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from src.models.app_data import AppData
from src.resources.default import COLUMN_KEYS, VISIBLE_HEADERS


class TableModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        logging.debug(f"TableModel Class starting.")

        self.visible_headers = VISIBLE_HEADERS  # Visible headers for UI
        self.column_keys = COLUMN_KEYS  # Keys (str) used internally

        self.app_data = AppData()
        try:
            self._data = self.app_data.get_all_entries()
        except Exception as e:
            logging.error(f"Exception in TableModel init: {e}")
            self.app_data.close()  # Close the database connection on failure
            raise  # Re-raise the exception to signal the failure

        logging.debug(f"TableModel Class constructor successfully initialized.")

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
        This method is called by the view to retrieve the data for a given index. The role parameter specifies what kind of data is being requested (e.g., display data, tooltip data).

        """
        if not index.isValid() or role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        row_data = self._data[index.row()]  # type=dictionary(column_key:value). Entire row data of index, including id
        column_key = self.column_keys[index.column()]  # name of the column defined in visible_headers

        return row_data.get(column_key, None)  # The value of the cell

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Called when the user edits a value in a view."""
        logging.debug(f"'setData' method called with value:{value}.")

        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False

        row = index.row()
        column_key = self.column_keys[index.column()]

        # Update the specific field in the row data
        try:
            self._data[row][column_key] = value
            self.dataChanged.emit(index, index, [role])
            logging.debug(f"'setData': value '{value}' set at row:{row} and column_key:'{column_key}'.")
            logging.debug(f"'setData': dataChanged signal emitted.")

            return True
        except Exception as e:
            logging.error(f"Exception type: {type(e)} in setData (Error Description: {e})")
            return False

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

