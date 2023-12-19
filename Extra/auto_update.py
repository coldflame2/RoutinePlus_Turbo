import logging
from datetime import timedelta


class TimeCalculator:

    def calculate_data(self, end_time_row_above, position_row_above):
        logging.debug(f"Calculating data to insert in new row.")

        end_time = end_time_row_above + timedelta(minutes=10) if end_time_row_above else None
        reminder = end_time_row_above - timedelta(minutes=5)

        data_to_insert = {
            'id': None,
            'start_time': end_time_row_above,
            'end_time': end_time,
            'duration': 10,
            'task_name': 'New Task',
            'reminders': reminder,
            'type': 'main',
            'position': position_row_above + 1,
            }

        return data_to_insert



    def handle_task_name_input(self, index, row, value, role):
        task_col_key = 'task_name'
        original_task_name = self._data[row][task_col_key]

        if original_task_name == value:
            logging.debug(f"Same value in 'Task' column. Returning without any changes.")
            return False

        else:
            return self.set_task_name_and_notify(index, row, value, role)

    def handle_duration_input(self, index, row, value, role):
        logging.debug(f"Change in duration")
        focus_widget = QApplication.focusWidget()

        original_duration = self._data[row]['duration']

        if value == "":
            logging.debug(f"Input value is empty:'{value}'")
            return False

        try:
            input_duration_int = helper_fn.strip_text(value)

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when striping input duration string (Error Description:{e}")
            return False

        if input_duration_int == 0 or input_duration_int < 0:
            QMessageBox.warning(focus_widget, "Can't be zero.", "The task has to be at least of one minute duration.")
            return False

        if original_duration != input_duration_int:  # If the input value is not equal to original
            if row == (len(self._data) - 1):
                logging.debug(f"Row edited is the last row. Index:'{row}'. Setting 'Duration' and updating 'end_time'.")
                return self.on_duration_input_same_row(index, row, input_duration_int, role)

            else:
                logging.debug(f"Next row exists. Calling methods to update its values.")
                return self.on_duration_input_next_row(index, row, input_duration_int, role)

        else:
            logging.debug(f"Same value in 'Duration'. Returning without any changes.")
            return False

    def on_duration_input_same_row(self, index, row, input_duration_int, role):

        try:
            original_from = self._data[row]['start_time']
            new_to = original_from + timedelta(minutes=input_duration_int)

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when updating 'from' after setting new duration (Error Description:{e}")
            return False

        try:
            self._data[row]['duration'] = input_duration_int  # Set the value to new_duration integer
            self._data[row]['end_time'] = new_to  # Set the 'To' value to new calculated one

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when setting input duration and calculated new 'end_time.' (Error Description:{e}")
            return False

        logging.debug(f"setData in 'duration'({input_duration_int} and 'end_time' {new_to}. Emitting dataChanged signals now.")
        self.dataChanged.emit(index, index, [role])  # Emit for 'start_time'

        end_time_index = self.createIndex(row, 1)  # end_time column index = 1
        self.dataChanged.emit(end_time_index, end_time_index, [role])  # Emit for 'end_time'

        return True

    def on_duration_input_next_row(self, index, row, input_duration_int, role):

        focus_widget = QApplication.focusWidget()

        next_row = row + 1
        original_from_next_row = self._data[next_row]['start_time']
        original_to_next_row = self._data[next_row]['end_time']
        original_duration_next_row = self._data[next_row]['duration']

        logging.debug(
            f"Next row values."
            f"start:'{original_from_next_row}'. To:{original_to_next_row}. Duration:{original_duration_next_row}"
            )

        try:
            original_duration = self._data[row]['duration']
            max_possible_duration = original_duration + original_duration_next_row

            if input_duration_int < max_possible_duration:
                # Duration same row

                # set
                logging.debug(f"Setting input duration ({input_duration_int}) in the same row.")
                self._data[row]['duration'] = input_duration_int  # Set the value to new_duration integer

                # Emit
                logging.debug(f"Emitting dataChanged for Duration in the same row.")
                self.dataChanged.emit(index, index, [role])

                # "To Time" same row

                # set
                logging.debug(f"Setting new 'end_time' in the same row.")
                original_from_same_row = self._data[row]['start_time']
                new_to_same_row = original_from_same_row + timedelta(minutes=input_duration_int)
                self._data[row]['end_time'] = new_to_same_row
                logging.debug(f"new 'end_time' same row:{new_to_same_row} set.")

                # Emit
                end_time_same_row_index = self.createIndex(row, 1)
                self.dataChanged.emit(end_time_same_row_index, end_time_same_row_index, [role])

                # "From Time" next row

                # set
                logging.debug(f"Setting new 'start_time' in the next row.")
                self._data[next_row]['start_time'] = new_to_same_row  # set same as 'end_time' of row above

                # Emit
                logging.debug(f"Emitting dataChanged for 'start_time' in the next row.")
                new_from_next_row_index = self.createIndex(row, 0)
                self.dataChanged.emit(new_from_next_row_index, new_from_next_row_index, [role])

                # 'Duration' next row

                # set
                logging.debug(f"Setting new 'duration' in the next row.")
                original_to_next_row = self._data[next_row]['end_time']
                new_time_diff_next_row = (original_to_next_row - new_to_same_row)  # This is in timedelta
                self._data[next_row]['duration'] = int(new_time_diff_next_row.total_seconds() / 60)

                # Emit
                logging.debug(f"Emitting dataChanged for 'duration' in the next row.")
                duration_next_row_index = self.createIndex(next_row, 2)  # duration column index = 2
                self.dataChanged.emit(duration_next_row_index, duration_next_row_index, [role])  # Emit for 'duration'

                return True

            else:
                logging.warning(f"Duration cannot be more than {max_possible_duration}")
                QMessageBox.warning(
                    focus_widget, f"Invalid. Input less than {max_possible_duration}",
                    "The task below has to be at least of one minute duration."
                    f"Therefore the duration for this task cannot be more than {max_possible_duration}."
                    )
                return False

        # Value isn't an integer
        except ValueError:
            QMessageBox.warning(focus_widget, "Invalid Duration", "Please input a valid number for duration.")
            logging.error(f"Input duration value isn't a valid integer. Input: {input_duration_int}")
            return False

        except Exception as e:
            QMessageBox.warning(focus_widget, "Unknown Exception", "Please restart.")
            logging.error(f"Exception type:{type(e)} after input in duration. Input value: {input_duration_int}. Error:{e}")
            return False

    def set_and_update_fields_and_notify(self, value, row, column_key):

        if column_key == 'duration':  # String input to Integer
            logging.debug(f"Change in duration")
            original_duration = self._data[row]['duration']

            try:
                input_duration_int = helper_fn.strip_text(value)

            except Exception as e:
                logging.error(f"Exception type:{type(e)} when striping input duration string (Error Description:{e}")
                return False

            if original_duration != input_duration_int:  # If the input value is not equal to original
                duration_input_handled = self.handle_duration_input(row, input_duration_int)
                return duration_input_handled

            else:
                logging.debug(f"Same value in 'Duration'. Returning without any changes.")
                return False

        if column_key == 'start_time':
            logging.debug(f"Change detected in 'start_time'. Input value:'{value}'")
            return self.handle_from_input(row, value)

        if column_key == 'end_time':
            logging.debug(f"Change detected in 'end_time'. Input value:'{value}'")
            return self.handle_to_input(row, value)

    def handle_from_input(self, row, user_input_value):
        focus_widget = QApplication.focusWidget()

        if row == 0:
            logging.debug(f"Cannot change the starting time of the day.")
            QMessageBox.warning(
                focus_widget, "START time of the first task cannot be changed.",
                "Cannot change the START time of the first task."
                "First task always begins from midnight. "
                )
            return False

        try:
            input_from_dt = self.parse_datetime(user_input_value)
            self._data[row]['start_time'] = input_from_dt

            return True

        # Value isn't an integer
        except ValueError:
            QMessageBox.warning(focus_widget, "Invalid 'START' time.", "Please input a valid START time for the task.")
            logging.error(f"Input value isn't a valid time in format: 09:00 am/pm. Input: {user_input_value}")
            return False

        except Exception as e:
            QMessageBox.warning(focus_widget, "Invalid Input", "Please input a valid START time for the task.")
            logging.error(f"Exception type:{type(e)} after input in duration. Input value: {user_input_value}. Error:{e}")
            return False

    def handle_to_input(self, row, user_input_value):
        focus_widget = QApplication.focusWidget()

        try:
            input_end_time = self.parse_datetime(user_input_value)
            self._data[row]['end_time'] = input_end_time
            return True

        # Value isn't an integer
        except ValueError:
            QMessageBox.warning(focus_widget, "Invalid 'END' time.", "Please input a valid END time for the task.")
            logging.error(f"Input value isn't a valid time in format: 09:00 am/pm. Input: {user_input_value}")
            return False

        except Exception as e:
            QMessageBox.warning(focus_widget, "Invalid Input", "Please input a valid END time for the task.")
            logging.error(f"Exception type:{type(e)} after input in duration. Input value: {user_input_value}. Error:{e}")
            return False

    def set_task_name_and_notify(self, index, row, value, role):
        column_key = 'task_name'

        try:
            self._data[row][column_key] = value  # Task Name Set
            self.dataChanged.emit(index, index, [role])
            logging.debug(f"Emitting dataChanged signal after updating task_name at row:{row}.")
            return True

        except Exception as e:
            logging.error(f"Exception type:{type(e)} when setting task name. Error: {e}")
            return False

    def parse_datetime(self, value):
        """Parse datetime fields from string."""
        try:
            format_str = "%I:%M %p, %Y-%m-%d"
            return datetime.strptime(f'{value}, 2023-01-01', format_str)

        except ValueError:
            QMessageBox.warning(self.parent_widget, "Invalid", "Please input a valid time in the format: 'HH:MM am/pm'.")
            logging.error(f"Input value isn't a valid integer. Input: {value}")
            return None
        except Exception as e:
            logging.error(f"Exception when parsing datetime in setData: {type(e)} - {e}")
            return None