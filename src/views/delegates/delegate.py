import logging

from PyQt6.QtCore import QModelIndex, Qt, QSize, QRect
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QFontDatabase
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

        # For Animation purposes: New row/task
        self.new_row_thickness_animated = 0
        self.fill_opacity_animated = 0
        self.animated_bottom_padding = 0

        # For Animation purposes: At main window launch
        self.txt_opacity = 0

        self.clicked_index = None
        self.selected_row = None

        self.connect_signals_from_view()

        logging.debug(f"Delegate Constructor initialized.")

    def define_padding_and_color(self):
        self.fill_padding = (0, 0, 3, 1)  # Left, Top, Right, Bottom
        self.text_padding = (8, 1, 1, 1)

        self.fill = "#FFFFFF"

        self.fill_hover = "#E3E5F5"
        self.border_hover = "#484D61"

        self.fill_selected_row = "#E1E1E6"
        self.fill_selected_index = "#E4E4E9"

        self.line_selected_row_keyboard = "#288ADD"

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
        font_family = "Calibri Light"
        font_db = QFontDatabase

        if font_family in font_db.families():
            self.font = QFont(font_family, 11)
        else:
            self.font = QFont('Arial', 10)

        self.font.setWeight(QFont.Weight.Normal)
        painter.setFont(self.font)

        pen_color = QColor(0, 0, 0, self.txt_opacity)
        pen = QPen(pen_color, 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Smooth end caps for lines
        painter.setPen(pen)

        brush = QBrush(QColor('black'))
        painter.setBrush(brush)

    def default_paint_1(self, painter, option):
        fill_rect = helper_fn.add_padding(option.rect, self.fill_padding)
        default_fill_color = QColor(self.fill)
        painter.fillRect(fill_rect, default_fill_color)

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

        # Drawing ellipse
        try:
            column_index = self.view.model().column_index(Columns.Reminder.value)
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            column_index = 0

        if index.row() == self.view.new_added_row:
            color = QColor(10, 10, 80, self.fill_opacity_animated)
            painter.fillRect(option.rect, color)

            white_to_black = self.fill_opacity_animated  # 255 to 0
            pen_color = QColor(white_to_black, white_to_black, white_to_black)
            pen = QPen(pen_color)
            painter.setPen(pen)

        # Paint green dot

        if index.row() in self.view.recent_rows_ids:
            self.font.setWeight(QFont.Weight.DemiBold)
            painter.setFont(self.font)

            if index.column() == column_index:
                pen = QPen(QColor("#36EF36"))
                brush = QBrush(QColor("#36EF36"))
                painter.setBrush(brush)
                painter.setPen(pen)
                ellipse_size = 5
                try:
                    ellipse_rect = QRect(int(option.rect.center().x() - ellipse_size / 2) + 30,
                                         int(option.rect.center().y() - ellipse_size / 2) + 1,
                                         ellipse_size, ellipse_size)
                    painter.drawEllipse(ellipse_rect)
                    pen = QPen(QColor("#000000"))
                    painter.setPen(pen)

                except Exception as e:
                    logging.error(f"Exception type: {type(e)}. Error:{e}")

        # Clicked cell
        if self.clicked_index and index == self.clicked_index:
            fill_rect = helper_fn.add_padding(option.rect, (0, 0, 0, 0))
            painter.fillRect(fill_rect, QColor(self.fill_selected_index))

        # Selected row minus clicked cell
        if self.selected_row is not None and index.row() == self.selected_row and self.clicked_index != index:
            painter.fillRect(option.rect, QColor('black'))  # To override system default

            fill_rect = helper_fn.add_padding(option.rect, self.fill_padding)
            painter.fillRect(fill_rect, QColor(self.fill_selected_row))

        # row selected by arrow keys
        if is_selected and index.row() != self.selected_row:
            painter.fillRect(option.rect, QColor('black'))  # To override system default

            pad_rect = helper_fn.add_padding(option.rect, self.fill_padding)
            painter.fillRect(pad_rect, QColor(self.fill))

            painter.save()
            pen = QPen(QColor(self.line_selected_row_keyboard), 5)
            painter.setPen(pen)
            painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
            painter.restore()

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
        font.setPointSize(10)
        editor.setFont(font)
        text_color = "#000000"
        background_color = self.fill_qt
        editor.setStyleSheet(f"background-color: {background_color};"
                             f"color: {text_color}")

        return editor

    def sizeHint(self, option, index):
        return QSize(1, 1)  # very small height and width
