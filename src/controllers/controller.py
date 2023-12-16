import logging

from src.controllers.task_services import TaskService


class Controller:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

        self.action_map = self.mapping()

        self.task_service = TaskService(model, table_view)

    def mapping(self):
        map = {
            'Save': self.process_saving_all,
            'Save As': self.save_as,
            'New Task': self.process_new_task,
            'Delete': self.process_delete_task,
            'Testing': self.testing,
            }  # Action:Method
        return map

    def signal_from_left_bar(self, action):
        logging.debug(f"Catching Signal '{action}' emitted from MainWindow (originated:LeftBar).")
        method_to_call = self._return_method_for_action(action)
        method_to_call()

    def process_new_task(self):
        logging.debug("New Task requested in controller.")
        self.task_service.create_new_task()

    def process_delete_task(self):
        logging.debug(f"'Delete Task' requested in controller.")
        self.task_service.remove_row_and_delete_data()

    def process_saving_all(self):
        logging.debug(f"Save data requested in controller.")
        self.model.save_to_database_file()

    def save_as(self):
        logging.debug(f"'Save As' requested in controller. Not implemented yet")

    def data_changed(self, value):
        logging.debug(f"data_changed. Value:'{value}'")
        self.table_view.update()

    def testing(self, action):
        logging.debug(f"Testing. Action:'{action}' in Controller.")
        print(f"Testing. Action:'{action}' in Controller.")

    def _return_method_for_action(self, action):
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


"""
The Controller accepts input and converts it to commands for the Model or View. It acts as an intermediary between the Model and the View.

The Controller sends commands to both the Model and the View. The Controller can call methods on the Model to update its state and on the View to change the presentation.

Responsibilities of the Controller include:

Input handling: Receiving input from the user and deciding what to do with it. 
Model interaction: Sending commands to the Model to update the Model's state (e.g., editing a document). 
View interaction: Sending commands to the View to change the View's presentation of the Model 
(e.g., scrolling through a document).

"""