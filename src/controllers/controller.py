import logging

from controllers.processor import Processor
from resources.default import Columns


class Controller:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

        self.action_map = self._mapping()

        self.processor = Processor(model, table_view)

    def new_task(self):
        logging.debug("New Task requested in controller.")
        selected_row = self.processor.get_selected_row()

        if not self.processor.is_valid_task_row(selected_row):
            logging.debug(f"Selected row ({selected_row}) is invalid for a new task.")
            return

        # Backup the current state
        backup = self.model.backup_state()

        try:
            new_task_data = self.processor.calculate_new_task_data(selected_row)

            data_below_new = self.model.auto_time_updater.data_after_new_task(selected_row, new_task_data)

            if not (new_task_data and data_below_new):
                logging.error("New task data or data for row below new task is missing.")
                return

            # Perform insert new task
            insert_successful = self.model.tasker_model.insert_new_task(selected_row + 1, new_task_data)

            if insert_successful is not True:
                logging.error(f"Inserting new task wasn't successful")
                return

            # Perform update after new task operation
            self.model.auto_time_updater.update_after_new_task(data_below_new)

        except Exception as e:
            logging.error(f"Exception occurred: {type(e)}. Error: {e}")

            # Rollback to the previous state
            self.model.rollback_state(backup)
            return

        logging.debug("New task added and subsequent row updated successfully.")

    def new_quick_task(self):
        logging.debug("New QuickTask requested in controller.")
        selected_row = self.processor.get_selected_row()

        if not self.processor.is_valid_row(selected_row):
            logging.debug(f"Selected row is invalid. Selected row: {selected_row}")
            return

        # Backup the current state
        backup = self.model.backup_state()

        try:
            new_quick_task_data = self.processor.calculate_new_quick_task_data(selected_row)

            if not new_quick_task_data:
                logging.debug("New quick task data is missing.")
                return

            logging.debug(f"New quick task data calculated. Data: {new_quick_task_data}")

            # Perform the insert operation
            insert_successful = self.model.tasker_model.insert_new_task(selected_row + 1, new_quick_task_data)

            if insert_successful is not True:
                logging.error(f" Inserting QuickTask wasn't successful")
                return

            self.model.auto_time_updater.update_after_new_quick_task(selected_row, new_quick_task_data)

        except Exception as e:
            logging.error(f"Exception occurred: {type(e)}. Error: {e}")

            # Rollback to the previous state
            self.model.rollback_state(backup)
            return

        logging.debug("New quick task added successfully.")

    def delete_task(self):

        logging.debug(f"'Delete Task' requested in controller.")
        selected_row = self.processor.get_selected_row()

        if not self.processor.is_row_deletable(selected_row):
            logging.debug(f"Selected row ({selected_row}) is invalid for deletion.")

        # Backup the current state
        backup_before_delete = self.model.backup_state()

        try:
            # Get data for replaced row (row that will replace the to-be deleted row index)
            replaced_row_data = self.model.auto_time_updater.calculate_data_after_deletion(selected_row)

            if not replaced_row_data:
                logging.error(f"Replaced Row Data is missing.")
                return

            # Perform Delete operation
            delete_successful = self.model.tasker_model.delete_row_and_data(selected_row)

            if delete_successful is not True:
                logging.error(f"Error While Deleting {selected_row} row.")
                return

            if self.model.get_item_from_model(selected_row, Columns.Type.value) == 'QuickTask':

                # Update only positions
                self.model.auto_time_updater.update_positions(selected_row, "delete")
            else:
                # Update the start time and duration of the row below the deleted row
                self.model.auto_time_updater.update_after_delete_task(replaced_row_data)

            logging.debug(f"Row {selected_row} deleted from model and SQLite database.")

        except Exception as e:
            logging.error(f"Exception type: (type{e}). Error:{e}")
            self.model.rollback_state(backup_before_delete)
            return


    def save_all(self):
        logging.debug(f"Save data requested in controller.")
        self.model.save_to_database_file()

    def save_as(self):
        logging.debug(f"'Save As' requested in controller. Not implemented yet")

    def return_method_for_action(self, action):
        if action in self.action_map:
            logging.debug(f"Action '{action}' found in action_map.")
            try:
                method_to_call = self.action_map[action]
                logging.debug(f"Returning the method '{method_to_call.__name__}' for action '{action}'.")
                return method_to_call
            except Exception as e:
                logging.error(
                    f" Exception type:{type(e)} while calling action_map with action name {action} (Description:{e}"
                )
                return None

    def _mapping(self):
        action_map = {
            'Save': self.save_all,
            'Save As': self.save_as,
            'New Task': self.new_task,
            'New QuickTask': self.new_quick_task,
            'Delete': self.delete_task,
            'Testing': self.testing,
            'Reset': self.request_clearing_model,

        }  # Action:Method
        return action_map

    def signal_from_left_bar(self, action):
        logging.debug(f"Catching Signal '{action}' from LeftBar.")
        method_to_call = self.return_method_for_action(action)
        method_to_call()

    def button_hover_state(self, action_name, bool_value):
        selected_row = self.processor.get_selected_row()
        if action_name in self.action_map:
            if action_name == 'New Task':
                self.table_view.set_hover_state(selected_row, bool_value)

    def testing(self):
        logging.debug(f"Testing. Controller.")
        print(f"Testing. Controller.")

        self.calculate_total_duration()
        # self.model.default_state()

    def calculate_total_duration(self):
        total_duration = 0
        try:
            for row in range(self.model.rowCount()):
                # Check the type of the task
                task_type = self.model.get_item_from_model(row, Columns.Type.value)
                logging.debug(f"Task type at row:{row} is {task_type}.")

                # Skip rows where the type is 'QuickTask'
                if task_type == 'QuickTask':
                    continue

                # Get the duration value for the row
                duration = self.model.get_item_from_model(row, Columns.Duration.value)
                logging.debug(f"Row {row}, Duration: {duration}")

                # Assuming duration is an integer or can be converted to an integer.
                # You may need to adjust this part if duration is stored in a different format.
                try:
                    total_duration += int(duration)
                except ValueError:
                    logging.error(f"Warning: Invalid duration format at row {row}")
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")

        # At this point, total_duration holds the sum of all durations (excluding QuickTasks)
        logging.debug(f"Total Duration: {total_duration}")
        print(f"Total Duration: {total_duration}")

    def request_clearing_model(self):
        # Clear the model
        try:
            self.model.default_state()
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
