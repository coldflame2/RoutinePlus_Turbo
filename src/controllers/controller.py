import logging
from datetime import timedelta

from PyQt6.QtCore import QModelIndex, QTimer

from src.utils import helper_fn


class Controller:
    def __init__(self, model, table_view):
        logging.debug(f"Constructor class constructor starting.")

        self.model = model
        self.table_view = table_view

        logging.debug(f"Controller class constructor successfully initialized.")

    def signal_from_left_bar(self, action):
        logging.debug(f"Catching Signal '{action}' emitted from MainFrame (originated:LeftBar).")
        method_to_call = self.action_method_mapping(action)
        method_to_call()

    def action_method_mapping(self, action):
        self.action_map = {
            'Save': self.model.call_save_all,
            'Save As': self.save_as,
            'New Task': self.new_task,
            }  # Action:Method

        if action in self.action_map:
            logging.debug(f"Action '{action}' found in action_map.")
            try:
                method_to_call = self.action_map[action]
                logging.debug(f"Returning the method/value of key/action: {method_to_call.__name__}")
                return method_to_call
            except Exception as e:
                logging.error(
                    f" Exception type:{type(e)} while calling action_map with action name {action} (Description:{e}"
                    )
                return None

    def new_task(self):
        logging.debug("New Task requested in controller.")
        total_rows = self.model.get_total_rows()

        last_task_index = total_rows - 1  # Same as index to insert
        index_to_get_data = last_task_index - 1  # to get data

        last_task_duration_original = self.model.get_entry_from_row(last_task_index, 'duration')

        logging.debug(f"total rows:'{total_rows}'")
        logging.debug(f"last task index:'{last_task_index}'")

        logging.debug(f"last task duration original:'{last_task_duration_original}'")

        data_to_set_new_row = self.get_data_to_insert(index_to_get_data)
        logging.debug(f"data to set in new row:'{data_to_set_new_row}'")

        self.model.insert_new_row(last_task_index, data_to_set_new_row)  # Insert at the end

        logging.debug(f"This is after new row has been inserted.")

        # Prepare data for updating the last row
        to_time_above = data_to_set_new_row.get('to_time')  # New from_time of last task
        last_task_new_duration = last_task_duration_original - 10

        logging.debug(f"to_time_above (same as 'from' of newly inserted row:'{to_time_above}'")
        logging.debug(f"new duration for last task (10 minutes less than original):'{last_task_new_duration}'")

        self.model.update_value(last_task_index + 1, to_time_above, last_task_new_duration)

    def get_data_to_insert(self, index):
        try:
            max_id = self.model.get_max_id()
            logging.debug(f"max_id({max_id}) retrieved from model.'")

            if index >= 0:
                to_time_row_above = self.model.get_entry_from_row(index, 'to_time')
                logging.debug(f"to_time_row_above:'{to_time_row_above}' retrieved from model.")
            else:
                logging.error(f"Index is less than zero.")
                return

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when getting max_id, row index, and to_time from model. (Error:{e}")
            return

        try:
            to_time = to_time_row_above + timedelta(minutes=10) if to_time_row_above else None
            reminder = to_time_row_above - timedelta(minutes=5)
            logging.debug(f"to_time for new row:'{to_time}' and reminder:{reminder} calculated.")

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when calculating new to_time and reminder. (Error Description:{e}")
            return

        # New task data
        data_to_insert = {
            'id': max_id,
            'from_time': to_time_row_above,
            'to_time': to_time,
            'duration': 10,
            'task_name': 'New Task',
            'reminders': reminder
            }

        return data_to_insert

    def save_as(self):
        logging.debug(f"'Save As' requested in controller. Not implemented yet")

    def data_changed(self, value):
        logging.debug(f"data_changed. Value:'{value}'")
        self.table_view.update()

    def testing(self, action):
        logging.debug(f"Testing. Action:'{action}' in Controller.")
        print(f"Testing. Action:'{action}' in Controller.")


"""
The Controller accepts input and converts it to commands for the Model or View. It acts as an intermediary between the Model and the View.

The Controller sends commands to both the Model and the View. The Controller can call methods on the Model to update its state and on the View to change the presentation.

Responsibilities of the Controller include:

Input handling: Receiving input from the user and deciding what to do with it. 
Model interaction: Sending commands to the Model to update the Model's state (e.g., editing a document). 
View interaction: Sending commands to the View to change the View's presentation of the Model 
(e.g., scrolling through a document).

"""