import logging

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QTableView, QHeaderView)

from resources.default import Columns
from src.resources.styles import table_qss
from src.views.delegates.table_delegate import TableDelegate


class TableView(QTableView):
    close_requested_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug(f"TableView class constructor starting. Nothing in TableView constructor.")

        self.clicked_index = None
        self.clicked.connect(self.on_cell_clicked)

    def on_cell_clicked(self, index):
        self.clicked_index = index
        self.update()

    def setModel(self, model):
        super().setModel(model)

        self.table_delegate = TableDelegate(self)
        self.setItemDelegate(self.table_delegate)

        self.connect_model_signals()
        self.quick_tasks_set_span()

        self.set_properties()
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
        model.rowsInserted.connect(self.quick_tasks_set_span)
        model.rowsRemoved.connect(lambda: self.table_delegate.update_row_type_dict(model))
        model.modelReset.connect(lambda: self.table_delegate.update_row_type_dict(model))

    def set_properties(self):
        # Hide columns 0, 6, 7
        self.setColumnHidden(0, True)
        self.setColumnHidden(6, True)
        self.setColumnHidden(7, True)



        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)

        self.setMouseTracking(True)
        self.setShowGrid(False)
        self.setFrameStyle(0)  # No frame

        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setFrameStyle(0)  # No frame

        self.verticalHeader().setVisible(True)
        self.verticalHeader().setFrameStyle(0)  # No frame
        self.verticalHeader().setSectionsClickable(True)



        self.verticalHeader().setSectionsMovable(True)

        self.verticalHeader().setSortIndicatorShown(False)
        self.verticalHeader().setStretchLastSection(False)

        self.setSortingEnabled(False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setTabKeyNavigation(True)
        self.setWordWrap(True)
        self.setCornerButtonEnabled(True)
        self.setDragEnabled(True)
        self.setDragDropOverwriteMode(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDropIndicatorShown(True)

        # I see no effects of these properties
        self.viewport().setAutoFillBackground(True)

    def quick_tasks_set_span(self):
        for row in range(self.model().rowCount()):
            task_type = self.model().get_item_from_model(row, Columns.Type.value)

            if task_type == 'QuickTask':
                end_col_index = list(Columns).index(Columns.EndTime)

                # Last argument is number of columns to span (not the index to span till)
                self.setSpan(row, end_col_index, 1, 3)

    def set_height(self):
        self.verticalHeader().setDefaultSectionSize(45)
        # Set the height of the rows
        for row in range(self.model().rowCount()):
            task_type = self.model().get_item_from_model(row, Columns.Type.value)
            if task_type == 'QuickTask':
                self.setRowHeight(row, 30)
            else:
                self.setRowHeight(row, 45)

    def apply_styles(self):
        self.setStyleSheet(table_qss.TABLE_STYLE)
        self.horizontalHeader().setStyleSheet(table_qss.HORIZONTAL_HEADER_STYLE)
        self.verticalHeader().setStyleSheet(table_qss.VERTICAL_HEADER_STYLE)

    def adjust_col_widths(self):
        task_type = self.model().data(self.model().index(0, 6), Qt.ItemDataRole.DisplayRole)

        if task_type == 'QuickTask':
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
        background = "#B3BFDC"
        painter.fillRect(self.viewport().rect(), QColor(background))
        super().paintEvent(event)
