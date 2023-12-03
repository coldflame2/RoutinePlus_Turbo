import os
import logging
from logging import handlers

from PyQt6.QtCore import Qt

from src.utils import helper_fn

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QPushButton


def setup_root_logger():  # This is a root logger, which is called in main(), and so it applies to the whole app
    environment_cls = helper_fn.get_environment_cls(False, caller='debugging')
    logs_folder_path = os.path.join(environment_cls.APP_FOLDER_PATH, environment_cls.LOG_FOLDER_NAME)
    os.makedirs(logs_folder_path, exist_ok=True)  # Create the log folder if it doesn't exist

    log_file_path = os.path.join(logs_folder_path, environment_cls.LOG_FILE_NAME)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=900000, backupCount=6
        )

    log_text_format = ('[%(levelname)s][%(lineno)d][%(filename)s] %(message)s '
                       ' [TIME: %(asctime)s][%(name)s]')

    '''
    Regex for LogExpert: \[(.+?)\]\[(\d+)\]\[(.+?)\](.*?)\[TIME: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\]\[(.+?)\]

    '''

    file_handler.setFormatter(logging.Formatter(log_text_format))
    file_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)


class LogDisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs")
        self.resize(560, 560)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        main_layout = QVBoxLayout(self)
        log_display = QPlainTextEdit(self)
        log_display.setReadOnly(True)
        main_layout.addWidget(log_display)

        clear_log_button = QPushButton("Clear Log", self)
        clear_log_button.clicked.connect(log_display.clear)
        main_layout.addWidget(clear_log_button)
        self.setup_logging(log_display)
        self.hide()

    def setup_logging(self, log_display_widget):
        text_edit_handler = QTextEditHandler(log_display_widget)
        log_format_for_win = '[%(levelname)s] %(message)s'
        text_edit_handler.setFormatter(logging.Formatter(log_format_for_win))
        log_win_logger = logging.getLogger()
        log_win_logger.addHandler(text_edit_handler)


class QTextEditHandler(logging.Handler):
    def __init__(self, text_edit_widget):
        super().__init__()
        self.text_edit_widget = text_edit_widget

    def emit(self, record):
        formatted_record = self.format(record)
        self.text_edit_widget.appendPlainText(formatted_record)