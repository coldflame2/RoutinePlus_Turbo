import logging

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, \
    QSpacerItem, \
    QTabWidget, \
    QVBoxLayout, QWidget


class RibbonWidget(QWidget):
    change_in_auto_height_checkbox = pyqtSignal(bool)
    change_in_auto_font_checkbox = pyqtSignal(bool)
    change_in_font_combobox = pyqtSignal(int)

    reset_col_widths_signal = pyqtSignal(bool)
    view_shortcuts_dialog_signal = pyqtSignal()

    def __init__(self, parent=None):  # Accept app_settings as an argument
        super().__init__(parent)

        self.update()
