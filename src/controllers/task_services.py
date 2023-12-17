import logging
from datetime import timedelta

from src.controllers.time_calculator import TimeCalculator
from utils import helper_fn


class TaskService:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view
        self.time_calculator = TimeCalculator()

    def create_new_task(self):
        """
        'replace_index' keyword is used to refer to the index where new row will be inserted.
        It's always the last row's index.

        'after_this' refers to the row above the 'replace_index' row and is used to get data for new row.
        """
        logging.debug("Executing New Task Request in TaskService.")

        selected_index = self.get_selected_index()
        replace_index = selected_index + 1
        if replace_index is None:
            logging.debug(f"No row selected. Returning.")
            return
        if replace_index == self.model.rowCount():
            logging.debug(f"Last row cannot be a subtask. Returning.")
            return

        logging.debug(f"Inserting new row at index:{replace_index}")

        # Crucial to get this before inserting new row (For updating)
        last_duration_original = self.model.get_row_data(replace_index, 'duration')

        # Get data of row above
        to_time_row_above = self.model.get_row_data(selected_index, 'to_time')
        task_sequence_row_above = self.model.get_row_data(selected_index, 'task_sequence')

        # For subtask name in 'task_name'
        sequence_new = task_sequence_row_above + 1
        ordinal_suffix_for_new = helper_fn.ordinal_suffix(sequence_new)

        to_time = to_time_row_above + timedelta(minutes=10)
        reminder = to_time_row_above - timedelta(minutes=5)

        data_to_insert = {
            'id': None,
            'from_time': to_time_row_above,
            'to_time': to_time,
            'duration': 10,
            'task_name': f'New Task. {sequence_new}{ordinal_suffix_for_new} row. Index:{replace_index}. '
                         f'sequence:{sequence_new}',
            'reminders': reminder,
            'type': 'main',
            'task_sequence': sequence_new,
        }

        self.model.insert_new_row(replace_index, data_to_insert)  # Insert new row

        logging.debug(f"New Task inserted. Updating last task from and duration.")

        self.update_sequences_below_row(replace_index)  # Update task sequences

    def create_new_subtask(self):
        selected_row_index = self.get_selected_index()
        if selected_row_index is None:
            logging.debug(f"No row selected. Returning.")
            return
        if selected_row_index == self.model.rowCount() - 1:
            logging.debug(f"Last row cannot be a subtask. Returning.")
            return

        selected_sequence = self.model.get_row_data(selected_row_index, column_key='task_sequence')
        replace_index = selected_row_index + 1

        # For subtask name in 'task_name'
        sequence_new = selected_sequence + 1
        ordinal_suffix_for_new = helper_fn.ordinal_suffix(sequence_new)

        subtask_data_to_insert = {
            'id': None,
            'from_time': None,
            'to_time': None,
            'duration': None,
            'task_name': f'New Subtask',
            'reminders': None,
            'type': 'subtask',
            'task_sequence': sequence_new,
        }

        logging.debug(f"replace_index:{replace_index}, selected_sequence:{selected_sequence},"
                      f"sequence_new:{sequence_new}, "
                      f" ordinal_suffix_for_new:{sequence_new}{ordinal_suffix_for_new}")

        self.model.insert_new_row(replace_index, subtask_data_to_insert)

        self.update_sequences_below_row(replace_index)

    def remove_row_and_delete_data(self):
        logging.debug(f"Remove and Delete executing in TaskServices.")

        selection_model = self.table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            logging.debug(f"No row selected. Nothing to delete.")
            return
        row_to_delete = self.get_selected_index()

        try:
            sequence = self.model.get_row_data(row_to_delete, 'task_sequence')
            task_name = self.model.get_row_data(row_to_delete, 'task_name')
            row_id = self.model.get_row_data(row_to_delete, 'id')

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
                self.update_sequences_below_row(row_to_delete)

    def update_sequences_below_row(self, row_index):
        for row in range(row_index, self.model.rowCount()):
            logging.debug(f"Updating sequence for row:{row}. Sequence:{row + 1}")
            self.model.set_row_data(row, new_task_sequence=row + 1)

    def get_selected_index(self):
        selection_model = self.table_view.selectionModel()
        selected_row_indices = selection_model.selectedIndexes()

        if not selected_row_indices:
            logging.debug(f"No row selected. Return.")
            return None

        selected_row_index = selected_row_indices[0].row()
        logging.debug(f"Selected row index:{selected_row_index}")
        return selected_row_index

    def save_task(self, task_data):
        pass
