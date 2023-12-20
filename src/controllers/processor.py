import logging
from datetime import timedelta

from resources.default import Columns
from utils import helper_fn


class Processor:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

    def calculate_new_task_data(self, selected_row):
        logging.debug("Calculating new task data in TaskService.")
        # if selected task is QuickTask, get the first main task from above
        try:
            if self.model.get_item_from_model(selected_row, Columns.Type.value) == 'QuickTask':
                logging.debug(f" -- Selected row = QuickTask. Retrieving first main task row index above.")
                main_task_index = self.get_main_task_index(selected_row)
                logging.debug(f" -- (Main task index:{main_task_index})")
            else:
                main_task_index = selected_row
                logging.debug(f" -- Selected row = Main Task. Index:{main_task_index}")

            # Get EndTime and Position of the main task
            end_main_task = self.model.get_item_from_model(main_task_index, Columns.EndTime.value)
            position_main_task = self.model.get_item_from_model(main_task_index, Columns.Position.value)

            new_end_time = end_main_task + timedelta(minutes=10)
            new_reminder = end_main_task - timedelta(minutes=10)

            # Prepare data for the new QuickTask
            data_to_insert = {
                Columns.ID.value: None,
                Columns.StartTime.value: end_main_task,
                Columns.EndTime.value: new_end_time,
                Columns.Duration.value: 10,
                Columns.Name.value: f'New Task.',
                Columns.Reminder.value: new_reminder,
                Columns.Type.value: 'main',
                Columns.Position.value: position_main_task + 1,
            }

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when calculating data for new task. Error:{e}")
            raise

        # ToDo: Update last task position
        return data_to_insert

    def update_positions(self, affected_row, operation):
        """
        Update sequences of rows below the affected row index.

        Args:
        affected_row (int): The index of the row where the operation (addition or deletion) occurred.
        operation (str): Type of operation, either 'add' or 'delete'.
        """
        logging.debug(f"Updating sequences of rows below row index: {affected_row} after {operation} operation.")

        # Determine the operation type: addition or deletion
        position_change = 1 if operation == 'add' else -1

        for row in range(affected_row, self.model.rowCount()):
            col_key = Columns.Position.value
            old_position = self.model.get_item_from_model(row, col_key)
            new_position = old_position + position_change

            try:
                update_successful = self.model.set_item_in_model(row, col_key, new_position)
                if not update_successful:
                    logging.error(f"Updating sequence for row: {row} failed.")
                    return False

            except Exception as e:
                logging.error(f"Exception type: {type(e)}  (Error Description: {e}")
                return

        return True

    def get_selected_row(self):
        selection_model = self.table_view.selectionModel()
        selected_row_indices = selection_model.selectedIndexes()

        if not selected_row_indices:
            logging.debug(f"No row selected. Return.")
            return None

        selected_row = selected_row_indices[0].row()
        logging.debug(f" (Selected row index:{selected_row})")
        return selected_row

    def get_main_task_index(self, clicked_row):
        # Find the main task associated with the selected QuickTask
        logging.debug(f" (Finding main task above the selected QuickTask.)")

        while clicked_row >= 0:
            if self.model.get_item_from_model(clicked_row, Columns.Type.value) == 'main':
                logging.debug(f" -- Main task found at row index: {clicked_row}")
                break
            else:
                clicked_row -= 1

        # If no main task found, abort the operation
        if clicked_row < 0:
            logging.error(" -- No main task found above the selected QuickTask.")
            return None

        return clicked_row

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
        clicked_row_type = self.model.get_item_from_model(clicked_row, Columns.Type.value)
        row_below_type = self.model.get_item_from_model(clicked_row + 1, Columns.Type.value)

        if clicked_row_type == 'QuickTask' and row_below_type == 'QuickTask':
            logging.debug(" -- Cannot add new row between QuickTasks.")
            return False

        return True

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
            logging.debug(" -- No row selected.")
            return False
        if selected_row <= 0:
            logging.debug(" -- Cannot delete the first row.")
            return False
        if selected_row == self.model.rowCount() - 1:
            logging.debug(" -- Cannot delete the last row.")
            return False

        return True

