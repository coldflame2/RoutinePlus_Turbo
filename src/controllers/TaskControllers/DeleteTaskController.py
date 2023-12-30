import logging

from controllers.TaskControllers import TaskUtilityService
from resources.default import Columns


def start_deleting_task(model, view):
    logging.debug(f"'Delete Task' requested in controller.")
    selected_row = TaskUtilityService.get_selected_row(view)

    if not TaskUtilityService.is_row_deletable(model, selected_row):
        logging.debug(f"Selected row ({selected_row}) is invalid for deletion.")

    # Backup the current state
    backup_before_delete = model.backup_state()

    try:
        # Get data for replaced row (row that will replace the to-be deleted row index)
        replaced_row_data = model.auto_time_updater.calculate_data_after_deletion(selected_row)

        if not replaced_row_data:
            logging.error(f"Replaced Row Data is missing.")
            return

        # Perform Delete operation
        delete_successful = model.tasker_model.delete_row_and_data(selected_row)

        if delete_successful is not True:
            logging.error(f"Error While Deleting {selected_row} row.")
            return

        if model.get_item_from_model(selected_row, Columns.Type.value) == 'QuickTask':

            # Update only positions
            model.auto_time_updater.update_positions(selected_row, "delete")
        else:
            # Update the start time and duration of the row below the deleted row
            model.auto_time_updater.update_after_delete_task(replaced_row_data)

        logging.debug(f"Row {selected_row} deleted from model and SQLite database.")

    except Exception as e:
        logging.error(f"Exception type: (type{e}). Error:{e}")
        model.rollback_state(backup_before_delete)
        return
