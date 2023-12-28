import logging

from PyQt6.QtCore import Qt

from resources.default import Columns
from utils import helper_fn


class AutoTimeUpdater:
    """
    Class for updating and syncing all other values in the table model after a change in the UI.
    """

    def __init__(self, model):
        self.model = model
        self._recently_updated_rows = set()

    def get_data_to_update(self, row, changed_column, new_value):
        """
        Updates the values of the table model after a change in the UI.

        :param row: Row index to update.
        :param changed_column: Column that was changed.
        :param new_value: New value for the changed column.
        """
        logging.debug(f"AutoDataUpdater: Updating values after changes in '{changed_column}' of row {row}...")

        if changed_column == Columns.Duration.value:
            logging.debug(f" --AutoDataUpdater: Getting other values to update after duration change...")
            return self._data_after_duration_change(row, new_value)

        elif changed_column == Columns.EndTime.value:
            logging.debug(f" --AutoDataUpdater: Getting other values to update after end time change...")
            return self._data_after_endtime_change(row, new_value)

        elif changed_column == Columns.StartTime.value:
            logging.debug(f" --AutoDataUpdater: Getting other values to update after start time change...")
            return self._data_after_startime_change(row, new_value)

        else:
            logging.info(f"No updates required for changes in column '{changed_column}'.")
            return None

    def _data_after_duration_change(self, row, input_duration):
        """
        Prepares the changes needed for a duration update.

        :param row: Row index where the duration changed.
        :param input_duration: The new duration value for the row.
        :return: A list of changes to be applied.
        """
        changes = []

        # get start time
        # calculate end time
        # -- UPDATE end time
        # -- UPDATE next row start time
        # get next row end time
        # calculate next row duration
        # -- UPDATE next row duration

        try:
            logging.debug(f"Preparing the changes after duration changed. ")

            if row == self.model.rowCount() - 1:
                logging.debug(f"The changed row is the last one. Propagating changes to row above.")

                start_time = self.model.get_item_from_model(row, Columns.StartTime.value)
                new_start_time = helper_fn.calculate_start_time(start_time, input_duration)
                changes.append((row, Columns.StartTime.value, new_start_time))

                logging.debug(f"New start time of the last row prepared: {new_start_time}")

                # for row above
                changes.append((row - 1, Columns.EndTime.value, new_start_time))
                logging.debug(f"New End time of row above prepared (same as end time of this row: {new_start_time}.")

                duration_row_above = helper_fn.calculate_duration(start_time, new_start_time)
                changes.append((row - 1, Columns.Duration.value, duration_row_above))
                logging.debug(f"New Duration for row above prepared: {duration_row_above}")

                return changes

            else:
                logging.debug(f"The changed row is not the last one. Propagating changes to row below.")

                # Get the start time of the current row
                start_time = self.model.get_item_from_model(row, Columns.StartTime.value)
                # Calculate new end time for the current row
                new_end_time = helper_fn.calculate_end_time(start_time, input_duration)
                changes.append((row, Columns.EndTime.value, new_end_time))
                logging.debug(f"New End time for same row prepared. (new end time: {new_end_time})")

                # Prepare changes for the next row
                next_row_end_time = self.model.get_item_from_model(row + 1, Columns.EndTime.value)
                next_row_duration = helper_fn.calculate_duration(new_end_time, next_row_end_time)

                changes.append((row + 1, Columns.StartTime.value, new_end_time))
                changes.append((row + 1, Columns.Duration.value, next_row_duration))

                logging.debug(f"Start time and duration for next row prepared. (new start time: {new_end_time}, "
                              f"new duration: {next_row_duration})")
                return changes

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return False

    def _data_after_endtime_change(self, row, input_end_time):
        """
        Prepares the changes needed after a duration update.

        :param row: Row index where the duration changed.
        :param input_end_time: The new_end_time value for the row.

        :return: A list of changes to be applied.
        """
        changes = []

        # get start time
        # calculate duration
        # -- UPDATE duration
        # -- UPDATE next row start time
        # get next row end time
        # calculate next row duration
        # -- UPDATE next row duration

        try:
            # Get the start time of the current row
            start_time = self.model.get_item_from_model(row, Columns.StartTime.value)

            # Calculate new duration for the current row
            new_duration = helper_fn.calculate_duration(start_time, input_end_time)

            # append changes to list
            changes.append((row, Columns.Duration.value, new_duration))
            logging.debug(f"New Duration for same row prepared. (new duration: {new_duration})")

            # Prepare changes for the next row if it exists
            if row + 1 < self.model.rowCount():
                # Start time for next row is same as end time of current row
                next_row_start_time = input_end_time

                # Get next row end time from model
                next_row_end_time = self.model.get_item_from_model(row + 1, Columns.EndTime.value)

                # Calculate next row duration
                next_row_duration = helper_fn.calculate_duration(next_row_start_time, next_row_end_time)

                # append changes to list
                changes.append((row + 1, Columns.StartTime.value, next_row_start_time))
                changes.append((row + 1, Columns.Duration.value, next_row_duration))

            else:
                # There is no row below this one. Which shouldn't happen.
                # The end time of the last row is fixed at 12:00 AM
                logging.exception(f"End time of last row changed. This shouldn't happen. ")
                raise Exception(f"End time of last row changed. This shouldn't happen. ")
                pass

            logging.debug(f"Changes prepared after duration change at row {row}: {changes}")
            return changes

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

    def _data_after_startime_change(self, row, input_start_time):
        """
        Prepares the changes needed after StartTime update.
        Changes propagated to the previous row.

        :param row: Row index where the duration changed.
        :param input_start_time: The new_start_time value for the row.

        :return: A list of changes to be applied.
        """
        changes = []

        # get end time of same row
        # calculate duration of same row from end time - input start time
        # -- UPDATE duration of same row
        # -- UPDATE end time of previous row (same as input start time)
        # get previous row start time
        # calculate previous row duration
        # -- UPDATE previous row duration

        try:
            # get end time of same row
            end_time = self.model.get_item_from_model(row, Columns.EndTime.value)
            duration = helper_fn.calculate_duration(input_start_time, end_time)
            changes.append((row, Columns.Duration.value, duration))
            logging.debug(f"New Duration for same row prepared. (new duration: {duration})")

            # Prepare changes for the previous row if it exists
            if row - 1 >= 0:
                # Get previous row start time from model
                prev_row_start_time = self.model.get_item_from_model(row - 1, Columns.StartTime.value)

                # Calculate previous row duration
                prev_row_duration = helper_fn.calculate_duration(prev_row_start_time, input_start_time)

                # append changes to list
                changes.append((row - 1, Columns.Duration.value, prev_row_duration))
                changes.append((row - 1, Columns.EndTime.value, input_start_time))

            else:
                # There is no row above this one. Which shouldn't happen.
                # The end time of the last row is fixed at 12:00 AM
                logging.exception(f"Start time of first row changed. This shouldn't happen. ")
                raise Exception(f"Start time of first row changed. This shouldn't happen. ")
                pass

            logging.debug(f"Changes prepared after duration change at row {row}: {changes}")
            return changes


        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

    def update_positions(self, first_row_to_update, operation):
        """
        Update sequences of rows below the affected row index.

        Args:
        affected_row (int): The index of the row where the operation (addition or deletion) occurred.
        operation (str): Type of operation, either 'add' or 'delete'.
        """
        logging.debug(f"Updating sequences of rows below row index: {first_row_to_update} after {operation} operation.")

        # Determine the operation type: addition or deletion
        position_change = 1 if operation == 'add' else -1

        for row in range(first_row_to_update, self.model.rowCount()):
            col_key = Columns.Position.value
            old_position = self.model.get_item_from_model(row, col_key)
            new_position = old_position + position_change

            try:
                update_successful = self.model.set_item_in_model(row, col_key, new_position)
                if not update_successful:
                    logging.error(f"Updating sequence for row: {row} failed.")
                    return False

            except Exception as e:
                logging.error(f"Exception type: {type(e)}  (Error Description: {e}")
                return

        return True

    def data_after_new_task(self, clicked_row, data_for_new_row):
        """
        Updates StartTime, Duration, and Positions of the row below the new row.

        :param clicked_row:
        This is the row index of clicked/selected row. This is also the data row.
        New row index is clicked_row + 1.
        And the row to auto-update is clicked_row + 1 + 1.

        IMPORTANT: New Row is not yet inserted. The indices are hypothetical.

        :param data_for_new_row:
        :return:
        """
        changes = []

        logging.debug(f"Updating next row's start time and duration.")

        main_row_below_new = self.find_main_task_below(clicked_row)

        try:
            start_time_row_below_new = data_for_new_row[Columns.EndTime.value]  # Same as end time of the new row
            changes.append((main_row_below_new, Columns.StartTime.value, start_time_row_below_new))

            end_time_row_below_new = self.model.get_item_from_model(clicked_row + 1, Columns.EndTime.value)
            duration_row_below_new = helper_fn.calculate_duration(start_time_row_below_new, end_time_row_below_new)

            changes.append((main_row_below_new, Columns.Duration.value, duration_row_below_new))

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

        logging.debug(f"Changes prepared for row below new: {changes}")
        return changes

    def find_main_task_below(self, initial_clicked_row):  # For updating next task after new task
        """
        Find the main task below with the selected row.

        IMPORTANT: To check row types, index in current state is checked. But to update, we add 1 to the index.
        This is because the new row is not yet inserted. And the changes would be for the row after the new row has been inserted.

        :param initial_clicked_row: The row index that the user initially clicked.
        :return: The row index of the main task found, or None if no main task is found.
        """
        logging.debug("Finding main task below the selected task for auto-update.")

        current_row_below_new = initial_clicked_row+1  # after new row, it will be clicked_row + 1 + 1
        if self.model.rowCount() - 1 == current_row_below_new:
            logging.debug(f"Row below new row would be last row. Returning last row for "
                          f"auto-updating.")
            return current_row_below_new + 1

        while current_row_below_new < self.model.rowCount():
            if self.model.get_item_from_model(current_row_below_new, Columns.Type.value) == 'main':
                logging.debug(f"Main task found at row index: {current_row_below_new + 1}")
                return current_row_below_new + 1
            else:
                logging.debug(f" Row {current_row_below_new+1} is QuickTask. Checking next row "
                              f"type.")
                current_row_below_new += 1

        logging.error("No main task found below the selected row for auto-updating.")
        return None


    def update_after_new_quick_task(self, clicked_row, data_to_insert):
        """
        Updates Positions of the row below the new row.

        :param clicked_row:
        This is the row index of clicked/selected row. This is also the data row.
        New row index is clicked_row + 1.
        And the row to auto-update is clicked_row + 1 + 1.

        :param data_to_insert:
        :return:
        """

        logging.debug(f"Updating next row's start time and duration.")

        self.update_positions(clicked_row + 1 + 1, 'add')

        logging.debug(f"New QuickTask inserted, positions updated.")

    def calculate_data_after_deletion(self, clicked_row):
        """
        Get Data for the replaced row (same index as clicked/to-be deleted row).
        Important: the row hasn't been deleted yet.

        Get EndTime of row above. That will be StartTime of Replaced/clicked row.
        Get EndTime of row below, that will be EndTime of replaced/clicked row.
        Calculate duration for replaced row.
        """
        logging.debug(f"Updating the replaced row's start time and duration.")
        changes = []
        task_type_row_above = self.model.get_item_from_model(clicked_row - 1, Columns.Type.value)
        task_type = self.model.get_item_from_model(clicked_row, Columns.Type.value)
        task_type_row_below = self.model.get_item_from_model(clicked_row + 1, Columns.Type.value)

        if task_type == 'QuickTask' and task_type_row_below == 'main' and task_type_row_above == 'main':
            logging.debug(f"Clicked row is QuickTask and row below is 'main.' Updating next row's start time and duration.")
            # Get the EndTime of 'main' row above clicked row
            end_time_above = self.model.get_item_from_model(clicked_row - 1, Columns.EndTime.value)

            # Set the StartTime of the clicked/replaced row (Because the row hasn't been deleted yet) to the
            # EndTime of the 'main' row
            changes.append((clicked_row, Columns.StartTime.value, end_time_above))

            # Get the EndTime of the 'main' row below the clicked row
            end_time_below = self.model.get_item_from_model(clicked_row + 1, Columns.EndTime.value)

            # Calculate the duration of the clicked row
            duration_replaced_row = helper_fn.calculate_duration(end_time_above, end_time_below)
            changes.append((clicked_row, Columns.Duration.value, duration_replaced_row))

            logging.debug(f"Changes prepared for the replaced row after deletion: {changes}")
            return changes


        try:
            end_time_above = self.model.get_item_from_model(clicked_row - 1, Columns.EndTime.value)
            end_time_below = self.model.get_item_from_model(clicked_row + 1, Columns.EndTime.value)
            duration_replaced_row = helper_fn.calculate_duration(end_time_above, end_time_below)
            changes.append((clicked_row, Columns.StartTime.value, end_time_above))
            changes.append((clicked_row, Columns.Duration.value, duration_replaced_row))
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

        logging.debug(f"Changes prepared for the replaced row after deletion: {changes}")
        return changes

    def update_after_new_task(self, data_below_new):
        # Update only Start time and Duration of row below the newly added row
        try:
            logging.debug("Updating StartTime and Duration of row below the new task row.")

            if data_below_new:
                # Update the row below with the new data
                for row, col, val in data_below_new:
                    self.model.set_item_in_model(row, col, val)

                # Update positions of all the rows below the new row
                row_below_new_row = data_below_new[0][0]
                self.update_positions(row_below_new_row, 'add')

            logging.debug("Data Updated after adding new task.")

        except Exception as e:
            logging.error(f"Exception type: {type(e)} while trying to update after new task. Error: {e}")
            raise e

    def update_after_delete_task(self, replaced_row_data):
        logging.debug(f"Updating replaced row data after row deletion.")
        try:
            if replaced_row_data:
                for row, col, val in replaced_row_data:
                    self.model.set_item_in_model(row, col, val)

                # Update positions of all the rows below starting from replaced row index
                replaced_row_index = replaced_row_data[0][0]

                self.update_positions(replaced_row_index, 'delete')

            logging.debug(f"Data of replaced row updated after deleting row.")

        except Exception as e:
            logging.error(f"Exception type: {type(e)} while trying to update after new task. Error: {e}")
            raise e
