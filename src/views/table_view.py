import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView, QTableView, QHeaderView)

from src.resources.styles import table_qss
from src.views.delegates.table_delegate import TableDelegate


class TableView(QTableView):
    close_requested_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug(f"TableView class constructor starting. Nothing in TableView constructor.")

    def setModel(self, model):
        super().setModel(model)

        table_delegate = TableDelegate()
        self.setItemDelegate(table_delegate)

        self.set_properties()
        self.set_triggers()
        self.set_height()
        self.apply_styles()
        self.adjust_col_widths()

    def set_properties(self):
        # Additional settings for transparent background can be here
        self.setShowGrid(False)  # Optionally hide the grid lines

        self.setFrameStyle(0)  # No frame
        self.viewport().setAutoFillBackground(True)

        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)


    def set_triggers(self):
        try:
            self.setEditTriggers(
                QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.AnyKeyPressed
                )
        except Exception as e:
            logging.error(f" Exception type:{type(e)} set_properties in TableView (Error Description:{e}")

    def set_height(self):
        row_height = 45
        self.verticalHeader().setDefaultSectionSize(row_height)

    def apply_styles(self):
        self.setStyleSheet(table_qss.TABLE_STYLES)
    
    def adjust_col_widths(self):
        # Resize first three columns to fit their content and add extra space
        for column in range(3):
            self.resizeColumnToContents(column)
            current_width = self.columnWidth(column)
            self.setColumnWidth(column, current_width + 60)

        # Set the fourth column to stretch and fill the available space
        header = self.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Resize the last column to its content and add extra space
        reminder_col = 4
        self.resizeColumnToContents(reminder_col)
        current_width = self.columnWidth(reminder_col)
        self.setColumnWidth(reminder_col, current_width + 60)
        