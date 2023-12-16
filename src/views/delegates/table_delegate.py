from PyQt6.QtCore import QModelIndex, QRect, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPalette, QPainter, QPen
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QStyle

from src.utils import helper_fn

app_accent_color = item_hover_bg = "#36436A"
first_and_last = "#959EB7"
other_row_color = "#F0FFFF"

item_selected_bg = "#DCFFFF"  # item background when selected


class TableDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        model = index.model()
        total_rows = model.rowCount()
        text = model.data(index, Qt.ItemDataRole.DisplayRole)

        # first and last row
        if index.row() == 0:
            padded_rect = helper_fn.add_padding(option.rect, 10, 3, 0, 2)
            painter.fillRect(padded_rect, QColor(first_and_last))  # Fill with color
        elif index.row() == total_rows - 1:
            padded_rect = helper_fn.add_padding(option.rect, 10, 2, 0, 3)
            painter.fillRect(padded_rect, QColor(first_and_last))  # Fill with color
        else:
            padded_rect = helper_fn.add_padding(option.rect, 10, 1, 0, 1)
            painter.fillRect(padded_rect, QColor(other_row_color))

        # Set font for text
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)

        # Draw text
        painter.setPen(QColor('black'))
        padded_rect = helper_fn.add_padding(option.rect, 20, 15, 0, 15)
        painter.drawText(padded_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))

        painter.restore()  # Restore the painter's state

        # Remove the dotted border around the focused item
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state ^= QStyle.StateFlag.State_HasFocus
            return

        # Check for mouse hover state
        if option.state & QStyle.StateFlag.State_MouseOver:
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QColor('white'))

            padded_rect = helper_fn.add_padding(option.rect, 10, 0, 0, 0)
            painter.fillRect(padded_rect, QBrush(QColor(item_hover_bg)))

            padded_rect = helper_fn.add_padding(option.rect, 20, 15, 0, 15)
            painter.drawText(padded_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))

        # Check for selected state
        if option.state & QStyle.StateFlag.State_Selected:
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QColor('white'))

            padded_rect = helper_fn.add_padding(option.rect, 10, 0, 0, 0)
            painter.fillRect(padded_rect, QBrush(QColor(item_selected_bg)))

            padded_rect = helper_fn.add_padding(option.rect, 20, 15, 0, 15)
            painter.drawText(padded_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))

        painter.restore()
