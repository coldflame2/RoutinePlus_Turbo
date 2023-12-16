Building GUI app using PyQt6 bindings and the architecture is MVC. It's called Routine Plus turbo. 
It shows a table, where each row represents a task with start, end, duration, name, and reminder value. 
The first cell of first row represents midnight and "from" or "end" cell of the last row represents end of the day (again midnight).

I have TableView class (QTableView) for view and TableModel(QAbstractItemModel) for model. Also, AppData for SQLite3 database.

My question is, 

This is the structure of the app explain in the order of execution.

```main() creates instance of model and view.
    |
    |__ and controller and passes model and view as arguments.

main() creates instance of MainWindow (passes view and controller)

MainWindow creates the QMainWindow and adds the view and other widgets to the interface. It also has 'controller.'

Then there's TableView. It creates the QTableView (the model is set to the view in main()). There's almost zero interaction with any other module other than MainWindow adds the view to the interface. It doesn't interact with any component.

There's left_bar.py module that emits only one signal when buttons are clicked with button_action passed as data.
 - that signal is caught in MainWindow and MainWindow emits another signal.
 - That signal from MainWindow is caught in controller and calls the method in controller using the button_action as argument.

Then there's TableModel. It creates the QAbstractItemModel and sets the data to the model. It also has 'appdata.'

Then there's AppData. It creates the SQLite3 database and has methods to interact with the database.
```