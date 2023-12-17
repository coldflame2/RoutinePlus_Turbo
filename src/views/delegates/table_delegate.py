import logging

from PyQt6.QtCore import QModelIndex, QRect, Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QFont, QPalette, QPainter, QPen
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QStyle

from src.utils import helper_fn


class TableDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.row_type_dict = {}
        logging.debug(f"TableDelegate class constructor starting. Nothing in TableDelegate constructor.")

    def update_row_type_dict(self, model):
        logging.debug(f"Updating row_type_dict in Delegate.")
        for row in range(model.rowCount()):
            try:
                row_type = model.data(model.index(row, 6), Qt.ItemDataRole.DisplayRole)
                self.row_type_dict[row] = row_type
            except Exception as e:
                logging.error(f"Error updating row type: {e}")

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        model = index.model()
        text_in_cell = model.data(index, Qt.ItemDataRole.DisplayRole)
        task_type = self.row_type_dict.get(index.row())

        self.set_font_and_pen(painter)  # Set font and pen

        self.paint_rows_bg(painter, option, index, model.rowCount(), text_in_cell)  # Fill rect

        if task_type == 'subtask':
            self.paint_subtask(painter, option, index, text_in_cell)  # Fill subtask rect

        self.paint_state(painter, option, text_in_cell)  # Draw line and fill color

    def set_font_and_pen(self, painter):
        font = QFont("Roboto", 11)  # Example: Arial font with size 10
        font.setWeight(QFont.Weight.Thin)  # Setting font weight
        painter.setFont(font)

        pen = QPen(QColor('black'), 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Smooth end caps for lines
        painter.setPen(pen)

        brush = QBrush(QColor('black'))
        painter.setBrush(brush)

    def paint_rows_bg(self, painter, option, index, total_rows, text):

        if index.row() == 0:
            color = "#DCEAEA"
            fill_rect = helper_fn.add_padding(option.rect, 2, 1, 0, 5)
        elif index.row() == total_rows - 1:
            color = "#DCEAEA"
            fill_rect = helper_fn.add_padding(option.rect, 1, 5, 0, 0)
        else:
            color = "#F0FFFF"
            fill_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 0)

        self.fill_rect_with_color(painter, option, fill_rect, color)

    def paint_subtask(self, painter, option, index, text):
        padded_rect = helper_fn.add_padding(option.rect, 2, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#CCE0FA")

        next_row = index.row() + 1
        task_type_next_row = self.row_type_dict.get(next_row)

        if task_type_next_row == 'main':
            self.draw_line(painter, padded_rect, "#36436A", 3)

    def paint_state(self, painter, option, text):
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        if is_selected and is_hovered:
            self.paint_hover_on_selected(painter, option)
        elif is_selected:
            self.paint_selected_state(painter, option, text)
        elif is_hovered:
            self.paint_hover_state(painter, option)

        text_rect = helper_fn.add_padding(option.rect, 25, 1, 1, 1)
        self.paint_text(painter, text_rect, text)

    def paint_hover_on_selected(self, painter, option):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#C1DEF6")

        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.draw_line(painter, padded_rect, "#36436A", 1)
        painter.setPen(QColor('black'))

    def paint_selected_state(self, painter, option, text):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#C8E6FF")
        self.draw_v_line(painter, padded_rect, "#36436A", 1)
        painter.setPen(QColor('black'))

    def paint_hover_state(self, painter, option):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#36436A")
        painter.setPen(QColor('white'))

    def fill_rect_with_color(self, painter, option, rect_fill, color):
        painter.fillRect(rect_fill, QColor(color))

    def draw_line(self, painter, rect_line, color, width):
        painter.drawLine(rect_line.bottomLeft(), rect_line.bottomRight())

    def draw_v_line(self, painter, rect_line, color, width):
        painter.drawLine(rect_line.topRight(), rect_line.bottomRight())

    def paint_text(self, painter, rect, text):
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))

