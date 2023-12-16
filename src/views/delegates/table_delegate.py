from PyQt6.QtCore import QModelIndex, QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPalette, QPainter, QPen
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QStyle

from src.utils import helper_fn


class TableDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        model = index.model()
        text_in_cell = model.data(index, Qt.ItemDataRole.DisplayRole)

        self.set_font_and_pen(painter, option, text_in_cell)  # font size and pen color
        self.paint_special_rows(painter, option, index, model.rowCount())

        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        # Handle selected state
        if is_selected:
            self.paint_selected_state(painter, option, text_in_cell)

        elif is_hovered:
            self.paint_hover_state(painter, option)

        # hovered on selected items
        if is_hovered and is_selected:
            self.paint_hover_on_selected(painter, option, text_in_cell)

        self.paint_text(painter, option, text_in_cell)

    def set_font_and_pen(self, painter, option, text):
        # Apply common font and pen settings here
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        
        painter.setPen(QColor('black'))

    def paint_special_rows(self, painter, option, index, total_rows):
        # first and last row
        first_and_last = "#959EB7"

        padded_rect = helper_fn.add_padding(option.rect, 10, 3, 0, 2)
        if index.row() == 0:
            painter.fillRect(padded_rect, QColor(first_and_last))  # Fill with color
        elif index.row() == total_rows - 1:
            painter.fillRect(padded_rect, QColor(first_and_last))  # Fill with color
        else:
            other_row_color = "#F0FFFF"
            painter.fillRect(padded_rect, QColor(other_row_color))

    def paint_hover_state(self, painter, option):
        if option.state & QStyle.StateFlag.State_MouseOver:

            item_hover_bg = "#36436A"
            padded_rect_fill = helper_fn.add_padding(option.rect, 10, 0, 0, 0)
            painter.fillRect(padded_rect_fill, QBrush(QColor(item_hover_bg)))

            accent_color_lighter = "#9AB0FF"
            painter.setPen(QPen(QColor(accent_color_lighter), 3))
            painter.drawLine(padded_rect_fill.bottomLeft(), padded_rect_fill.bottomRight())

            painter.setPen(QColor('white'))

    def paint_selected_state(self, painter, option, text):
        if option.state & QStyle.StateFlag.State_Selected:
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QColor('black'))

            item_selected_bg = "#C8E6FF"  # item background when selected

            padded_rect = helper_fn.add_padding(option.rect, 10, 0, 0, 0)
            painter.fillRect(padded_rect, QBrush(QColor(item_selected_bg)))

            padded_rect = helper_fn.add_padding(option.rect, 20, 15, 0, 15)
            painter.drawText(padded_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))

            app_accent_color = "#36436A"
            painter.setPen(QColor(app_accent_color))
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

    def paint_hover_on_selected(self, painter, option, text):
        hover_on_selected_bg = "#C1DEF6"
        padded_rect_fill = helper_fn.add_padding(option.rect, 10, 0, 0, 0)
        painter.fillRect(padded_rect_fill, QBrush(QColor(hover_on_selected_bg)))
        
        app_accent_color = "#36436A"
        painter.setPen(QPen(QColor(app_accent_color), 3))
        painter.drawLine(padded_rect_fill.bottomLeft(), padded_rect_fill.bottomRight())

        painter.setPen(QColor('black'))

    def paint_text(self, painter, option, text):
        # Paint the text
        padded_rect_text = helper_fn.add_padding(option.rect, 20, 15, 0, 15)
        painter.drawText(padded_rect_text, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))
