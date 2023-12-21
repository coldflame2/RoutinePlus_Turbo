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
