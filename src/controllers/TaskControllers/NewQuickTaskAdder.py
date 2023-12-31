import logging

from controllers.TaskControllers import TaskUtilityService


def start_new_quicktask(model, view):
    logging.debug("New QuickTask requested in controller.")
    selected_row = TaskUtilityService.clicked_row_index(view)

    if not TaskUtilityService.is_rowValid(model, selected_row):
        logging.debug(f"Selected row is invalid. Selected row: {selected_row}")
        return

    # Backup the current state
    backup = model.backup_state()

    try:
        new_quick_task_data = TaskUtilityService.calculate_new_quick_task_data(model, selected_row)

        if not new_quick_task_data:
            logging.debug("New quick task data is missing.")
            return

        logging.debug(f"New quick task data calculated. Data: {new_quick_task_data}")

        # Perform the insert operation
        insert_successful = model.model_utility_service.insert_row_with_data(selected_row + 1, new_quick_task_data)

        if insert_successful is not True:
            logging.error(f" Inserting QuickTask wasn't successful")
            return

        model.auto_timeUpdater.update_after_new_quick_task(selected_row, new_quick_task_data)

    except Exception as e:
        logging.error(f"Exception occurred: {type(e)}. Error: {e}")

        # Rollback to the previous state
        model.rollback_state(backup)
        return

    logging.debug("New quick task added successfully.")
