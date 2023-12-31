import logging
from datetime import timedelta

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication

from resources.default import Columns


def calculate_data_new_maintask(updates_linked_maintask):
    logging.debug(f"Calculating data for to-be new MainTask.")
    try:
        endtime_linked_maintask_after_insertion = updates_linked_maintask[1][2]

        # Calculate end time and reminder for the new task
        duration_new_maintask = 1
        endtime_new_maintask = endtime_linked_maintask_after_insertion + timedelta(minutes=duration_new_maintask)
        reminder_new_maintask = endtime_linked_maintask_after_insertion - timedelta(minutes=duration_new_maintask)

    except Exception as e:
        logging.error(f"Exception type:{type(e)} when calculating data for new task. Error:{e}")
        raise e

    # Prepare data for the new QuickTask
    data_new_maintask = {
        Columns.ID.value: None,  # ID is inserted automatically when data is inserted in SQLite database
        Columns.StartTime.value: endtime_linked_maintask_after_insertion,
        Columns.EndTime.value: endtime_new_maintask,
        Columns.Duration.value: duration_new_maintask,
        Columns.Name.value: f'New Task.',
        Columns.Reminder.value: reminder_new_maintask,
        Columns.Type.value: 'MainTask',
        Columns.Position.value: None,  # Position is updated after (in NewMainTaskAdder)
    }

    logging.debug(f"Data for new MainTask to be added:{data_new_maintask}")
    return data_new_maintask


def find_linked_maintask(model, clicked_row):
    """
    Checks if selected row is 'MainTask' or 'QuickTask.'
    If it is QuickTask, call the find_main_task_row method.

    :param model:
    :param clicked_row:
    :return:
    """
    if model.get_item_from_model(clicked_row, Columns.Type.value) == 'QuickTask':
        # if selected task is QuickTask, get the first main task from above
        try:
            current_row = clicked_row
            while current_row >= 0:
                if model.get_item_from_model(current_row, Columns.Type.value) == 'MainTask':
                    return current_row
                else:
                    current_row -= 1

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

    else:
        # if clicked row is main task, return it
        return clicked_row


def find_main_task_above(model, initial_clicked_row):  # For New Task Data
    """
    Find the main task above with the selected QuickTask.

    :param model:
    :param initial_clicked_row: The row index that the user initially clicked.
    :return: The row index of the main task found, or None if no main task is found.
    """
    logging.debug(f"Clicked Row is subtask. Finding MainTask above it.")
    current_row = initial_clicked_row
    while current_row >= 0:
        if model.get_item_from_model(current_row, Columns.Type.value) == 'MainTask':
            return current_row
        else:
            current_row -= 1

    logging.error("No main task found above the selected QuickTask.")
    return None


def calculate_new_quick_task_data(model, selected_row):
    selected_sequence = model.get_item_from_model(selected_row, column_key=Columns.Position.value)

    quick_task_data_to_insert = {
        Columns.ID.value: None,
        Columns.StartTime.value: None,
        Columns.EndTime.value: None,
        Columns.Duration.value: None,
        Columns.Name.value: f'New QuickTask.',
        Columns.Reminder.value: None,
        Columns.Type.value: 'QuickTask',
        Columns.Position.value: selected_sequence + 1,
    }

    return quick_task_data_to_insert


def is_rowDeletable(model, selected_row):
    if selected_row is None:
        logging.debug(" --(No row selected.)")
        return False
    if selected_row <= 0:
        logging.debug(" --(Cannot delete the first row.)")
        return False
    if selected_row == model.rowCount() - 1:
        logging.debug(" --(Cannot delete the last row.)")
        return False

    return True


def is_rowValid(model, clicked_row):
    if clicked_row is None:
        logging.debug(" -- No row selected.")
        return False
    if clicked_row < 0:
        logging.debug(" -- Cannot add new task above the first row.")
        return False
    if clicked_row == model.rowCount() - 1:
        logging.debug(" -- Cannot add new task below the last row.")
        return False

    return True


def get_clicked_row(model, view):
    clicked_row = clicked_row_index(view)

    if is_rowValid(model, clicked_row) is False:
        return None

    try:
        clicked_row_type = model.get_item_from_model(clicked_row, Columns.Type.value)
        row_below_type = model.get_item_from_model(clicked_row + 1, Columns.Type.value)

    except Exception as e:
        logging.error(f"Error while getting row types. Exception type: {type(e)}. Error:{e}")
        return None

    if clicked_row_type == 'QuickTask' and row_below_type == 'QuickTask':
        logging.debug(" -- Cannot add new row between QuickTasks.")
        return None

    if model.get_item_from_model(clicked_row, Columns.Duration.value) == 1:
        logging.debug(f"Existing Task is already of one minute.")
        return None

    return clicked_row


def clicked_row_index(table_view):
    selection_model = table_view.selectionModel()
    selected_row_indices = selection_model.selectedIndexes()

    if not selected_row_indices:
        return None

    selected_row = selected_row_indices[0].row()
    return selected_row
