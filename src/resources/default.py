import logging
import os
import sys
from datetime import datetime
from enum import Enum

VISIBLE_HEADERS = ["Start Time", "End Time", "Duration", "Task", "Remind Me"]


class Columns(Enum):
    """
    Order of these columns is important. It is used in the model to get the data from the model.
    """
    ID = "id"  # 0, hidden

    # Visible
    StartTime = "start_time"  # 1
    EndTime = "end_time"  # 2
    Duration = "duration"  # 3
    Name = "task_name"  # 4
    Reminder = "reminders"  # 5

    # Hidden
    Type = "type"  # 6
    Position = "position"  # 7


# Constants
DATE_FORMAT = "%I:%M %p, %Y-%m-%d"
DATETIME_COLUMN_KEYS = ["start_time", "end_time"]
FIXED_DATE = "2023-01-01"  # Year-month-day
LAST_CELL = "2023-01-02"


def convert_to_datetime(time_str):
    """ Convert time string to datetime object with a fixed date. """
    try:
        return datetime.strptime(f'{time_str}, {FIXED_DATE}', DATE_FORMAT)
    except Exception as e:
        logging.error(f"Exception type: {type(e)} while converting to datetime. Description: {e}")
        return None

def Convert_last_cell(time_str):
    """ Convert time string to datetime object with a fixed date. """
    try:
        return datetime.strptime(f'{time_str}, {LAST_CELL}', DATE_FORMAT)
    except Exception as e:
        logging.error(f"Exception type: {type(e)} while converting to datetime. Description: {e}")
        return None

default_tasks = (
    {
        Columns.StartTime.value: convert_to_datetime('12:00 AM'),
        Columns.EndTime.value: convert_to_datetime('07:00 AM'),
        Columns.Duration.value: 420,
        Columns.Name.value: 'Sleep/Wake up',
        Columns.Reminder.value: convert_to_datetime('12:00 AM'),
        Columns.Type.value: 'main',
        Columns.Position.value: 1
    },
    {
        Columns.StartTime.value: convert_to_datetime('07:00 AM'),
        Columns.EndTime.value: Convert_last_cell('12:00 AM'),
        Columns.Duration.value: 1020,
        Columns.Name.value: 'Last',
        Columns.Reminder.value: convert_to_datetime('07:00 AM'),
        Columns.Type.value: 'main',
        Columns.Position.value: 2
    },
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
    'New QuickTask': resource_path('../assets/buttons_icons/newQuickTask_icon.png'),
    'Settings': resource_path('../assets/buttons_icons/settings_icon.png'),

    'Back up': resource_path('assets/buttons_icons/back_up_icon.png'),
    'Open': resource_path('../assets/buttons_icons/open_icon.png'),
    'Open Data Folder': resource_path('assets/buttons_icons/open_folder_icon.png'),
    'Log Window': resource_path('assets/buttons_icons/log_window_icon.png'),
    'TEST': resource_path('assets/buttons_icons/test_icon.png'),
    'Exit': resource_path('assets/buttons_icons/exit_icon.png'),
    'Minimize to Tray': resource_path('assets/buttons_icons/minimize_to_tray.png'),
}
