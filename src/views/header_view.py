from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QFont
from PyQt6.QtWidgets import QHeaderView

from utils import helper_fn


class HeaderView(QHeaderView):
    BACKGROUND_COLOR = QColor("#CCD4F0")
    TEXT_COLOR = QColor('#1e1f22')
    FONT = QFont("Calibri", 14)
    MIN_SECTION_SIZE = 80
    MIN_HEIGHT = 35
    TEXT_PADDING = (8, 0, 2, 0)
    FRAME_PADDING = (0, 0, 0, 0)  # Left, Top, Right, bottom
    FILL_PADDING = (0, 0, 3, 1)

    def __init__(self, model, orientation, parent=None):
        super().__init__(orientation, parent)
        self.model = model
        self.setMinimumSectionSize(self.MIN_SECTION_SIZE)
        self.setMinimumHeight(self.MIN_HEIGHT)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        self.paint_background(painter, rect)
        self.paint_text(painter, rect, logicalIndex)
        painter.restore()

    def paint_background(self, painter, rect):
        rect = self.add_padding(rect, self.FILL_PADDING)
        painter.fillRect(rect, self.BACKGROUND_COLOR)

    def paint_text(self, painter, rect, logicalIndex):
        header_text = self.model.headerData(logicalIndex, self.orientation())
        painter.setPen(QPen(self.TEXT_COLOR))
        painter.setFont(self.FONT)
        rect = self.add_padding(rect, self.TEXT_PADDING)
        alignment_flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        painter.drawText(rect, alignment_flags, header_text)

    @staticmethod
    def add_padding(rect, padding):
        return helper_fn.add_padding(rect, padding)


class VHeaderView(QHeaderView):
    BACKGROUND_COLOR = QColor("#CCD4F0")
    TEXT_COLOR = QColor('#1e1f22')
    FONT = QFont("Calibri", 8)
    MIN_SECTION_SIZE = 0
    TEXT_PADDING = (0, 0, 0, 0)
    FRAME_PADDING = (0, 0, 0, 0)  # Left, Top, Right, bottom
    fill_padding = (0, 0, 1, 1)  # Left, Top, Right, Bottom

    def __init__(self, model, orientation, parent=None):
        super().__init__(orientation, parent)
        self.model = model
        self.setMinimumSectionSize(self.MIN_SECTION_SIZE)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        self.paint_background(painter, rect)
        self.paint_text(painter, rect, logicalIndex)
        painter.restore()

    def paint_background(self, painter, rect):
        rect = self.add_padding(rect, self.fill_padding)
        painter.fillRect(rect, self.BACKGROUND_COLOR)

    def paint_text(self, painter, rect, logicalIndex):
        header_text = self.model.headerData(logicalIndex, self.orientation())
        painter.setPen(QPen(self.TEXT_COLOR))
        painter.setFont(self.FONT)
        rect = self.add_padding(rect, self.TEXT_PADDING)
        alignment_flags = Qt.AlignmentFlag.AlignCenter
        painter.drawText(rect, alignment_flags, header_text)

    @staticmethod
    def add_padding(rect, padding):
        return helper_fn.add_padding(rect, padding)
