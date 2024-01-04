import logging

from PyQt6.QtCore import QAbstractAnimation, QEasingCurve


class MainWindowAnimation(QAbstractAnimation):
    def __init__(self, main_win, view, duration=500):
        super().__init__()

        self.main_win = main_win
        self.view = view

        self._mainwin_opacity_duration = 500
        self._rows_text_opacity_duration = 800

    def duration(self):
        return max(self._mainwin_opacity_duration, self._rows_text_opacity_duration)

    def updateCurrentTime(self, current_time):
        if not self.main_win or not self.view:
            return

        try:
            self.setup_mainwin_opacity_animation(current_time)
            self.setup_rows_text_opacity_animation(current_time)

        except Exception as e:
            logging.error(f"Animation error: {e}")
            return

        self.finished.connect(self.reset_values)

    def setup_mainwin_opacity_animation(self, win_op_time):
        win_ani_curve = QEasingCurve(QEasingCurve.Type.Linear)
        progress_mainwin_op = min(1.0, win_op_time / self._mainwin_opacity_duration)
        mainwin_op_animated_value = win_ani_curve.valueForProgress(progress_mainwin_op)
        self.main_win.setWindowOpacity(mainwin_op_animated_value)

    def setup_rows_text_opacity_animation(self, rows_txt_op_time):
        rows_txt_ani_curve = QEasingCurve(QEasingCurve.Type.Linear)
        progress_txt_op = min(1.0, rows_txt_op_time / self._rows_text_opacity_duration)
        rows_txt_op_animated_value = int(rows_txt_ani_curve.valueForProgress(progress_txt_op) * 255)
        self.view.table_delegate.txt_opacity = rows_txt_op_animated_value

        self.view.viewport().update()

    def reset_values(self):
        try:
            self.main_win.setWindowOpacity(1)
            self.view.table_delegate.txt_opacity = 255
        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")

        self.stop()
