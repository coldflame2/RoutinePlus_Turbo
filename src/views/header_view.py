from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QColor, QPen, QPainter, QFont
from PyQt6.QtCore import Qt

from utils import helper_fn


class HeaderView(QHeaderView):
    BACKGROUND_COLOR = QColor("#CCD4F0")
    TEXT_COLOR = QColor('#1e1f22')
    FRAME_COLOR = QColor('#EFEFE5')
    FONT = QFont("Calibri", 14)
    MIN_SECTION_SIZE = 80
    MIN_HEIGHT = 35
    TEXT_PADDING = (8, 1, 1, 1)
    FRAME_PADDING = (0, 0, 0, 0)  # Left, Top, Right, bottom

    def __init__(self, model, orientation, parent=None):
        super().__init__(orientation, parent)
        self.model = model
        self.setMinimumSectionSize(self.MIN_SECTION_SIZE)
        self.setMinimumHeight(self.MIN_HEIGHT)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        self.paint_frame(painter, rect)
        self.paint_background(painter, rect)
        self.paint_text(painter, rect, logicalIndex)
        painter.restore()

    def paint_background(self, painter, rect):
        rect = self.add_padding(rect, (0, 0, 3, 0))
        painter.fillRect(rect, self.BACKGROUND_COLOR)

    def paint_frame(self, painter, rect):
        pen = QPen(self.FRAME_COLOR)
        pen.setWidth(15)  # Set the width of the pen to 3 pixels
        painter.setPen(pen)

        rect = self.add_padding(rect, self.FRAME_PADDING)
        painter.drawLine(rect.bottomRight(), rect.topRight())

    def paint_text(self, painter, rect, logicalIndex):
        header_text = self.model.headerData(logicalIndex, self.orientation())
        painter.setPen(QPen(self.TEXT_COLOR))
        painter.setFont(self.FONT)
        rect = self.add_padding(rect, self.TEXT_PADDING)
        alignment_flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        painter.drawText(rect, alignment_flags, header_text)

    @staticmethod
    def add_padding(rect, padding):
        # helper_fn.add_padding can be implemented here
        return helper_fn.add_padding(rect, padding)
