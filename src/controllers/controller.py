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
            'New Task': self.new_maintask,
            'New QuickTask': self.new_quicktask,
            'Delete': self.delete_task,
            'Test': self.testing,
            'Reset': self.request_clearing_model,
            }

    def new_maintask(self):
        logging.debug("New Main Task requested in controller.")
        NewMainTaskAdder.start_new_maintask(self.model, self.table_view)

    def new_quicktask(self):
        logging.debug("New QuickTask requested in controller.")
        NewQuickTaskAdder.start_new_quicktask(self.model, self.table_view)

    def delete_task(self):
        logging.debug(f"'Delete Task' requested in controller.")
        DeleteTaskController.start_deleting_task(self.model, self.table_view)

    def save_all(self):
        logging.debug(f"Save data requested in controller.")
        self.model.save_to_database_file()

    def save_as(self):
        logging.debug(f"'Save As' requested in controller. Not implemented yet")

    def get_method_for_action(self, action):
        logging.debug(f"Getting method for action: {action}")
        action_method_map = self.create_action_method_map()
        method = action_method_map.get(action)
        if method:
            logging.debug(f"Method '{method.__name__}' found for action '{action}'.")
            return method
        else:
            logging.error(f"No method found for action '{action}'.")
            return None

    def sidebar_btn_clicked_signals(self, action):  # Called from MainWindow
        logging.debug(f"Catching Signal '{action}' from Sidebar.")
        method_to_call = self.get_method_for_action(action)
        method_to_call()

    def sidebar_btn_hovered_signals(self, action_name, bool_value):  # Called from MainWindow
        if action_name in self.create_action_method_map():
            if action_name == 'Test':
                self.testing()
                # self.table_view.table_state.update_btn_hover_state(bool_value)

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


