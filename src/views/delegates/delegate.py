import logging

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QStyle, QLineEdit

from resources.default import Columns
from src.utils import helper_fn


class Delegate(QStyledItemDelegate):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view

        self.define_padding_and_color()

        self.row_type = {}  # {row:type}
        self.update_row_type()  # Update row types at initialization

        self.clicked_index = None
        self.selected_row = None

        self.connect_signals_from_view()

        logging.debug(f"Delegate Constructor initialized.")

    def define_padding_and_color(self):
        self.fill_padding = (0, 0, 3, 1)  # Left, Top, Right, Bottom
        self.text_padding = (8, 1, 1, 1)

        self.fill = "#FFFFFF"

        self.fill_hover = "#FAFAFF"
        self.border_hover = "#B0B0B5"  # Darker version of fill_hover

        self.fill_selected_row = "#EEEEF3"  # EEEEF3
        self.fill_selected_index = "#E4E4E9"

        self.fill_qt = "#EBFAFF"  # for quicktask

    def update_row_type(self):
        logging.debug(f"Model Row inserted signal caught in delegate. Updating row types.")
        model = self.view.model()

        for row in range(model.rowCount()):
            try:
                row_type = model.get_item_from_model(row, Columns.Type.value)
                self.row_type[row] = row_type
            except Exception as e:
                logging.error(f"Error updating row type: {e}")

    def update_clicked_index(self, index):
        self.clicked_index = index
        self.selected_row = index.row()
        self.view.viewport().update()

    def connect_signals_from_view(self):
        self.view.model().rowsInserted.connect(self.update_row_type)
        self.view.update_selection_index.connect(self.update_clicked_index)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()

        model = index.model()
        text_data = str(model.data(index, Qt.ItemDataRole.DisplayRole))

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        self.set_painter_basics(painter)  # font, pen, brush

        self.default_paint_1(painter, option)
        self.main_or_quicktask_2(painter, option, index)
        self.paint_state_3(painter, option, index, text_data)
        self.paint_text_4(painter, option, text_data)

    def set_painter_basics(self, painter):
        font = QFont("Roboto", 10)
        font.setWeight(QFont.Weight.Light)
        painter.setFont(font)

        pen = QPen(QColor('black'), 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Smooth end caps for lines
        painter.setPen(pen)

        brush = QBrush(QColor('black'))
        painter.setBrush(brush)

    def default_paint_1(self, painter, option):
        fill_rect = helper_fn.add_padding(option.rect, self.fill_padding)
        painter.fillRect(fill_rect, QColor(self.fill))

    def main_or_quicktask_2(self, painter, option, index):
        # Get type
        if self.row_type.get(index.row()) == 'MainTask':
            pass  # default_paint_1 will apply
        elif self.row_type.get(index.row()) == 'QuickTask':
            fill_rect = helper_fn.add_padding(option.rect, self.fill_padding)
            painter.fillRect(fill_rect, QColor(self.fill_qt))

    def paint_state_3(self, painter, option, index, text_data):
        is_focused = option.state & QStyle.StateFlag.State_HasFocus
        is_selected = option.state & QStyle.StateFlag.State_Selected

        # Clicked cell
        if self.clicked_index and index == self.clicked_index:
            fill_rect = helper_fn.add_padding(option.rect, (0, 0, 0, 0))
            painter.fillRect(fill_rect, QColor(self.fill_selected_index))

        # Selected row minus clicked cell
        if self.selected_row is not None and index.row() == self.selected_row and self.clicked_index != index:
            fill_rect = helper_fn.add_padding(option.rect, (0, 0, 0, 0))
            painter.fillRect(fill_rect, QColor(self.fill_selected_row))

        # row selected by arrow keys
        if is_selected and index.row() != self.selected_row:
            fill_rect = helper_fn.add_padding(option.rect, (0, 0, 0, 0))
            painter.fillRect(fill_rect, QColor(self.fill))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        if is_focused:
            fill_rect = helper_fn.add_padding(option.rect, (0, 0, 0, 0))

            painter.save()
            pen = QPen(QColor('white'), 1)
            painter.setPen(pen)
            text_rect = helper_fn.add_padding(option.rect, self.text_padding)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text_data)
            painter.fillRect(fill_rect, QColor("#2B3356"))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        if is_hovered:
            painter.save()
            pen = QPen(QColor(self.border_hover), 1)  # slight darker than dft_hover_fill
            painter.setPen(pen)
            fill_rect = helper_fn.add_padding(option.rect, self.fill_padding)
            painter.drawLine(fill_rect.bottomLeft(), fill_rect.bottomRight())
            painter.restore()

    def paint_text_4(self, painter, option, text_data):
        text_rect = helper_fn.add_padding(option.rect, self.text_padding)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text_data)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        font = editor.font()
        font.setPointSize(12)
        editor.setFont(font)
        return editor
