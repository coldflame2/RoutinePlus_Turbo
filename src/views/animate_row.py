import logging

from PyQt6.QtCore import QPropertyAnimation, pyqtSignal


class AnimateRow:
    def __init__(self, view):
        self.view = view

    def startRowAnimation(self, row, duration=2000):
        logging.debug(f"Starting row animation in AnimateRow.")

        self.view.animated_row = row
        self.view._animated_height = 10

        animation = QPropertyAnimation(self.view, b"_animated_height")
        animation.setDuration(duration)
        animation.setStartValue(0)
        final_height = 50  # Get the final height for the row
        animation.setEndValue(final_height)
        animation.start()

        animation.finished.connect(lambda: self._resetAnimation(row+1))

    def _resetAnimation(self, row):
        self.view.animated_row = -1
        self.view._animated_height = 0
        self.view.update()
