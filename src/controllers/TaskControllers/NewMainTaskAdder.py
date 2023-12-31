import logging

from controllers.TaskControllers import TaskUtilityService


def initiate_maintask_addition(model, view):
    clicked_row = TaskUtilityService.get_clicked_row(model, view)
    if clicked_row is None:
        return

    state_backup = model.backup_state()

    try:
        data_for_update = _prepare_data_for_task_insertion(clicked_row, model)

    except Exception as e:
        logging.error(f"Error at Data Retrieval during NewTask insert operation. Type:{type(e)}. Error: "
                      f"{e}")
        return

    try:
        _insert_and_update(clicked_row, data_for_update, model)

    except Exception as e:
        logging.error(f"{e} Error. Type:{type(e)} during NewTask insert operation.")
        model.rollback_state(state_backup)
        return


def _prepare_data_for_task_insertion(clicked_row, model):
    try:
        linked_maintask = TaskUtilityService.find_linked_maintask(model, clicked_row)

        updates_linked_maintask = model.auto_timeUpdater.calculate_updates_linked_maintask(linked_maintask)
        print(f"updates_linked_maintask = {updates_linked_maintask}")

        data_new_maintask = TaskUtilityService.calculate_data_new_maintask(updates_linked_maintask)

        # IMPORTANT! For now, there is no change in shifted_task (as the new task affects the row above by
        # taking one minute from its duration, not from the task below)
        updates_for_shifted_task = model.auto_timeUpdater.calculate_updates_tobe_shifted_maintask(clicked_row, data_new_maintask)

    except Exception as e:
        logging.error(f"Error during data retrieval. Type: {type(e)}. Error:{e}")
        raise e

    prepared_data = (updates_linked_maintask, data_new_maintask, updates_for_shifted_task)
    return prepared_data


def _insert_and_update(clicked_row, prepared_data, model):
    """
    Flow:
     - First update linked MainTask (or clicked row if it is already the MainTask)
     - Then insert new MainTask with its data (data_for_update[0])
     - Then update shifted row (below new task) (NOTE: No data is changed for this row, for NOW)
     - Then update positions starting from new inserted row index
    """

    # Update data in selected row
    try:
        model.auto_timeUpdater.update_linked_maintask(prepared_data[0])
    except Exception as e:
        logging.error(f"Inserting new MainTask Failed. Type:{type(e)}. Error:{e}")
        raise e

    # Insert New Row
    try:
        model.model_utility_service.insert_row_in_model(clicked_row + 1, prepared_data[1])
    except Exception as e:
        logging.error(f"Inserting new MainTask Failed. Type:{type(e)}. Error:{e}")
        raise e

    # Update data in row below new
    try:
        model.auto_timeUpdater.update_shifted_maintask(prepared_data[2])
    except Exception as e:
        logging.error(f"Error when updating after new task was added. Exception type: {type(e)}. Error:{e}")
        raise e

    # Update Positions
    try:
        model.auto_timeUpdater.update_positions(clicked_row + 1, "add")
    except Exception as e:
        logging.error(f"Error when updating positions after new task was added. Exception type: {type(e)}. "
                      f"Error:{e}")
        raise e
