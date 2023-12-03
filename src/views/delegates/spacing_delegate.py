import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStyle, QTableView, QStyledItemDelegate
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QRect


# Custom Delegate
class SpacingDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Add space around the cell content
        space = 0  # Adjust the space as needed
        option.rect.adjust(space, space, -space, -space)
        super().paint(painter, option, index)

        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state = option.state ^ QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)
