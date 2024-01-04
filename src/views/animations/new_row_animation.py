import logging

from PyQt6.QtCore import QAbstractAnimation, QEasingCurve, QTimer


class NewRowAnimation(QAbstractAnimation):

    def __init__(self, view, row, duration=800, parent=None):
        super().__init__(parent)

        self.height_duration = 650
        self.opacity_duration = 800

        self.view = view
        self.row = row

        self.finished.connect(self.reset_values)

    def duration(self):
        if self.height_duration > self.opacity_duration:
            return self.height_duration
        else:
            return self.opacity_duration

    def updateCurrentTime(self, currentTime):
        if not self.view or self.row < 0:
            return
        try:
            self.setup_height_animation(currentTime)
            self.setup_opacity_animation(currentTime)

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")

    def setup_height_animation(self, currentTime):
        easing_curve = QEasingCurve(QEasingCurve.Type.InOutQuart)
        progress = easing_curve.valueForProgress(currentTime / self.height_duration)

        animated_height = 0 + progress * 40
        self.view.setRowHeight(self.row, int(animated_height))

    def setup_opacity_animation(self, currentTime):
        easing_curve = QEasingCurve(QEasingCurve.Type.Linear)
        progress = min(1.0, easing_curve.valueForProgress(currentTime / self.opacity_duration))

        animated_opacity = 255 - (progress*255)
        self.view.table_delegate.fill_opacity_animated = int(animated_opacity)

        self.view.viewport().update()

    def reset_values(self):
        try:
            self.view.reset_new_added_row()

        except Exception as e:
            logging.error(f"Exception type: {type(e)}. Error:{e}")

        self.stop()
