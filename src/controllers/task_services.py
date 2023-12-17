import logging
from datetime import timedelta

from src.controllers.time_calculator import TimeCalculator


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

        # Get indices
        replace_index = self.model.rowCount() - 1
        second_last_index = replace_index - 1

        logging.debug(f"Last row index and index to insert at:{replace_index}. ")

        # Crucial to get this before inserting new row (For updating)
        last_duration_original = self.model.get_row_data(replace_index, 'duration')

        # Get data of row above
        to_time_row_above = self.model.get_row_data(second_last_index, 'to_time')
        task_sequence_row_above = self.model.get_row_data(second_last_index, 'task_sequence')

        to_time = to_time_row_above + timedelta(minutes=10)
        reminder = to_time_row_above - timedelta(minutes=5)

        data_to_insert = {
            'id': None,
            'from_time': to_time_row_above,
            'to_time': to_time,
            'duration': 10,
            'task_name': 'New Task',
            'reminders': reminder,
            'type': 'main',
            'task_sequence': task_sequence_row_above + 1,
        }

        self.model.insert_new_row(replace_index, data_to_insert)  # Insert new row

        logging.debug(f"New Task inserted. Updating last task from and duration.")

        self.update_last_task(data_to_insert, last_duration_original)

    def update_last_task(self, new_row_data, last_task_duration_original):
        """
        This is to update the very last row in the table. And this is after a row has been inserted
        above the last one.
        """

        logging.debug(f"Updating last task in TaskServices.")

        from_time = to_time_new_row = new_row_data.get('to_time')  # New from_time of last task
        new_duration = last_task_duration_original - 10
        task_sequence = self.model.rowCount()
        row = self.model.rowCount() - 1  # Last row

        try:
            self.model.set_row_data(
                row, new_from=from_time, new_duration=new_duration, new_type='main',
                new_task_sequence=task_sequence
            )
        except Exception as e:
            logging.error(f"Exception type:{type(e)}  (Error Description:{e}")

        logging.debug(f"Last task updated.")

    def create_new_subtask(self):
        selection_model = self.table_view.selectionModel()

        selected_indexes = selection_model.selectedIndexes()
        if not selected_indexes:
            logging.debug(f"No row selected. Cannot insert subtask.")
            return

        selected_index = selected_indexes[0].row() if selected_indexes else self.model.rowCount() - 1
        replace_index = selected_index + 1
        sequence = self.model.get_row_data(selected_index, column_key='task_sequence')

        data_to_insert = {
            'id': None,
            'from_time': None,
            'to_time': None,
            'duration': None,
            'task_name': f'New Subtask at {replace_index}',
            'reminders': None,
            'type': 'subtask',
            'task_sequence': sequence + 1,
        }
        self.model.insert_new_row(replace_index, data_to_insert)

        self.update_sequences_after_insertion()

    def update_sequences_after_insertion(self):
        logging.debug(f"Updating sequences after insertion of new row.")

        selection_model = self.table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            logging.debug(f"No row selected. Cannot update sequences.")
            return

        selected_index = selected_indexes[0].row() if selected_indexes else self.model.rowCount() - 1

        for row in range(selected_index + 1, self.model.rowCount()):
            logging.debug(f"Updating sequence for row:{row}. Sequence:{row + 1}")
            self.model.set_row_data(row, new_task_sequence=row + 1)

    def remove_row_and_delete_data(self):
        logging.debug(f"Remove and Delete executing in TaskServices.")

        selection_model = self.table_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            logging.debug(f"No row selected. Nothing to delete.")
            return
        row_to_delete = selected_indexes[0].row()

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
                for row in range(row_to_delete, self.model.rowCount()):
                    logging.debug(f"Updating sequence for row:{row}. Sequence:{row + 1}")
                    self.model.set_row_data(row, new_task_sequence=row + 1)

    def save_task(self, task_data):
        pass
