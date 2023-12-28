Flow of events on new row addition and deletion:
1. Left bar triggers a signal after user interaction.
2. Signal is intercepted by MainWindow, which emits/forwards it, and is then intercepted again by Controller.
3. Controller calls Processor functions to process the data (and to check validity of selected row, etc.).
4. Processor returns the processed data to Controller.
5. Controller calls TaskerModel methods with the processed data to update the table.
6. It also calls AutoTimeUpdater to update the table after tasks are added or deleted.

Flow of events when value edited in table:
1. Editing triggers setData() in TableModel.
2. TableModel calls TaskerModel methods to validate and format the new edited value.
3. TableModel retrieves the returned value and passes on to the AutoTimeUpdater.
4. AutoTimeUpdater prepares the new data for updating the table and returns back to the model.
5. TableModel finally updates both the edited cell and other interdependent cells.

Flow of events when new task is added:
1. Left bar triggers a signal after user interaction, caught by MainWindow and Controller.
2. Controller calls is_valid_task_row() from Processor to check if the selected row is valid for adding a new task.
4. If valid, it calls calculate_new_task_data() from Processor to calculate the data for the new task.
5.