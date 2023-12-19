import logging

from PyQt6.QtCore import QModelIndex, QRect, Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QFont, QPalette, QPainter, QPen
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QStyle, QLineEdit

from src.utils import helper_fn


class TableDelegate(QStyledItemDelegate):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.row_type_dict = {}  # {row index:type}
        logging.debug(f"TableDelegate class constructor starting. Nothing in TableDelegate constructor.")

    def update_row_type_dict(self, model):
        logging.debug(f"Updating row_type_dict in Delegate.")
        for row in range(model.rowCount()):
            try:
                row_type = model.data(model.index(row, 6), Qt.ItemDataRole.DisplayRole)
                self.row_type_dict[row] = row_type
            except Exception as e:
                logging.error(f"Error updating row type: {e}")

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        font = editor.font()
        font.setPointSize(12)
        editor.setFont(font)
        return editor

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()

        model = index.model()
        text_in_cell = model.data(index, Qt.ItemDataRole.DisplayRole)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        self.set_font_and_pen(painter)  # Set font and pen

        self.paint_rows_bg(painter, option, index, model.rowCount())

        self.paint_state(painter, option, index, text_in_cell)  # Draw line and fill color

        painter.restore()

    def set_font_and_pen(self, painter):
        font = QFont("Roboto", 11)
        font.setWeight(QFont.Weight.Light)
        painter.setFont(font)

        pen = QPen(QColor('black'), 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Smooth end caps for lines
        painter.setPen(pen)

        brush = QBrush(QColor('black'))
        painter.setBrush(brush)

    def paint_rows_bg(self, painter, option, index, total_rows):

        if index.row() == 0:  # First row
            color = "#DCEAEA"
            fill_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 5)

        elif index.row() == total_rows - 1:  # Last row
            color = "#DCEAEA"
            fill_rect = helper_fn.add_padding(option.rect, 1, 5, 0, 1)

        else:  # For other rows
            if self.row_type_dict.get(index.row()) == 'QuickTask':  # QuickTask rows
                color = '#CCE0FA'
                fill_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 0)
            else:  # Main task rows
                color = "#F0FFFF"
                fill_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 0)

        self.fill_rect_with_color(painter, option, fill_rect, color)

        type_previous = self.row_type_dict.get(index.row() - 1)
        if self.row_type_dict.get(index.row()) == 'QuickTask' and type_previous == 'main':
            self.draw_line_for_QuickTask(painter, option)

    def draw_line_for_QuickTask(self, painter, option):
        line_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 0)
        painter.save()
        pen = QPen(QColor("#A9BCD5"))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Smooth end caps for lines
        painter.setPen(pen)
        painter.drawLine(line_rect.topLeft(), line_rect.topRight())
        painter.restore()

    def paint_state(self, painter, option, index, text):
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        if is_selected and is_hovered:
            self.paint_hover_on_selected(painter, option)
        elif is_selected:
            self.paint_selected_state(painter, option, index)
        elif is_hovered:
            self.paint_hover_state(painter, option)

        text_rect = helper_fn.add_padding(option.rect, 25, 1, 1, 1)
        self.paint_text(painter, text_rect, text)

    def paint_hover_on_selected(self, painter, option):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#C1DEF6")

        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.draw_h_line_bottom(painter, padded_rect, "#36436A", 1)
        painter.setPen(QColor('black'))

    def paint_selected_state(self, painter, option, index):
        if self.view and self.view.clicked_index == index:  # Selected Cell
            padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
            self.fill_rect_with_color(painter, option, padded_rect, "#C8E6FF")
            painter.setPen(QColor('black'))

        else:  # Selected row
            padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
            self.fill_rect_with_color(painter, option, padded_rect, "#DCFFFF")
            self.draw_v_line(painter, padded_rect, "#36436A", 1)
            painter.setPen(QColor('black'))


    def paint_hover_state(self, painter, option):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#36436A")
        painter.setPen(QColor('white'))

    def fill_rect_with_color(self, painter, option, rect_fill, color):
        painter.fillRect(rect_fill, QColor(color))

    def draw_h_line_bottom(self, painter, rect_line, color, width):
        pen = QPen(QColor(color), width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawLine(rect_line.bottomLeft(), rect_line.bottomRight())

    def draw_h_line_top(self, painter, rect_line, color, width):
        pen = QPen(QColor(color), width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)

        painter.drawLine(rect_line.topLeft(), rect_line.topRight())

    def draw_v_line(self, painter, rect_line, color, width):
        pen = QPen(QColor(color), width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)  # Smooth end caps for lines
        painter.setPen(pen)

        painter.drawLine(rect_line.topRight(), rect_line.bottomRight())

    def paint_text(self, painter, rect, text):
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))
