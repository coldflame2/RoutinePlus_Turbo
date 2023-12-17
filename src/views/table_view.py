import logging

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor
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

        self.table_delegate = TableDelegate()
        self.setItemDelegate(self.table_delegate)

        self.connect_model_signals()
        self.set_properties()
        self.set_triggers()
        self.set_height()
        self.apply_styles()
        self.adjust_col_widths()

    def connect_model_signals(self):
        model = self.model()
        self.table_delegate.update_row_type_dict(model)  # Call once to initialize the row type dict

        # Connect model signals to the cache updating method
        model.dataChanged.connect(lambda: self.table_delegate.update_row_type_dict(model))
        model.dataChanged.connect(self.set_height)

        model.rowsInserted.connect(lambda: self.table_delegate.update_row_type_dict(model))
        model.rowsInserted.connect(self.set_span_for_subtasks)
        model.rowsRemoved.connect(lambda: self.table_delegate.update_row_type_dict(model))
        model.modelReset.connect(lambda: self.table_delegate.update_row_type_dict(model))

    def set_properties(self):
        # Additional settings for transparent background can be here
        self.setShowGrid(False)  # Optionally hide the grid lines
        self.setMouseTracking(True)

        self.setFrameStyle(0)  # No frame
        self.viewport().setAutoFillBackground(True)

        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)

        self.set_span_for_subtasks()

    def set_span_for_subtasks(self):
        # Get Data from model for column 7
        for row in range(self.model().rowCount()):
            task_type = self.model().data(self.model().index(row, 6), Qt.ItemDataRole.DisplayRole)
            print(f"Task type:{task_type}")
            if task_type == 'subtask':
                print("Task type is subtask")
                for column in range(self.model().columnCount()):
                    # Span the cell at column 5 across multiple columns, e.g., 3 columns
                    self.setSpan(row, 1, 1, 7)

            else:
                print("Task type is not subtask")
                self.horizontalHeader().setVisible(True)
                self.verticalHeader().setVisible(True)

    def set_triggers(self):
        try:
            self.setEditTriggers(
                QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.AnyKeyPressed
            )
        except Exception as e:
            logging.error(f" Exception type:{type(e)} set_properties in TableView (Error Description:{e}")

    def set_height(self):
        self.verticalHeader().setDefaultSectionSize(45)

        # Set the height of the rows
        for row in range(self.model().rowCount()):
            if self.model().data(self.model().index(row, 6),
                                 Qt.ItemDataRole.DisplayRole) == 'subtask':
                self.setRowHeight(row, 30)
            else:
                self.setRowHeight(row, 45)

    def apply_styles(self):
        self.horizontalHeader().setStyleSheet(table_qss.HEADER_STYLE)

    def adjust_col_widths(self):
        # Resize first three columns to fit their content and add extra space
        row_id = 0
        from_time = 1
        to_time = 2
        duration = 3
        task_name = 4
        reminder = 5
        col_type = 6
        task_sequence = 7

        task_type = self.model().data(self.model().index(0, 6), Qt.ItemDataRole.DisplayRole)
        if task_type == 'subtask':
            return

        headers = self.horizontalHeader()

        headers.setMaximumSectionSize(300)
        headers.setMinimumSectionSize(30)

        for col_index in [1, 2]:  # From, To, Duration
            self.setColumnWidth(col_index, 100)
        self.setColumnWidth(3, 120)  # Duration
        for col_index in (0, 6, 7):  # ID, Type, Sequence
            self.setColumnWidth(col_index, 60)
        headers.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Task Name

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        background = item_border = "#B3BFDC"

        painter.fillRect(self.viewport().rect(), QColor(background))  # Choose your color
        super().paintEvent(event)
