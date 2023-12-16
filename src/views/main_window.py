# Python
import logging
import os

# PyQt
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QSplitter, QSplitterHandle, QVBoxLayout, QWidget

# This app's utilities and resources
from src.resources.styles import all_styles
from src.utils import helper_fn

# This app's Modules
from src.views.title_bar import TitleBar
from src.views.left_bar import LeftBar
from src.views.ribbon import RibbonWidget


class MainWindow(QMainWindow):
    close_requested_signal = pyqtSignal(str)
    main_frame_signal_after_left_bar = pyqtSignal(str)

    def __init__(self, table_view, controller):
        super().__init__()
        logging.debug(f"MainFrame class constructor starting.")

        self.closing_source = None  # This is instance variable so that it can be used in MainApp class (main.py)
        self.table_view = table_view
        self.controller = controller

        self.get_geometry_and_state()  # Settings, geometry, window state
        self._instantiate_components()  # ribbon, left bar, splitter, title bar
        self._container_layout()
        self._splitter_layout()
        self._configure_ui_elements()
        self._setup_win_properties()

        logging.debug(f"MainFrame constructor successfully initialized.")

    def get_geometry_and_state(self):
        self.env_config_class = helper_fn.get_environment_cls(False, caller='MainWin')
        self.settings_values = self.env_config_class.SETTINGS_VALUES

        self.geometry = self.settings_values.value("geometry")
        self.state = self.settings_values.value("windowState")

    def _instantiate_components(self):
        try:
            self.title_bar = TitleBar(self)
            self.ribbon = RibbonWidget()
            self.left_bar = LeftBar()
            self.splitter = HoverSplitter()
        except Exception as e:
            logging.error(f" Exception type:{type(e)}  (Error Description:{e}")

    def _container_layout(self):
        # Create the main container widget and set it as the central widget of the QMainWindow
        self.main_app_container_widget = QWidget()
        self.setCentralWidget(self.main_app_container_widget)

        # Create the main vertical layout
        self.main_frame_v_layout = QVBoxLayout()

        # Add the title bar widget to the main vertical layout
        self.main_frame_v_layout.addWidget(self.title_bar)

        # Set the main frame vertical layout to main app container widget
        self.main_app_container_widget.setLayout(self.main_frame_v_layout)

        self.main_frame_v_layout.setSpacing(0)  # vertical space between widgets
        self.main_frame_v_layout.setContentsMargins(0, 1, 5, 5)  # left, top, right, bottom

    def _splitter_layout(self):
        # Create splitter horizontal layout and add splitter as the only widget for now
        splitter_h_layout = QHBoxLayout()
        splitter_h_layout.addWidget(self.splitter)

        # Create container layout and widget for both ribbon and table and set the layout to the widget
        table_and_ribbon_v_layout = QVBoxLayout()
        self.table_and_ribbon_container = QWidget(self)
        self.table_and_ribbon_container.setLayout(table_and_ribbon_v_layout)

        # Add both ribbon and table widgets to 'table and ribbon vertical' layout
        table_and_ribbon_v_layout.addWidget(self.ribbon)
        table_and_ribbon_v_layout.addWidget(self.table_view)

        # Add left bar and table+ribbon container widget to splitter
        self.splitter.addWidget(self.left_bar.left_widget)
        self.splitter.addWidget(self.table_view)

        splitter_h_layout.setContentsMargins(0, 0, 0, 0)  # Set margins for the layout
        splitter_h_layout.setSpacing(0)  # Set spacing between widgets in the layout

        table_and_ribbon_v_layout.setContentsMargins(0, 0, 0, 0)
        table_and_ribbon_v_layout.setSpacing(0)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        # Add the horizontal layout to the main vertical layout
        self.main_frame_v_layout.addLayout(splitter_h_layout)

    def _configure_ui_elements(self):
        self._configure_title_bar()
        self.left_bar.left_bar_signals.connect(self.connect_to_controller)

    def connect_to_controller(self, action):
        logging.debug(f"Emitting '{action}' signal from MainWindow (originally emitted from LeftBar).")
        self.controller.signal_from_left_bar(action)

    def _configure_title_bar(self):
        self.title_bar.update()
        self.title_bar.minimize_tray_title_bar_clicked_signal.connect(self.minimize_to_tray)
        self.title_bar.minimize_title_bar_clicked_signal.connect(self.showMinimized)
        self.title_bar.maximize_title_bar_clicked_signal.connect(self.toggle_maximize_restore)
        self.title_bar.close_title_bar_clicked_signal.connect(
            lambda: self.close_requested_signal.emit("Title Bar")
            )

    def _setup_win_properties(self):
        self.restore_state()
        self.restore_geometry()
        self.setStyleSheet(all_styles.MAIN_WINDOW_STYLE)
        self.setWindowTitle(self.env_config_class.APP_NAME)  # Keep this, even though visible win title is custom.
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)

        title_bar_icon_relative_path = (os.path.join('resources/icons/title_bar_icons', self.env_config_class.ICON_NAME))
        self.icon_path = helper_fn.resource_path(title_bar_icon_relative_path)
        self.setWindowIcon(QIcon(self.icon_path))

    def set_win_state_and_geometry(self):
        logging.debug(f" Retrieving MainWin geometry and state and saving them to QSettings.")

        win_geometry = self.saveGeometry()
        win_state = self.saveState()
        try:
            logging.debug(f" Saving Window geometry and stated to settings.")

            self.settings_values.setValue("geometry", win_geometry)
            self.settings_values.setValue("windowState", win_state)

        except Exception as e:
            # Handle the exception or re-raise with a custom exception
            logging.error(f"Error saving window state and geometry: {str(e)}. Removing values from the settings.")

            self.settings_values.remove("geometry")
            self.settings_values.remove("windowState")

    def toggle_maximize_restore(self):
        if self.windowState() == Qt.WindowState.WindowNoState:  # If window not maximized
            self.setWindowState(Qt.WindowState.WindowMaximized)  # Then maximize it
        else:
            self.setWindowState(Qt.WindowState.WindowNoState)  # Otherwise, restore it to normal

    def minimize_to_tray(self):
        pass
        # self.hide()
        # self.tray_icon.show()
        # self.tray_icon.showMessage(
        #     f"{self.env_config_class.WIN_TITLE}",
        #     "The app is minimized to the system tray.",
        #     QSystemTrayIcon.MessageIcon.Information, 1000
        #     )
        # logging.debug(f" Application minimized to the system tray.")

    def closeEvent(self, event):
        try:
            self.set_win_state_and_geometry()
            print(f"closeEvent of MainFrame called from source: {self.closing_source}")
            logging.debug(f" Closing main window. closeEvent of MainWin called from source: {self.closing_source}")
            event.accept()  # This will accept the close action
        except Exception as e:
            logging.error(f" Exception type:{type(e)} (Error Description:{e}")
            event.ignore()

    def show_win_geometry(self):
        helper_fn.show_toast("Geometry", f"Geometry: {self.geometry()}", 4000)
        print(f"Geometry: {self.geometry()}")

    def restore_geometry(self):
        try:
            self.restoreGeometry(self.geometry)
        except TypeError:
            logging.debug(f" TypeError when restoring geometry. Setting default geometry.")
            self.setGeometry(340, 220, 650, 500)
        except Exception as e:
            print(f" Exception '{e}' while restoring state.")
            logging.error(f" Exception '{e}' while restoring state.")

    def restore_state(self):
        try:
            self.restoreState(self.state)
        except TypeError:
            logging.error(f" TypeError when restoring state.")
        except Exception as e:
            print(f" Exception '{e}' while restoring state.")
            logging.error(f" Exception '{e}' while restoring state.")


class HoverSplitter(QSplitter):
    def createHandle(self) -> QSplitterHandle:
        self.setHandleWidth(1)
        return HoverSplitterHandle(self.orientation(), self)


class HoverSplitterHandle(QSplitterHandle):
    def __init__(self, orientation: Qt.Orientation, parentSplitter: QSplitter):
        super().__init__(orientation, parentSplitter)
        self.setStyleSheet("background-color: #4C5F96;")
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: #494F74;")