import logging

from PyQt6.QtCore import QModelIndex, Qt, QRect, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QImage
from PyQt6.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QStyle, QLineEdit

from resources.default import Columns
from src.utils import helper_fn


class TableDelegate(QStyledItemDelegate):
    def __init__(self, view, parent=None):
        super().__init__(parent)

        self.view = view
        self.row_type_dict = {}  # {row index:type}
        self.selected_row_on_btn_hover = {}  # {selected_row: True/False}
        self.selected_row = None
        self.hovered_row = None
        self.clicked_index = None

        self.opacity = 0.0

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.increment_opacity)
        self.animation_timer.start(100)  # Adjust the interval for smoother or faster animation

        logging.debug(f"TableDelegate class constructor starting. Nothing in TableDelegate constructor.")

    def update_selected_row_on_btn_hover(self, selected_row, is_btn_hovered):
        # This method is called every time mouse enters or leaves the "new task" button on Sidebar
        #

        # Reset if no row is selected or when hover state is false
        if selected_row is None or not is_btn_hovered:  # No selected row and btn isn't hovered
            print(f"Can't say either row is selected or btn is hovered or both.")
            self.selected_row = None
            self.opacity = 0.0
            if not is_btn_hovered:  # Not hovered
                print(f"Btn is definitely not hovered. A row might or might not be selected.")
                self.animation_timer.start(50)  # Adjust for animation speed
            return

        print(f"BOTH: A row is selected and button is hovered.")

        # Update settings for the hovered row
        self.opacity = 1.0
        self.selected_row = selected_row
        self.selected_row_on_btn_hover[selected_row] = is_btn_hovered

        # Update the current and next row if valid
        for row in [selected_row, selected_row + 1]:
            index = self.view.model().index(row, 0)
            if index.isValid():
                self.view.update(index)

    def update_hovered_row(self, hovered_row):
        self.hovered_row = hovered_row

    def update_row_type_dict(self, model):
        for row in range(model.rowCount()):
            try:
                row_type = model.get_item_from_model(row, Columns.Type.value)
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

        if self.selected_row is not None and index.column() in [1]:
            self.draw_arrow(painter, option, index)

        if self.hovered_row is not None and index.column() in [0, 1]:
            self.draw_plus_sign(painter, option, index, self.hovered_row)

    def draw_arrow(self, painter, option, index):
        if index.row() == self.selected_row:
            self.draw_h_line_bottom(painter, option.rect, "#8791AB", 10)

        if index.row() == self.selected_row + 1:
            if self.selected_row_on_btn_hover.get(self.selected_row, False):
                # Get the image path
                image_path = helper_fn.resource_path("resources/images/arrow.png")

                # Load the image
                image = QImage(image_path)
                if not image.isNull():
                    transparent_image = self.set_transparency(image, self.opacity)  # 50% transparency

                    image_width = 20
                    image_height = 20
                    try:
                        x_position = int(option.rect.x() + (option.rect.width() - image_width) / 2)
                        y_position = int(option.rect.y() + (option.rect.height() - 40 - image_height) / 2)

                        image_rect = QRect(x_position, y_position, image_width, image_height)

                    except Exception as e:
                        logging.error(f"Exception type: {type(e)}. Error:{e}")

                    # Draw the image
                    painter.drawImage(image_rect, transparent_image)

    def set_transparency(self, image, alpha):
        """
        Adjust the transparency of an image.
        :param image: QImage object
        :param alpha: float (0.0 - 1.0), where 0.0 is fully transparent and 1.0 is fully opaque
        :return: QImage with adjusted transparency
        """
        transparent_image = QImage(image.size(), QImage.Format.Format_ARGB32)
        transparent_image.fill(0)

        painter = QPainter(transparent_image)
        painter.setOpacity(alpha)
        painter.drawImage(0, 0, image)
        painter.end()

        return transparent_image

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
            fill_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 2)

        elif index.row() == total_rows - 1:  # Last row
            color = "#DCEAEA"
            fill_rect = helper_fn.add_padding(option.rect, 1, 2, 0, 1)

        elif index.row() < total_rows - 1:  # Rows in between
            if self.row_type_dict.get(index.row()) == 'QuickTask':  # QuickTask rows
                color = "#EAF9F9"
                fill_rect = helper_fn.add_padding(option.rect, 1, 1, 0, 0)
            elif self.row_type_dict.get(index.row()) == 'main':  # Main task rows
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
        is_focused = option.state & QStyle.StateFlag.State_HasFocus

        if is_focused:
            painter.setPen(QColor('black'))
            self.paint_focused_state(painter, option, index)

        if is_selected:
            self.paint_selected_state(painter, option, index)

        if is_selected and is_focused:
            self.paint_focused_state(painter, option, index)

        if is_hovered:
            self.paint_hover_state(painter, option)

        text_rect = helper_fn.add_padding(option.rect, 25, 1, 1, 1)
        self.paint_text(painter, text_rect, text)

    def paint_recently_updated_row(self, painter, option, index):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.draw_h_line_bottom(painter, padded_rect, "#FF00CE", 5)
        self.draw_v_line(painter, padded_rect, "#FF00CE", 5)
        painter.setPen(QColor('black'))

    def paint_focused_state(self, painter, option, index):
        padded_rect = helper_fn.add_padding(option.rect, 0, 0, 0, 0)
        self.draw_h_line_bottom(painter, padded_rect, "#27304E", 5)
        self.draw_v_line(painter, padded_rect, "#27304E", 5)
        self.fill_rect_with_color(painter, option, padded_rect, "#DAE6F7")
        # self.draw_v_line_left(painter, padded_rect, "#36436A", 1)
        painter.setPen(QColor('black'))

    def paint_hover_on_selected(self, painter, option):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#C1DEF6")

        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.draw_h_line_bottom(painter, padded_rect, "#36436A", 1)
        painter.setPen(QColor('black'))

    def paint_selected_state(self, painter, option, index):
        if self.view and self.view.clicked_index == index:  # Selected Cell
            print("this one")
            padded_rect = helper_fn.add_padding(option.rect, 0, 0, 0, 0)
            self.fill_rect_with_color(painter, option, padded_rect, "#DAE6F7")

            padded_rect = helper_fn.add_padding(option.rect, 0, 0, 0, 0)
            self.draw_h_line_bottom(painter, padded_rect, "#36436A", 2)

        elif self.view.clicked_index != index:  # Selected row
            print(f"Selected row")
            padded_rect = helper_fn.add_padding(option.rect, 0, 0, 0, 1)
            self.draw_v_line_left(painter, padded_rect, "#EAF9F9", 5)
            self.fill_rect_with_color(painter, option, padded_rect, "#403E59")

            padded_rect = helper_fn.add_padding(option.rect, 0, 0, 0, 0)
            self.draw_h_line_bottom(painter, padded_rect, "#36436A", 2)

            painter.setPen(QColor('white'))

    def paint_hover_state(self, painter, option):
        padded_rect = helper_fn.add_padding(option.rect, 0, 1, 0, 0)
        self.fill_rect_with_color(painter, option, padded_rect, "#36436A")

        painter.setPen(QColor('white'))

    def draw_plus_sign(self, painter, option, index, hovered_row):

        if index.row() == self.hovered_row + 1:
            plus_sign_size = 10  # Adjust size as needed

            # Calculate the center of the current row (which is the next row after the hovered row)
            center_x = int(option.rect.center().x())
            center_y = int(option.rect.center().y())

            # Set pen for drawing the plus sign
            painter.setPen(QPen(QColor('blue'), 2))  # Adjust color and thickness as needed

            # Draw vertical line of the plus sign
            painter.drawLine(center_x, center_y - plus_sign_size // 2, center_x, center_y + plus_sign_size // 2)

            # Draw horizontal line of the plus sign
            painter.drawLine(center_x - plus_sign_size // 2, center_y, center_x + plus_sign_size // 2, center_y)

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

    def draw_v_line_left(self, painter, rect_line, color, width):
        pen = QPen(QColor(color), width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)  # Smooth end caps for lines
        painter.setPen(pen)

        painter.drawLine(rect_line.topLeft(), rect_line.bottomLeft())

        self.view.viewport().update()

    def increment_opacity(self):
        if self.opacity < 1.0:
            self.opacity += 0.1  # Increment opacity; adjust for different speed
            self.view.viewport().update()  # Trigger a repaint
        else:
            self.opacity -= 0.1  # Stop the timer if full opacity is reached
            self.view.viewport().update()  # Trigger a repaint
