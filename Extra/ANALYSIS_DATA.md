## Database Storage (AppData class):

- The from_time and to_time columns are stored in the SQLite database in the daily_routine table as text in an ISO8601 string format, which is the default way SQLite handles datetime values.

## Fetching and Conversion to datetime (AppData.get_all_entries method):

- When entries are retrieved from the database, the get_all_entries method in the AppData class fetches them as text.
- Before returning, get_all_entries calls helper_fn.string_to_datetime for each from_time and to_time entry to convert the string format into Python datetime objects. These conversions are stored in the existing_data_formatted list, which contains dictionaries with keys corresponding to column names and values being the data, including the now converted datetime objects for from_time and to_time.

## Data Handling in TableModel class:

- The TableModel class maintains a list of dictionaries called _data. Each dictionary corresponds to a row from the database, with keys as column names and values as the corresponding data.
- The data method of TableModel is responsible for providing this data to the view component. When the view requests the data for display (Qt.ItemDataRole.DisplayRole), the data method checks if the requested column is from_time or to_time.
- If so, it uses the strftime method to convert the datetime object back into a string formatted for display (e.g., "01:23 PM") and returns this string to the view.

## Editing and Saving Data (TableModel.setData method):

- When a user edits a time value in the view, the setData method in TableModel is called with the new value as a string.
- If the edited value is for from_time or to_time, setData uses the parse_datetime method to convert the string back into a datetime object, which can then be stored in the _data list.
- When saving changes to the database, the save_to_db_in_model method of TableModel is called, which in turn calls the save_all method of AppData. This method will save the datetime object as a string back into the SQLite database, converting it to the ISO8601 string format if necessary.

## Database Update (AppData.save_all method):

- The save_all method in the AppData class is used to update the SQLite database with any changes.
- This method takes the list of dictionaries with potentially updated data from TableModel and updates (or inserts) the records in the database. The datetime objects for from_time and to_time would be stored as strings in the ISO8601 format in the database.

## Summary of the Data Flow for from_time and to_time:
- SQLite Database: Stored as text in ISO8601 format (but columns from and to are defined as datetime and duration as integer)

- Fetching from Database (AppData.get_all_entries): Text (ISO string format for date) converted to datetime (HH:MM:SS, Y-M-D) and integer objects. If default tasks, they are already in desired data types.

- In TableModel: Data fetched in desired data types and stored in _data.

- in 'data' method, data is converted to strings of desired format for display when requested by the view. (START and END times are converted to simple HH:MM am/pm format, and Duration integer is converted to string and added 'minutes' as text.)

- Editing in View (TableModel.setData): String input in START/END of format HH:MM am/pm parsed back to datetime and integer data types.

- Saving to Database (AppData.save_all): model passes self._data that already contains desired data types. Save_all inserts to table or updates (in case existing ID). When the data is saved, SQLite3 automatically saves them in text. 