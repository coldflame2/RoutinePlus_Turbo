import logging

from PyQt6.QtCore import QAbstractItemModel, QModelIndex


class TaskerModel:
    def __init__(self, model: QAbstractItemModel):
        self.model = model

    def insert_new_task(self, row, data_to_insert):
        if row < 0 or row >= self.model.rowCount():
            logging.error(f"IndexError: Row index {row} is out of range")
            return False

        if data_to_insert is None:
            logging.warning(f"Null value not allowed for row {row}")
            return False

        try:
            self.model.beginInsertRows(QModelIndex(), row, row)
            self.model.set_row_data(row, data_to_insert)
            self.model.endInsertRows()
        except Exception as e:
            logging.error(f"Exception type: (type{e}). Error:{e}")

        self.update_row_id(row, data_to_insert)

    def update_row_id(self, row, data_to_insert):
        row_id = self.model.app_data.insert_new_row(data_to_insert)
        self.model.set_item(row, 'id', row_id)

    def delete_row_and_data(self, row):
        logging.debug(f"Deleting row: '{row}'")
        self.model.beginRemoveRows(QModelIndex(), row, row)

        try:
            row_id = self.model.get_item_from_model(row, 'id')
            self.model.delete_row_from_model(row)  # Delete from model
            self.model.app_data.delete_task(row_id)  # Delete from SQLite file using row ID

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when deleting row (Error Description:{e}")
            return False

        self.model.endRemoveRows()
        logging.debug(f"Row {row} deleted from model and SQLite database.")
        return True
