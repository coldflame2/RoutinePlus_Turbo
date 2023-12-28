from PyQt6.QtWidgets import QHeaderView, QApplication, QTableView, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor


class CustomHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        # Call the base class to draw the default header
        super().paintSection(painter, rect, logicalIndex)

        # Customize the header drawing here
        # Example: Change background color if the section is selected
        if self.isSectionSelected(logicalIndex):
            painter.fillRect(rect, QColor(200, 200, 255))  # Light blue background for selected headers

        painter.restore()

    def isSectionSelected(self, logicalIndex):
        # Implement logic to determine if the section should be considered 'selected'
        # This might involve checking the selection of the table view
        return False  # Placeholder, implement your own logic here
