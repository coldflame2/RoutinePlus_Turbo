import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView, QTableView)

from src.resources.styles import table_qss
from src.views.delegates.spacing_delegate import SpacingDelegate


class TableView(QTableView):
    close_requested_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug(f"TableView class constructor starting. Nothing in TableView constructor.")
        spacing_delegate = SpacingDelegate()
        self.setItemDelegate(spacing_delegate)

    def setModel(self, model):
        super().setModel(model)
        self.set_properties()

    def set_properties(self):
        # Additional settings for transparent background can be here
        self.setShowGrid(False)  # Optionally hide the grid lines

        self.setFrameStyle(0)  # No frame
        self.viewport().setAutoFillBackground(True)

        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)  # if you want vertical headers as well

        self.set_triggers()
        self.set_height()
        self.apply_styles()

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
