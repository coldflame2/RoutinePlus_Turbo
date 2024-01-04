import logging
import os

from PyQt6.QtCore import QPoint, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from src.resources.styles import all_styles
from src.utils import helper_fn


class TitleBar(QWidget):
    minimize_tray_title_bar_clicked_signal = pyqtSignal()
    minimize_title_bar_clicked_signal = pyqtSignal()
    maximize_title_bar_clicked_signal = pyqtSignal()
    close_title_bar_clicked_signal = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.dragPos = self.mapToGlobal(QPoint(0, 0))  # Initialize to (0,0) or any desired value
        self.main_window = main_window

        self.setup_title_bar_layout()

        # For Text/Label on the left
        self.setup_text_label_for_title_bar()

        # For Buttons on the right
        self.setup_min_max_close_buttons()

        self.main_window.window_state_changed.connect(self.update_maximize_restore_icon)
        self.setup_title_bar_icon()
        # Add all the widgets to the 'self' QWidget
        self.add_widgets()
        self.apply_styles()

    def setup_title_bar_layout(self):
        self.main_layout = QHBoxLayout()
        self.setFixedHeight(38)
        self.main_layout.setContentsMargins(2, 0, 0, 1)  # left, top, right, bottom
        self.main_layout.setSpacing(0)

        self.container_widget = QWidget()
        self.container_widget.setObjectName("containerWidget")
        self.container_layout = QHBoxLayout()
        self.container_layout.setContentsMargins(10, 4, 3, 1)  # left, top, right, bottom
        self.container_layout.setSpacing(0)

    def setup_text_label_for_title_bar(self):
        env_config_class = helper_fn.get_environment_cls(False, caller='TitleBar.py')
        win_title = env_config_class.WIN_TITLE
        self.title = QLabel(win_title)
        self.title.setObjectName("labelCustomTitle")

    def setup_min_max_close_buttons(self):
        self.setup_minimize_to_tray_button()
        self.setup_minimize_to_taskbar_button()
        self.setup_toggle_window_maximize_button()
        self.setup_close_button()

    def setup_minimize_to_tray_button(self):
        self.minimize_tray = QPushButton('')
        self.minimize_tray.setObjectName("minTrayTitleButton")
        minimize_tray_icon_path = helper_fn.resource_path(os.path.join('resources/icons/title_bar_icons',
                                                                       'minimizetotray_icon.png'))
        self.minimize_tray.setIcon(QIcon(minimize_tray_icon_path))
        self.minimize_tray.setToolTip("Minimize To Tray")
        self.minimize_tray.clicked.connect(self.minimize_tray_title_bar_clicked_signal.emit)

    def setup_minimize_to_taskbar_button(self):
        self.minimize_button = QPushButton('')
        minimize_icon_path = helper_fn.resource_path(os.path.join('resources/icons/title_bar_icons', 'minimize_icon.png'))
        self.minimize_button.setIcon(QIcon(minimize_icon_path))
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.clicked.connect(self.minimize_title_bar_clicked_signal.emit)

    def setup_toggle_window_maximize_button(self):
        self.maximize_button = QPushButton('')
        max_icon_path = helper_fn.resource_path(os.path.join('resources/icons/title_bar_icons', 'max_icon.png'))
        self.maximize_button.setIcon(QIcon(max_icon_path))
        self.maximize_button.clicked.connect(self.maximize_title_bar_clicked_signal.emit)

    def setup_close_button(self):
        self.close_button = QPushButton('')
        self.close_button.setObjectName("closeTitleButton")
        self.close_button.setToolTip("Close")
        close_icon_path = helper_fn.resource_path(os.path.join('resources/icons/title_bar_icons', 'close_icon.png'))
        self.close_button.setIcon(QIcon(close_icon_path))
        self.close_button.clicked.connect(lambda: self.close_title_bar_clicked_signal.emit("Title bar"))

        logging.debug(f" custom_title constructor initialized.")

    def setup_title_bar_icon(self):
        env_class = helper_fn.get_environment_cls(False, caller='sidebar.py')
        icon_name = env_class.ICON_NAME
        icon_folders_relative = 'resources/icons/others/'
        icon_path = helper_fn.resource_path(os.path.join(icon_folders_relative, icon_name))

        # Create a new QLabel for the icon
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        scaled_pixmap = pixmap.scaled(
            20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        self.icon_label.setPixmap(scaled_pixmap)

    def add_widgets(self):
        # Add the widgets to the container_layout
        self.container_layout.addWidget(self.icon_label)

        self.container_layout.addWidget(self.title)
        self.container_layout.addStretch(1)  # To expand or contract as the window is resized.
        self.container_layout.addWidget(self.minimize_tray)
        self.container_layout.addWidget(self.minimize_button)
        self.container_layout.addWidget(self.maximize_button)
        self.container_layout.addWidget(self.close_button)

        # set the container_layout to the container_widget
        self.container_widget.setLayout(self.container_layout)

        # Finally, add the container_widget to the main_layout of the title bar
        self.main_layout.addWidget(self.container_widget)
        self.setLayout(self.main_layout)

    def apply_styles(self):
        self.container_widget.setStyleSheet(all_styles.TITLE_BAR)

    def update_maximize_restore_icon(self):
        if self.main_window.isMaximized():
            restore_icon_path = helper_fn.resource_path(os.path.join('resources/icons/title_bar_icons', 'restore_icon.png'))
            self.maximize_button.setIcon(QIcon(restore_icon_path))
            self.maximize_button.setToolTip("Restore Down")
        else:
            max_icon_path = helper_fn.resource_path(os.path.join('resources/icons/title_bar_icons', 'max_icon.png'))
            self.maximize_button.setIcon(QIcon(max_icon_path))
            self.maximize_button.setToolTip("Maximize")

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.main_window.move(self.main_window.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()

    def maximize_restore(self):
        if self.main_window.isMaximized():
            self.main_window.showNormal()
            logging.debug("Custom Normal (maximize) button clicked: Window resized to normal.")
        else:
            self.main_window.showMaximized()
            logging.debug("Custom Maximize button clicked: Window maximized.")
        self.update_maximize_restore_icon()

    def delayed_minimize(self):
        logging.debug("Custom Minimize to Tray Button clicked.")
        self.main_window.hide()
        QTimer.singleShot(100, self.main_window.showMinimized)
