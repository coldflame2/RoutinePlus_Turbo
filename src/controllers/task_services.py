import logging
from datetime import timedelta

from resources.default import Columns
from utils import helper_fn


class TaskService:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

    def create_new_task(self):
        logging.debug("Executing New Task Request in TaskService.")
        clicked_row = self.get_selected_index()

        new_task_valid = self.is_new_task_valid(clicked_row)
        if not new_task_valid:
            return

        main_task_index = self.get_main_task_index(clicked_row)

        replace_index = clicked_row + 1

        # Get data from the main task
        end_main_task = self.model.get_item(main_task_index, Columns.EndTime.value)
        position_main_task = self.model.get_item(main_task_index, Columns.Position.value)

        # Calculate data for the new QuickTask
        sequence_new = position_main_task + 1  # or any other logic you need
        ordinal_suffix_for_new = helper_fn.ordinal_suffix(sequence_new)
        end_new = end_main_task + timedelta(minutes=10)
        reminder_new = end_main_task - timedelta(minutes=5)

        # Prepare data for the new QuickTask
        data_to_insert = {
            Columns.ID.value: None,
            Columns.StartTime.value: end_main_task,
            Columns.EndTime.value: end_new,
            Columns.Duration.value: 10,
            Columns.Name.value: f'New QuickTask. {sequence_new}{ordinal_suffix_for_new} row. Index: {replace_index}. sequence: {sequence_new}',
            Columns.Reminder.value: reminder_new,
            Columns.Type.value: 'main',  # Set as 'QuickTask' since it's inserted under a QuickTask
            Columns.Position.value: sequence_new,
        }

        try:
            self.model.insert_new_row(replace_index, data_to_insert)  # Insert new QuickTask row
        except Exception as e:
            logging.error(f"Exception type: {type(e).__name__}. Error: {e}")

        # Update positions for rows below the new QuickTask
        update_success = self.update_positions(replace_index)

        if update_success:
            logging.debug(" -- Updating sequences of rows below successful.")
        else:
            logging.error("Updating sequences of rows below failed.")

        logging.debug(f"SUCCESS - New Task: New QuickTask inserted at index: {replace_index}.")

    def create_new_QuickTask(self):
        logging.debug("Executing New QuickTask Request in TaskService.")
        selected_row_index = self.get_selected_index()
        if selected_row_index is None:
            logging.debug(f"No row selected. Returning.")
            return
        if selected_row_index == self.model.rowCount() - 1:
            logging.debug(f"Last row cannot be a QuickTask. Returning.")
            return

        replace_index = selected_row_index + 1
        logging.debug(f"Inserting new QuickTask at index:{replace_index}")

        # For QuickTask name in Columns.Name.value
        selected_sequence = self.model.get_item(selected_row_index, column_key=Columns.Position.value)
        sequence_new = selected_sequence + 1
        task_serial = f'{sequence_new}{helper_fn.ordinal_suffix(sequence_new)}'  # Just for display

        QuickTask_data_to_insert = {
            Columns.ID.value: None,
            Columns.StartTime.value: None,
            Columns.EndTime.value: None,
            Columns.Duration.value: None,
            Columns.Name.value: f'New QuickTask. {task_serial}',
            Columns.Reminder.value: None,
            Columns.Type.value: 'QuickTask',
            Columns.Position.value: sequence_new,
        }

        logging.debug(f"replace_index:{replace_index}, selected_sequence:{selected_sequence},"
                      f"sequence_new:{sequence_new}, "
                      f" ordinal_suffix{task_serial}")

        self.model.insert_new_row(replace_index, QuickTask_data_to_insert)

        self.update_positions(replace_index)

    def remove_row_and_delete_data(self):
        logging.debug(f"Remove and Delete executing in TaskServices.")

        selection_model = self.table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            logging.debug(f"No row selected. Nothing to delete.")
            return
        row_to_delete = self.get_selected_index()

        try:
            sequence = self.model.get_item(row_to_delete, Columns.Position.value)
            task_name = self.model.get_item(row_to_delete, Columns.Name.value)
            row_id = self.model.get_item(row_to_delete, Columns.ID.value)

        except Exception as e:
            logging.error(f"Exception type:{type(e)}  (Error Description:{e}")
            return

        logging.debug(f"Row to delete index:{row_to_delete}, Sequence:{sequence}, "
                      f"Task Name:{task_name}, Row ID:{row_id}")

        if sequence == self.model.rowCount():
            logging.debug(f"Last row cannot be deleted.")
            return

        if sequence == 1:
            logging.debug(f"First row cannot be deleted.")
            return

        else:
            delete_success = self.model.delete_row_and_data(row_to_delete)

            if delete_success:  # update task sequences
                logging.debug(f"Row deleted successfully. Updating task sequences")

                # update task sequences of all rows below the deleted row
                self.update_positions(row_to_delete)

    def update_positions(self, row_index):
        row_below = row_index + 1
        for row in range(row_index, self.model.rowCount()):
            logging.debug(f"  (Updating position for row:{row} to {row + 1})")
            col_key = Columns.Position.value
            old_position = self.model.get_item(row, col_key)
            new_position = old_position + 1
            try:
                update_successful = self.model.set_item(row, col_key, new_position)
                if not update_successful:
                    logging.error(f"Updating sequence for row:{row} failed.")
                    return False

            except Exception as e:
                logging.error(f"Exception type:{type(e)}  (Error Description:{e}")
                return

        return True

    def get_selected_index(self):
        selection_model = self.table_view.selectionModel()
        selected_row_indices = selection_model.selectedIndexes()

        if not selected_row_indices:
            logging.debug(f"No row selected. Return.")
            return None

        selected_row = selected_row_indices[0].row()
        logging.debug(f" (Selected row index:{selected_row})")
        return selected_row

    def is_new_task_valid(self, clicked_row):
        if clicked_row is None:
            logging.debug(" -- No row selected.")
            return False
        if clicked_row == self.model.rowCount() - 1:
            logging.debug(" -- Cannot add new row below the last row.")
            return False

        return True

    def save_task(self, task_data):
        pass

    def get_main_task_index(self, clicked_row):
        # Find the main task associated with the selected QuickTask
        logging.debug(f" (Finding main task above the selected QuickTask.)")
        while clicked_row >= 0:
            if self.model.get_item(clicked_row, Columns.Type.value) == 'main':
                logging.debug(f" -- Main task found at row index: {clicked_row}")
                break
            else:
                clicked_row -= 1

        # If no main task found, abort the operation
        if clicked_row < 0:
            logging.error(" -- No main task found above the selected QuickTask.")
            return None

        return clicked_row
