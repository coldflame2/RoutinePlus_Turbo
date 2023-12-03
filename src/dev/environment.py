import logging
import os
from pathlib import Path

from PyQt6.QtCore import QSettings


class DefaultEnvironment:
    APP_NAME = "Routine Plus Turbo"
    VERSION = "1.0.0 Turbo"
    ORG_NAME = "ColdFlame Turbo"

    SYSTEM_PATH = os.getenv('APPDATA')  # Get the 'APPDATA' folder path

    APP_FOLDER_PATH = os.path.join(SYSTEM_PATH, f'{APP_NAME}{VERSION}')

    LOG_FOLDER_NAME = f'Logs ({APP_NAME})'
    LOG_FILE_NAME = f'Log {VERSION}.log'

    DATA_FOLDER_NAME = f'Data ({APP_NAME})'
    DATA_FILE_NAME = f'Routine {VERSION}.db'

    BACKUP_FOLDER_NAME = f'Backup_({APP_NAME})'

    ICON_NAME = 'icon.png'
    WIN_TITLE = f"{APP_NAME}.{VERSION}"

    LOCAL_SERVER = f'Local Sever for {APP_NAME}.{VERSION}'

    SETTINGS_VALUES = QSettings(f'{APP_NAME}', 'Settings')


class DevelopmentEnvironment(DefaultEnvironment):
    APP_NAME = "DEV Routine Plus Turbo"
    VERSION = "1.0.0"
    ORG_NAME = "ColdFlame"

    SYSTEM_PATH = Path(os.path.expanduser("~")) / "Desktop"  # Get Desktop

    APP_FOLDER_PATH = os.path.join(SYSTEM_PATH, f'{APP_NAME}{VERSION}')

    LOG_FOLDER_NAME = f'Logs ({APP_NAME})'
    LOG_FILE_NAME = f'Log {VERSION}.log'

    DATA_FOLDER_NAME = f'Data ({APP_NAME})'
    DATA_FILE_NAME = f'Routine {VERSION}.db'

    BACKUP_FOLDER_NAME = f'Backup_({APP_NAME})'

    ICON_NAME = 'dev_icon.png'
    WIN_TITLE = f"{APP_NAME}.{VERSION}"

    LOCAL_SERVER = f'Local Sever for {APP_NAME}.{VERSION}'

    SETTINGS_VALUES = QSettings(f'{APP_NAME}', 'Settings')


class ProductionEnvironment(DefaultEnvironment):
    # No overrides. So all variables from the superclass 'DefaultConfig' remain the same.
    pass


environment = os.getenv('APP_ENV')  # Get the environment using the key 'APP_ENV'

# Set the appropriate environment_cls class based on the environment variable
if environment == 'development':
    environment_cls = DevelopmentEnvironment
    print(f"\nAPPLICATION STARTED IN '{environment}' environment.")
    logging.debug("App_env: Development")

else:
    environment_cls = ProductionEnvironment

    logging.warning(
        f"READ: Currently in {environment} environment. "
        f"Set app_env variable to dev if working in development.\n"
        f"If in production/use, then ignore.\n"
        )

    print(
        f"READ: Currently in {environment} environment. "
        f"Set app_env variable to dev if working in development.\n"
        f"If in production/use, then ignore.\n"
        )

# This page basically contains global defaults that switch depending on environment.
# As opposed to default.py file, where the default remain constant no matter what.


"""
environment.py

This module provides configuration classes for the application. 
The configuration is determined by the environment in which the application is running.


Classes:
    - DefaultConfig: The base configuration class containing general settings like logging directories, 
        database details, and application metadata.

    - DevelopmentConfig(DefaultConfig): A subclass of `DefaultConfig`. This contains settings specific 
        to the development environment, such as different paths for logs and data.

    - ProductionConfig(DefaultConfig): A subclass of `DefaultConfig`. For now, it doesn't override or 
        add any settings but is kept for clarity and potential future use.

Variables:
    - app_env: Determines the current environment the application is running in. This 
        is fetched from the environment variables (which is usually added to run configurations 
        in PyCharm and other similar IDEs).

    - env_config: Holds an instance of either `DevelopmentConfig` or `ProductionConfig` 
        based on the `app_env` value.

Usage:
    To access configurations:

    from env_config import env_config
    print(env_config.LOG_FOLDER_NAME)

Note:
    If the environment isn't explicitly set to 'development', the module defaults 
    to using the settings in `ProductionConfig`.
"""