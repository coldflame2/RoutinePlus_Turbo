import pytest
from PyQt6.QtCore import QAbstractItemModel
from src.models.table_model import TableModel

def test_tablemodel_initialization():
    # Assuming TableModel can be instantiated without any arguments
    model = TableModel()
    assert model is not None
    assert isinstance(model, QAbstractItemModel)  # Check if it's a subclass of QAbstractItemModel
