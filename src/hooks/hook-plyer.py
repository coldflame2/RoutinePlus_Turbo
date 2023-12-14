# This hook-plyer.py file is only for when packaging with PyInstaller.
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Plyer requires data files (platform-specific backends) to be bundled with your application.
# This hook ensures these data files are included.

datas = collect_data_files('plyer.platforms', include_py_files=True)

