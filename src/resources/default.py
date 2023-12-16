import logging
import os
import sys
from aenum import Enum, NoAlias
from datetime import datetime

COLUMN_KEYS = ["id", "from_time", "to_time", "duration", "task_name", "reminders", "type", "task_sequence"]
VISIBLE_HEADERS = ["ID", "Start", "End", "Duration", "Task", "Reminders", "type", "Sequence"]

# Constants
DATE_FORMAT = "%I:%M %p, %Y-%m-%d"
DATETIME_COLUMN_KEYS = ["from_time", "to_time"]
FIXED_DATE = "2023-01-01"


def convert_to_datetime(time_str):
    """ Convert time string to datetime object with a fixed date. """
    try:
        return datetime.strptime(f'{time_str}, {FIXED_DATE}', DATE_FORMAT)
    except Exception as e:
        logging.error(f"Exception type: {type(e)} while converting to datetime. Description: {e}")
        return None


default_tasks = (
    {
        'from_time': convert_to_datetime('12:00 AM'),
        'to_time': convert_to_datetime('07:00 AM'),
        'duration': 420,
        'task_name': 'Sleep/Wake up',
        'reminders': convert_to_datetime('12:00 AM'),
        'type': 'main',
        'task_sequence': 1
        },
    {
        'from_time': convert_to_datetime('07:00 AM'),
        'to_time': convert_to_datetime('12:00 AM'),
        'duration': 1020,
        'task_name': 'Sleep',
        'reminders': convert_to_datetime('06:55 AM'),
        'type': 'main',
        'task_sequence': 2
        }
    )


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in bundled mode (either --onedir or --onefile)
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


# This dictionary maps button names to their respective icon paths.
BUTTON_ICON_PATHS = {
    'Save': resource_path('../assets/buttons_icons/save_icon.png'),
    'Save As': resource_path('../assets/buttons_icons/saveas_icon.png'),

    'New Task': resource_path('../assets/buttons_icons/newtask_icon.png'),
    'New Subtask': resource_path('../assets/buttons_icons/newsubtask_icon.png'),
    'Settings': resource_path('../assets/buttons_icons/settings_icon.png'),

    'Back up': resource_path('assets/buttons_icons/back_up_icon.png'),
    'Open': resource_path('../assets/buttons_icons/open_icon.png'),
    'Open Data Folder': resource_path('assets/buttons_icons/open_folder_icon.png'),
    'Log Window': resource_path('assets/buttons_icons/log_window_icon.png'),
    'TEST': resource_path('assets/buttons_icons/test_icon.png'),
    'Exit': resource_path('assets/buttons_icons/exit_icon.png'),
    'Minimize to Tray': resource_path('assets/buttons_icons/minimize_to_tray.png'),
    }


class ColorsEn(Enum):
    _settings_ = NoAlias
    ROW_COLOR = "#DDEAF0"
    ALT_ROW_COLOR = "#C4D0D5"
    SUBTASK_ROW_COLOR = "#364135"
    HEADERS_COLOR = "#36436A"
    HEADERS_FONT_COLOR = "#DDEAF3"
    CURRENT_ROW_COLOR = "#D7B1D9"


class NumericEn(Enum):
    _settings_ = NoAlias

    FONT_SIZE = 11
    SUBTASK_FONT_SIZE = 11
    HEADERS_FONT_SIZE = 15
    ROW_HEIGHT = 40
    SUBTASK_HEIGHT = 25
    REMINDER_LEAD_TIME = 5


class BoolEn(Enum):
    _settings_ = NoAlias

    REMINDERS = True
    EXIT_CONFIRM = True
    AUTO_ROW_HEIGHT = False
    AUTO_FONT = False