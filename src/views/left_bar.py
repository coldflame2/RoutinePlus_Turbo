import logging
import os
from datetime import datetime

from PyQt6.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget

from src.resources.styles import all_styles
from src.utils import helper_fn


class LeftBar(QObject):
    left_bar_signals = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_layout()

    def setup_layout(self):
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_widget.setMinimumWidth(130)

        # Layouts for top and bottom buttons
        self.layout_buttons_above = QVBoxLayout()
        self.layout_buttons_below = QVBoxLayout()

        self.left_layout.addLayout(self.layout_buttons_above)
        self.left_layout.addLayout(self.layout_buttons_below)

        self.left_layout.setContentsMargins(0, 1, 0, 0)  # Left, Top, Right, Bottom margins
        self.left_layout.setSpacing(10)  # between widgets in left layout (so, between last top button and first bottom button)

        self.layout_buttons_above.setContentsMargins(0, 0, 0, 0)
        self.layout_buttons_above.setSpacing(10)

        self.layout_buttons_below.setContentsMargins(0, 0, 0, 0)
        self.layout_buttons_below.setSpacing(10)

        self.setup_header()
        self.define_buttons_names()

        # Add spacer to absorb extra space and keep button layouts at top and bottom
        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.left_layout.addItem(spacer)

    def setup_header(self):
        # Create a new horizontal layout for the icon and date label
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(0)
        self.header_layout.setContentsMargins(3, 1, 1, 1)
        env_class = helper_fn.get_environment_cls(False, caller='left_bar.py')
        icon_name = env_class.ICON_NAME
        icon_folders_relative = 'resources/icons/others/'
        icon_path = helper_fn.resource_path(os.path.join(icon_folders_relative, icon_name))

        # Create a new QLabel for the icon
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        scaled_pixmap = pixmap.scaled(
            32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        self.icon_label.setPixmap(scaled_pixmap)

        # Add the horizontal layout to the main layout
        self.layout_buttons_above.addLayout(self.header_layout)

        self.header_layout.addWidget(self.icon_label)

    def setup_date_label(self):
        current_date = datetime.now().strftime("%d %B")  # May 3, 2023

        # Create a new QLabel for the date
        self.date_label = QLabel(current_date)
        self.date_label.setStyleSheet("color: white; font-size: 11pt")

        # Add spacer to absorb extra space and keep button layouts at top and bottom
        spacer = QSpacerItem(20, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.header_layout.addItem(spacer)

        self.header_layout.addWidget(self.date_label)

        # Add spacer to absorb extra space and keep button layouts at top and bottom
        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header_layout.addItem(spacer)

    def define_buttons_names(self):
        """
        Defines primary and secondary buttons and a
        """

        primary_buttons_names = [
            {"display_name": "Save", "action_name": "Save", "tool_tip": "Save current data"},
            {"display_name": "Save As", "action_name": "Save As", "tool_tip": "Save data to a new file"},
            {"display_name": "+ Task", "action_name": "New Task", "tool_tip": "Add a new task"},
            {"display_name": "+ Subtask", "action_name": "New Subtask", "tool_tip": "Add a new subtask"},
            {"display_name": "Preferences", "action_name": "Settings", "tool_tip": "Modify app preferences"},
            ]

        secondary_buttons_names = [
            {"display_name": "Delete", "action_name": "Delete", "tool_tip": "Delete Task"},
            {"display_name": "Tray", "action_name": "Minimize to Tray", "tool_tip": "minimize to system tray"},
            ]

        self.initialize_buttons(
            primary_buttons_names,
            self.layout_buttons_above,
            all_styles.LEFT_SIDE_BUTTONS_PRIMARY
            )

        self.initialize_buttons(
            secondary_buttons_names,
            self.layout_buttons_below,
            all_styles.LEFT_SIDE_BUTTONS_SECONDARY
            )

    def initialize_buttons(self, buttons_names, layout, style):
        """
        Initializes buttons with given names and styles and adds them to the specified layout.
        """
        for name in buttons_names:
            button = self.create_button(name, style)
            layout.addWidget(button)

    def create_button(self, name, style):
        """
        Creates a QPushButton with specified information and style.
        """
        button = QPushButton(" " + name["display_name"])
        button.setStyleSheet(style)
        self.set_button_icon(button, name["action_name"])
        button.setToolTip(name.get("tool_tip", name["display_name"]))

        button_action = name["action_name"]
        button.clicked.connect(lambda _, action=button_action: self.emit_signal(action))

        return button

    def emit_signal(self, action):
        logging.debug(f"Emitting '{action}' signal from LeftBar.")
        self.left_bar_signals.emit(action)

    def set_button_icon(self, button, action_name):
        """
        Sets an icon for the button if available.
        """
        icon_path = self.get_icon_path(action_name)
        if icon_path:
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(20, 20))
        else:
            logging.debug(f"Icon path not found for action: {action_name}")

    def get_icon_path(self, action_name):
        """
        Generates and returns the icon path for a given action.
        """
        icon_name = action_name.replace(" ", "").lower() + "_icon"
        icon_folders_relative = 'resources/icons/left_bar_icons'
        icon_path = helper_fn.resource_path(os.path.join(icon_folders_relative, icon_name))
        return helper_fn.resource_path(icon_path)

    def handle_actions_here(self, action):
        pass
