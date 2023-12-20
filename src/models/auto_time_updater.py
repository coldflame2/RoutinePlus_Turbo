import logging

from resources.default import Columns
from utils import helper_fn


class AutoTimeUpdater:
    """
    Class for updating and syncing all other values in the table model after a change in the UI.
    """

    def __init__(self, model):
        self.model = model

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
            self._update_after_end_time_change(row)
        elif changed_column == Columns.StartTime.value:
            self._update_after_start_time_change(row)
        else:
            logging.info(f"No updates required for changes in column '{changed_column}'.")

        return False

    # def _update_after_duration_change(self, row, new_duration):
    #     """
    #     Handles updates when the duration of a row changes.
    #     It updates the end time of the current row and
    #     the start time and duration of the next row.
    #
    #     :param row: Row index where the duration changed.
    #     :param new_duration: The new duration value for the row.
    #     """
    #     logging.debug(f"Preparing to update values for duration change at row {row}.")
    #
    #     try:
    #         # Prepare changes
    #         changes = self._data_after_duration_change(row, new_duration)
    #
    #         # Apply all changes
    #         for change_row, column, value in changes:
    #             self.model.set_item_in_model(change_row, column, value)
    #
    #     except Exception as e:
    #         logging.error(f"Error preparing updates after duration change at row {row}: {e}")
    #
    #         return False
    #
    #     logging.debug(f"Values successfully updated after duration change at row {row}.")
    #     return True

    def _data_after_duration_change(self, row, new_duration):
        """
        Prepares the changes needed for a duration update.

        :param row: Row index where the duration changed.
        :param new_duration: The new duration value for the row.
        :return: A list of changes to be applied.
        """
        changes = []

        try:
            # Get the start time of the current row
            start_time = self.model.get_item_from_model(row, Columns.StartTime.value)

            # Calculate new end time for the current row
            new_end_time = helper_fn.calculate_end_time(start_time, new_duration)
            changes.append((row, Columns.EndTime.value, new_end_time))
            logging.debug(f"End time for same row prepared. (new end time: {new_end_time})")

            # Prepare changes for the next row if it exists
            if row + 1 < self.model.rowCount():
                next_row_end_time = self.model.get_item_from_model(row + 1, Columns.EndTime.value)
                next_row_duration = helper_fn.calculate_duration(new_end_time, next_row_end_time)

                changes.append((row + 1, Columns.StartTime.value, new_end_time))
                changes.append((row + 1, Columns.Duration.value, next_row_duration))

                logging.debug(f"Start time and duration for next row prepared. (new start time: {new_end_time}, "
                              f"new duration: {next_row_duration})")

            logging.debug(f"Changes prepared after duration change at row {row}: {changes}")
            return changes

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")
            return None

    def _update_after_end_time_change(self, row):
        # Logic for updating when end time changes.
        pass  # Implement logic

    def _update_after_start_time_change(self, row):
        # Logic for updating when start time changes.
        pass  # Implement logic

    def calculate_values(self, row, duration=None, start_time=None, end_time=None):
        # Method for calculating values based on given parameters.
        pass  # Implement logic

    def _update_items(self):
        # Common method to update items in the model.
        pass  # Implement logic

    # Additional helper methods can be defined here as needed.
