import inspect
import logging

from PyQt6.QtCore import QObject


class Singleton(type):
    # track of instances of classes using this metaclass. The class itself is the key, and its instance is the value.
    instances_of_classes = {}

    def __call__(cls, *args, **kwargs):
        # Get the name of the class that is being instantiated
        class_name = cls.__name__

        # Get the name of the calling class
        caller_class_name = cls.get_caller_class_name()

        if cls not in cls.instances_of_classes:
            cls.instances_of_classes[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            logging.debug(f"'{class_name}' instance created in '{caller_class_name}'.")
        else:
            logging.debug(
                f"'{class_name}' instance requested in '{caller_class_name},' but already exists. Returning existing instance"
                )

        return cls.instances_of_classes[cls]

    @staticmethod
    def get_caller_class_name():
        stack = inspect.stack()
        # Inspect the stack and find the appropriate frame that represents the class
        for frame_info in stack:
            if 'self' in frame_info.frame.f_locals:
                caller_class = frame_info.frame.f_locals['self'].__class__
                return caller_class.__name__
        return None


class SingletonQObject(type(QObject), Singleton):
    """Allows the Singleton pattern to be used with PyQt6's QObject class. QObject requires a specific metaclass (type(QObject)), so SingletonQObject combines it with Singleton."""
    pass
