import logging

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QTableView)

from resources.default import Columns
from resources.styles import table_qss
from views.delegates.delegate import Delegate
from views.header_view import HeaderView


class TableView(QTableView):
    close_requested_signal = pyqtSignal(str)
    update_selection_index = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        logging.debug(f"TableView class constructor starting.")

        """
        Most of the instance attributes that are generally initialized in the constructor have been 
        initialized in the setModel method. This is because the model is not available at the time of
        initialization of the TableView class.
        """
        super().__init__(*args, **kwargs)
        self.update()
        self.repaint()

    def setModel(self, model):
        super().setModel(model)
        self.set_styles()
        self.set_headers(model)
        self.set_delegate()
        self.connect_signals()
        self.set_span_for_quicktasks()
        self.set_view_properties()
        self.set_height()
        self.set_columns_widths()
        self.set_styles()

    def set_headers(self, model):
        self.header_view = HeaderView(model, Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self.header_view)
        # self.header_view = self.horizontalHeader()

        # self.v_header_view = VHeaderView(model, Qt.Orientation.Vertical, self)
        # self.setVerticalHeader(self.v_header_view)

    def set_delegate(self):
        self.table_delegate = Delegate(self)
        self.setItemDelegate(self.table_delegate)

    def connect_signals(self):
        # Rest of them are to connect signals from model
        model = self.model()
        model.dataChanged.connect(self.set_height)
        model.rowsInserted.connect(self.set_span_for_quicktasks)
        model.rowsInserted.connect(self.set_height)

    def set_view_properties(self):

        # Hide columns ID, Type, and Position
        for col_index in (0, 6, 7):
            self.setColumnHidden(col_index, True)

        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked |
                             QAbstractItemView.EditTrigger.AnyKeyPressed)

        self.setMouseTracking(True)
        self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def set_span_for_quicktasks(self):
        for row in range(self.model().rowCount()):
            task_type = self.model().get_item_from_model(row, Columns.Type.value)

            if task_type == 'QuickTask':
                end_col_index = list(Columns).index(Columns.EndTime)

                # Last argument is number of columns to span (not the index to span till)
                self.setSpan(row, end_col_index, 1, 3)

    def set_height(self):
        self.verticalHeader().setDefaultSectionSize(45)

        for row in range(self.model().rowCount()):
            task_type = self.model().get_item_from_model(row, Columns.Type.value)
            if task_type == 'QuickTask':
                self.setRowHeight(row, 28)
            else:
                self.setRowHeight(row, 45)

    def set_styles(self):
        pass
        # self.setStyleSheet(table_qss.CORNER_BTN_STYLE)

    def set_columns_widths(self):
        task_type = self.model().get_item_from_model(0, Columns.Type.value)
        if task_type == 'QuickTask':
            return

        self.header_view.setMaximumSectionSize(300)
        self.header_view.setMinimumSectionSize(30)

        for col_index in [1, 2]:  # From, To, Duration (0 is ID)
            self.setColumnWidth(col_index, 100)
        self.setColumnWidth(3, 120)  # Duration
        for col_index in (0, 6, 7):  # ID, Type, Sequence
            self.setColumnWidth(col_index, 60)
        self.header_view.setSectionResizeMode(4, self.header_view.ResizeMode.Stretch)  # Task Name

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        background_bg = "#EFEFE5"  # Original: EFEFE5
        painter.fillRect(self.viewport().rect(), QColor(background_bg))
        super().paintEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        # IMPORTANT! Call the base class implementation to handle default behavior
        super().mousePressEvent(event)

        # Get the index of the item that was clicked
        index = self.indexAt(event.pos())

        # Check if the click was on a valid index (row)
        if not index.isValid():
            # If the click was on an empty area, clear the selection
            # apparently, this makes index.row() to be -1
            self.clearFocus()
            self.update_selection_index.emit(index)
        else:
            super().mousePressEvent(event)
            self.update_selection_index.emit(index)

