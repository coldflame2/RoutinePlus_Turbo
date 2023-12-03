import logging


class Controller:
    def __init__(self, model, table_view):
        logging.debug(f"Constructor class constructor starting.")

        self.model = model
        self.table_view = table_view
        self.model.dataChanged.connect(self.testing)

        logging.debug(f"Controller class constructor successfully initialized.")

    def signal_from_left_bar(self, action):
        logging.debug(f"Signal '{action}' from MainFrame (originated:LeftBar) caught.")
        method_to_call = self.action_to_method(action)
        method_to_call()

    def action_to_method(self, action):
        self.action_map = {
            'Save': self.model.save_to_db_in_model,
            'Save As': self.save_table_data_as,
            'New Task': self.create_new_task,
            }

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

    def testing(self):
        print(f" 'model': '{self.model}'")

    def handle_action(self, action_name):
        logging.debug(f" 'Handling Action in Controller': '{action_name}'")
        try:
            if action_name in self.action_map:
                try:
                    self.action_map[action_name]()
                except Exception as e:
                    logging.error(
                        f" Exception type:{type(e)} while calling action_map with action name (Error Description:{e}"
                        )

        except Exception as e:
            logging.error(f" Exception type:{type(e)} while handling action in data controller (Error Description:{e}")

    def save_table_data_as(self):
        # Implement "Save As" logic here
        print("Saving table data as a new file...")

    def create_new_task(self):
        # Implement task creation logic here
        print("Creating new task...")


"""The Controller accepts input and converts it to commands for the Model or View. It acts as an intermediary between 
the Model and the View.

The Controller sends commands to both the Model and the View. The Controller can call methods on the Model to update 
its state and on the View to change the presentation.

Responsibilities of the Controller include:

Input handling: Receiving input from the user and deciding what to do with it. 
Model interaction: Sending commands to the Model to update the Model's state (e.g., editing a document). 
View interaction: Sending commands to the View to change the View's presentation of the Model 
(e.g., scrolling through a document).

"""