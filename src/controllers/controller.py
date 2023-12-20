import logging

from controllers.processor import Processor


class Controller:
    def __init__(self, model, table_view):
        self.model = model
        self.table_view = table_view

        self.action_map = self._mapping()

        self.processor = Processor(model, table_view)

    def new_task(self):
        logging.debug("New Task requested in controller.")
        selected_row = self.processor.get_selected_row()
        if self.processor.is_valid_row(selected_row):
            if self.processor.is_valid_task_row(selected_row):
                logging.debug(f"Selected row ({selected_row}) is valid.")

                try:
                    new_task_data = self.processor.calculate_new_task_data(selected_row)
                except Exception as e:
                    logging.error(f"Error when calculating new task data. Exception type:{type(e)} Error:{e}")
                    return

                logging.debug(f"New task data calculated. Data:{new_task_data}")

                if new_task_data:
                    logging.debug(f"New task data calculated. Data:{new_task_data}")
                    self.insert_and_update_positions(selected_row, new_task_data)

    def new_quick_task(self):
        logging.debug("New QuickTask requested in controller.")
        selected_row = self.processor.get_selected_row()
        if self.processor.is_valid_row(selected_row):
            logging.debug(f"Selected row is valid. Selected row:{selected_row}")

            try:
                new_quick_task_data = self.processor.calculate_new_quick_task_data(selected_row)
            except Exception as e:
                logging.error(f"Error when processing new QuickTask data. Exception type: {type(e)}. Error"
                              f":{e}")
                return

            if new_quick_task_data:
                logging.debug(f"New quick task data calculated. Data:{new_quick_task_data}")
                self.insert_and_update_positions(selected_row, new_quick_task_data)

    def insert_and_update_positions(self, selected_row, data_to_insert):
        # Insert new row in the model with the data
        try:
            self.model.tasker_model.insert_new_task(selected_row + 1, data_to_insert)
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")

        # Update the positions of the rows below the new row
        try:
            self.processor.update_positions(selected_row + 1 + 1)  # +1 for the new row, +1 for the row below
        except Exception as e:
            logging.error(f"Exception type: (type{e}). Error:{e}")

    def delete_task(self):
        logging.debug(f"'Delete Task' requested in controller.")
        selected_row = self.processor.get_selected_row()
        if self.processor.is_row_deletable(selected_row):
            logging.debug(f"Selected row is valid. Selected row:{selected_row}")

            try:
                self.model.tasker_model.delete_row_and_data(selected_row)
            except Exception as e:
                logging.error(f"Exception type: (type{e}). Error:{e}")

            self.processor.update_positions(selected_row)
    def save_all(self):
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
            }  # Action:Method
        return action_map

    def signal_from_left_bar(self, action):
        logging.debug(f"Catching Signal '{action}' emitted from MainWindow (originated:LeftBar).")
        method_to_call = self.return_method_for_action(action)
        method_to_call()
