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

        print(f"data_linked_mainTaskRow:{updates_linked_maintask}")

        data_new_maintask = TaskUtilityService.calculate_data_new_maintask(model, linked_maintask, updates_linked_maintask)

        # IMPORTANT! For now, there is no change in shifted_task (as the new task takes its duration from
        # clicked or linked_maintask)
        updates_for_shifted_task = model.auto_timeUpdater.calculate_updates_tobe_shifted_maintask(clicked_row, data_new_maintask)

    except Exception as e:
        logging.error(f"Error during data retrieval. Type: {type(e)}. Error:{e}")
        raise e

    prepared_data = (data_new_maintask, updates_linked_maintask, updates_for_shifted_task)
    return prepared_data


def _insert_and_update(clicked_row, data_for_update, model):
    # Insert New Row
    try:
        model.model_utility_service.insert_row_with_data(clicked_row + 1, data_for_update[0])
    except Exception as e:
        logging.error(f"Inserting new MainTask Failed. Type:{type(e)}. Error:{e}")
        raise e

    # Update data in selected row
    try:
        model.auto_timeUpdater.update_linked_maintask(data_for_update[1])
    except Exception as e:
        logging.error(f"Inserting new MainTask Failed. Type:{type(e)}. Error:{e}")
        raise e

    # Update data in row below new
    try:
        model.auto_timeUpdater.update_shifted_maintask(data_for_update[2])
    except Exception as e:
        logging.error(f"Error when updating after new task was added. Exception type: {type(e)}. Error:{e}")
        raise e
