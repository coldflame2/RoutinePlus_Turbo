import logging
from datetime import timedelta

from resources.default import Columns


class Processor:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

    def calculate_new_task_data(self, selected_row):
        logging.debug("Calculating new task data in TaskService.")

        try:
            # Get the main task index for data
            main_task_index_for_data = self.get_main_task_index(selected_row)

            # Get EndTime and Position of the main task
            end_time_main_task = self.model.get_item_from_model(main_task_index_for_data, Columns.EndTime.value)
            position_main_task = self.model.get_item_from_model(main_task_index_for_data, Columns.Position.value)

            # Calculate end time and reminder for the new task
            duration = 10
            end_time_for_new = end_time_main_task + timedelta(minutes=duration)
            reminder_for_new = end_time_main_task - timedelta(minutes=duration)

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when calculating data for new task. Error:{e}")
            return None

        # Prepare data for the new QuickTask
        data_to_insert = {
            Columns.ID.value: None,
            Columns.StartTime.value: end_time_main_task,
            Columns.EndTime.value: end_time_for_new,
            Columns.Duration.value: duration,
            Columns.Name.value: f'New Task.',
            Columns.Reminder.value: reminder_for_new,
            Columns.Type.value: 'main',
            Columns.Position.value: position_main_task + 1,
        }

        return data_to_insert

    def get_main_task_index(self, clicked_row):
        """
        Checks if selected row is 'main' or 'QuickTask.'
        If it is QuickTask, call the find_main_task_row method.

        :param clicked_row:
        :return:
        """
        if self.model.get_item_from_model(clicked_row, Columns.Type.value) == 'QuickTask':
            # if selected task is QuickTask, get the first main task from above

            logging.debug(f" --(Clicked row is QuickTask. Calling find_main_task method.)")

            try:
                return self.find_main_task_above(clicked_row)

            except Exception as e:
                logging.error(f"Exception type: {type(e)}. Error:{e}")
                return None

        else:
            # if clicked row is main task, return itself
            logging.debug(f" --(Clicked row is main task. Returning same for new row data.)")
            return clicked_row

    def find_main_task_above(self, initial_clicked_row):  # For New Task Data
        """
        Find the main task above with the selected QuickTask.

        :param initial_clicked_row: The row index that the user initially clicked.
        :return: The row index of the main task found, or None if no main task is found.
        """
        logging.debug("Finding main task above the selected QuickTask.")

        current_row = initial_clicked_row
        while current_row >= 0:
            if self.model.get_item_from_model(current_row, Columns.Type.value) == 'main':
                logging.debug(f"Main task found at row index: {current_row}")
                return current_row
            else:
                current_row -= 1

        logging.error("No main task found above the selected QuickTask.")
        return None

    def calculate_new_quick_task_data(self, selected_row):
        replace_index = selected_row + 1
        logging.debug(f"Inserting new QuickTask at index:{replace_index}")

        # For QuickTask name in Columns.Name.value
        selected_sequence = self.model.get_item_from_model(selected_row, column_key=Columns.Position.value)

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

    def is_row_deletable(self, selected_row):
        if selected_row is None:
            logging.debug(" --(No row selected.)")
            return False
        if selected_row <= 0:
            logging.debug(" --(Cannot delete the first row.)")
            return False
        if selected_row == self.model.rowCount() - 1:
            logging.debug(" --(Cannot delete the last row.)")
            return False

        return True

    def is_valid_row(self, clicked_row):
        if clicked_row is None:
            logging.debug(" -- No row selected.")
            return False
        if clicked_row < 0:
            logging.debug(" -- Cannot add new task above the first row.")
            return False
        if clicked_row == self.model.rowCount() - 1:
            logging.debug(" -- Cannot add new task below the last row.")
            return False

        return True

    def is_valid_task_row(self, clicked_row):
        if self.is_valid_row(clicked_row) is False:
            return False

        clicked_row_type = self.model.get_item_from_model(clicked_row, Columns.Type.value)
        row_below_type = self.model.get_item_from_model(clicked_row + 1, Columns.Type.value)

        if clicked_row_type == 'QuickTask' and row_below_type == 'QuickTask':
            logging.debug(" -- Cannot add new row between QuickTasks.")
            return False

        return True

    def get_selected_row(self):
        selection_model = self.table_view.selectionModel()
        selected_row_indices = selection_model.selectedIndexes()

        if not selected_row_indices:
            return None

        selected_row = selected_row_indices[0].row()
        return selected_row
