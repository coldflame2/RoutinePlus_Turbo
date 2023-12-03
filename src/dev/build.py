import os
import subprocess
import sys
from datetime import datetime

MAJOR = 9
MINOR = 8
PATCH = 0
REMARKS = f""

APP_NAME = "RoutinePlusTurbo"
ORG_NAME = "ColdFlame"

current_datetime = datetime.now().strftime('%d_%B_%Y_%I%M%p%S%f')[:-3]  # Remove last 4 digits to get 'ms'
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
THIS_BUILD = f"{VERSION}.{REMARKS}"
CHANGELOG_FILE = f"Changelog.V{VERSION}.txt"
APP_EXE_NAME = f"{APP_NAME}.{VERSION}"

PATH_FOR_PYINSTALLER_BUILD = (
    f"F:/Creative Projects (Database)/Coding/Daily Routine Windows (PyQt)/PyInstaller/"
    f"Version {MAJOR}/{VERSION} ({current_datetime})({REMARKS})"
    )


def write_changelog():
    os.makedirs(PATH_FOR_PYINSTALLER_BUILD, exist_ok=True)  # Create the directory if it doesn't exist

    with open(
            f'{PATH_FOR_PYINSTALLER_BUILD}/{CHANGELOG_FILE}', 'w'
            ) as f:
        # WRITE THE CHANGELOG HERE
        f.write(f"{VERSION}\n")
        f.write(f"Few basic UI modifications: like icons, widget sizes, and so on. \n")
        f.write(f"Added the option to disable confirmation while closing the app. \n")
        f.write(f"Added the option to disable reminders.\n")
        f.write(f"Fixed the settings manager.\n")
        f.write(f"Ribbon bar is hidden by default.\n")
        f.write(f"Modified reminders column width when setting the reminder to make AM/PM visible.\n")

        f.write(f"\n")


def build():
    # Write the changelog
    write_changelog()

    # Get the directory of the build.py script
    build_script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"build script dir: {build_script_dir}")

    # Define the path to main.py based on the structure
    main_py_path = os.path.join(build_script_dir, '', 'main.py')
    print(f"main.py file path: {main_py_path}")

    main_dir_path = os.path.dirname(main_py_path)
    print(f"{main_dir_path}' <= 'main_dir_path' variable.")

    # Define the path to the assets directory
    assets_dir = os.path.join(main_dir_path, 'modules/assets')
    print(f"assets dir: {assets_dir}")

    # Define the path to the buttons icon directory inside assets directory
    assets_dir_button_icons = os.path.join(assets_dir, 'buttons_icons')
    print(f"assets_dir_button_icons: {assets_dir_button_icons}")

    # Define the path to hooks directory
    hooks_dir = os.path.join(build_script_dir, '', 'hooks')
    print(f"hooks_dir: {hooks_dir}")

    # List of assets to add (only filenames since the complete path is appended below in the for loop)
    assets_list = [
        'minimize_icon.png',
        'minimize_to_tray.png',
        'max_icon.png',
        'close_icon.png',
        'dev_icon.png',
        'icon.png'
        ]

    assets_button_icons_list = [
        'settings_icon.png',
        'minimizetotray_icon.png',
        'newsubtask_icon.png',
        'newtask_icon.png',
        'open_icon.png',
        'save_icon.png',
        'saveas_icon.png'
        ]

    # Build the PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        '--paths', assets_dir,
        '--paths', assets_dir_button_icons,

        '--additional-hooks-dir', hooks_dir,
        '--hidden-import', 'ctypes.wintypes',
        '--distpath', PATH_FOR_PYINSTALLER_BUILD,
        '--workpath', f'{PATH_FOR_PYINSTALLER_BUILD}/build_files',
        '--name', f'{APP_EXE_NAME}',
        '--icon', os.path.join(assets_dir, 'exe_icon.ico')  # Updated path to the icon
        ]

    # Add assets to the cmd list
    for asset in assets_list:
        print(f"asset in 'FOR' loop in assets_list dict: {asset}")
        cmd.append('--add-data')
        cmd.append(f'{os.path.join(assets_dir, asset)};modules/assets/')

    for button_icon_asset in assets_button_icons_list:
        print(f"button_icon_asset in 'FOR' loop in assets_list dict: {button_icon_asset}")
        cmd.append('--add-data')
        cmd.append(f'{os.path.join(assets_dir_button_icons, button_icon_asset)};modules/assets/buttons_icons/')

    # Add changelog data to cmd list
    cmd.extend(['--add-data', f'{PATH_FOR_PYINSTALLER_BUILD}/{CHANGELOG_FILE};.'])

    # Finally, append main.py path
    cmd.append(main_py_path)

    # Execute the command
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    build()
