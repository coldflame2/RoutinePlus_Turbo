import logging

from controllers.TaskControllers import DeleteTaskController
from controllers.TaskControllers import NewQuickTaskAdder
from controllers.TaskControllers import NewMainTaskAdder
from resources.default import Columns


class Controller:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

    def create_action_method_map(self):
        return {
            'Save': self.save_all,
            'Save As': self.save_as,
            'New MainTask': self.process_new_maintask,
            'New QuickTask': self.process_new_quicktask,
            'Delete': self.process_delete_task,
            'Test': self.testing,
            'Reset': self.request_clearing_model,
            }

    def process_new_maintask(self):
        """
        Flow:
        MainTaskAdder > start_new_maintask > validate selected row >
        _data_retrieval
        :return:
        """
        logging.debug("Processing new MainTask from controller.")
        NewMainTaskAdder.initiate_maintask_addition(self.model, self.table_view)

    def process_new_quicktask(self):
        logging.debug("Processing new QuickTask from controller.")
        NewQuickTaskAdder.start_new_quicktask(self.model, self.table_view)

    def process_delete_task(self):
        logging.debug(f"Processing delete task from controller.")
        DeleteTaskController.start_deleting_task(self.model, self.table_view)

    def save_all(self):
        logging.debug(f"Save data requested in controller.")
        try:
            self.model.save_to_database_file()
        except Exception as e:
            logging.error(f"Exception when saving to database. Type: {type(e)}. Error:{e}")

        try:
            self.model.app_data.commit_sqlite_all()
        except Exception as e:
            logging.error(f"Exception when committing to database. Type: {type(e)}. Error:{e}")

        self.table_view.reset_recent_row_ids_dict()

    def save_as(self):
        logging.debug(f"'Save As' requested in controller. Not implemented yet")

    def sidebar_btn_clicked_signals(self, action):  # Called from MainWindow
        logging.debug(f"Catching Signals from Sidebar. (Action:'{action}')")
        method_to_call = self._get_method_for_action(action)
        method_to_call()

    def sidebar_btn_hovered_signals(self, action_name, bool_value):  # Called from MainWindow
        if action_name in self.create_action_method_map():
            if action_name == 'Test':
                self.testing()
                # self.table_view.table_state.update_btn_hover_state(bool_value)

    def _get_method_for_action(self, action):
        action_method_map = self.create_action_method_map()
        method = action_method_map.get(action)
        if method:
            logging.debug(f"Method '{method.__name__}' found for action '{action}'.")
            return method
        else:
            logging.error(f"No method found for action '{action}'.")
            return None

    def testing(self):
        logging.debug(f"Controller: Testing.")
        print(f"Controller: Testing.")

        self.calculate_total_duration()

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
        try:
            self.model.default_state()
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")


