import logging

from controllers.TaskControllers import TaskUtilityService


def start_new_maintask(model, view):
    selected_row = _validate_selected_row(model, view)
    if selected_row is None:
        return

    backup = model.backup_state()

    try:
        new_task_data, data_below_new = _data_retrieval(selected_row, model)
    except Exception as e:
        _handle_data_retrieval_exception(e)
        return

    try:
        _insert_and_update(selected_row, new_task_data, data_below_new, backup, model)
    except Exception as e:
        _handle_insert_and_update_exception(e, backup, model)


def _data_retrieval(selected_row, model):
    new_task_data = TaskUtilityService.calculate_new_task_data(selected_row, model)
    data_below_new = model.auto_time_updater.data_after_new_task(selected_row, new_task_data)

    if not (new_task_data and data_below_new):
        logging.error("New task data or data for row below new task is missing.")
        raise Exception("Data retrieval failed")

    return new_task_data, data_below_new


def _insert_and_update(selected_row, new_task_data, data_below_new, backup, model):
    insert_successful = model.tasker_model.insert_new_task(selected_row + 1, new_task_data)
    if insert_successful is not True:
        logging.error("Inserting new task wasn't successful")
        model.rollback_state(backup)
        raise Exception("Insert failed")
    # Perform update after new task operation
    model.auto_time_updater.update_after_new_task(data_below_new)


def _validate_selected_row(model, table_view):
    selected_row = TaskUtilityService.get_selected_row(table_view)
    if not TaskUtilityService.is_valid_task_row(model, selected_row):
        return None

    return selected_row


def _handle_data_retrieval_exception(e):
    logging.error(f"Exception type:{type(e)} when calculating data for new task. Error:{e}")
    return None


def _handle_insert_and_update_exception(e, backup, model):
    logging.error(f"Exception type:{type(e)} when inserting new task. Error:{e}")
    model.rollback_state(backup)
    return
