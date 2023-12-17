import pytest
from src.models.app_data import AppData

def test_appdata_creation():
    app_data = AppData()
    assert app_data is not None
