# Python
import logging
import sys
import traceback

from PyQt6.QtGui import QIcon
# PyQt
from PyQt6.QtWidgets import QApplication, QMessageBox

# This app's utilities and resources
from src.utils import helper_fn

# This app's modules
from src.utils.app_logging import setup_root_logger
from src.views.main_window import MainWindow
from src.controllers.controller import Controller
from src.models.table_model import TableModel
from src.views.table_view import TableView


class MainApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self._get_and_set_app_info()

    def set_controller_and_view(self, controller, table_view):
        self.controller = controller
        self.table_view = table_view
        self.main_window = MainWindow(table_view, controller)

        self._initialize_events()

    def _get_and_set_app_info(self):
        """
        Get app info from environment_cls and set it.
        """
        self.environment_cls = helper_fn.get_environment_cls(caller=main)
        app_name = self.environment_cls.APP_NAME
        org_name = self.environment_cls.ORG_NAME
        version = self.environment_cls.VERSION
        self.setApplicationName(app_name)
        self.setApplicationDisplayName(app_name)

        self.setOrganizationName(org_name)
        self.setApplicationVersion(version)
        icon_relative_path = f'resources/icons/others/{self.environment_cls.ICON_NAME}'
        icon_path = helper_fn.resource_path(icon_relative_path)
        self.setWindowIcon(QIcon(icon_path))
        logging.debug(f" _get_and_set_app_info method successfully completed.")

    def _initialize_events(self):
        self.main_window.close_requested_signal.connect(self.prepare_to_close_app)
        logging.debug(f" _initialize_events method successfully completed.")

    def prepare_to_close_app(self, source=None):
        """
        Ask for confirmation. If received, call final close/quit method.
        """
        logging.debug(f"Closing....")
        logging.warning(f"****CLOSING DOWN IN PROGRESS. [closing source: {source}]****")

        try:
            self.main_window.set_win_state_and_geometry()
            self.main_window.closing_source = source

            # Get "if confirmation needed" setting
            is_confirmation_needed = False  # Set it to False for now

        except Exception as e:
            logging.error(f" Exception type:{type(e)} when preparing to close the app.")
            is_confirmation_needed = True  # If exception, set enable the confirmation required

        if is_confirmation_needed:  # call method to show confirmation box
            logging.warning(f" **Getting confirmation to close the app...")
            confirmation_response = self.confirmation_box()
            if confirmation_response:  # If method to show confirmation box returned True
                logging.warning(f" CONFIRMATION to close the app received.")
                self.final_close_down()

            else:
                logging.warning(f" ****closeEvent ignored because the user chose not to exit.****")

        else:  # directly without confirmation box
            logging.warning(f" **Exit Confirmation disabled. Calling final close down method.**")
            self.final_close_down()

    def confirmation_box(self):
        """
        Ask for confirmation.

        :return:
        Return confirmation response to
        """

        logging.warning(f" **Showing Exit Confirmation response box.")

        yes_button = QMessageBox.StandardButton.Yes
        no_button = QMessageBox.StandardButton.No
        title = "Confirm Exit?"
        message = "Are you sure you want to exit?"

        # Arguments: Parent, Title, Text, Button 1, Button 2, Default button
        response = QMessageBox.question(self.main_window, title, message, yes_button | no_button, no_button)

        if response == QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    def final_close_down(self):
        logging.warning(f" ****FINAL CLOSING (Calling 'instance.quit' on QApplication)****")
        try:
            self.main_window.close()
            QApplication.instance().quit()
        except Exception as e:
            logging.error(f"EXCEPTION type:{type(e)} when quitting app. Exception: {e}")


def main():
    try:
        setup_root_logger()
        logging.debug(f"")
        logging.debug(f"****APPLICATION STARTED****")
        logging.debug(f"")

        main_app = MainApp()

        model = TableModel()
        table_view = TableView()
        table_view.setModel(model)
        controller = Controller(model, table_view)

        main_app.set_controller_and_view(controller, table_view)

        # main_app.setQuitOnLastWindowClosed(True)  # To prevent app from closing when closing reminder window

        main_app.aboutToQuit.connect(lambda: app_about_to_quit(model))

        main_app.main_window.show()

        logging.debug("main function loop starting.")

        sys.exit(main_app.exec())
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"Exception type:{type(e)} in main(). (Description{e}.")
        traceback.print_exc()


def app_about_to_quit(model):
    print(f"***APPLICATION CLOSED SUCCESSFULLY****")
    logging.warning(f"***APPLICATION CLOSED SUCCESSFULLY****")
    model.close_database()


if __name__ == '__main__':
    main()