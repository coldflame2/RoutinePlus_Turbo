import os
import subprocess
import sys
from datetime import datetime

MAJOR = 1
MINOR = 0
PATCH = 3
REMARKS = f""

APP_NAME = "Routine Plus Turbo"
ORG_NAME = "ColdFlame"

current_datetime = datetime.now().strftime('%d_%B_%Y_%I%M%p%S%f')[:-3]  # Remove last 4 digits to get 'ms'
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
THIS_BUILD = f"{VERSION}.{REMARKS}"
CHANGELOG_FILE = f"Changelog.V{VERSION}.txt"
APP_EXE_NAME = f"{APP_NAME}.{VERSION}"

PATH_FOR_PYINSTALLER_BUILD = (
    f"F:/Creative Projects (Database)/Coding/Routine Plus Turbo Executables/"
    f"Version {MAJOR}/{VERSION} ({current_datetime})({REMARKS})"
    )


def write_changelog():
    os.makedirs(PATH_FOR_PYINSTALLER_BUILD, exist_ok=True)  # Create the directory if it doesn't exist

    with open(
            f'{PATH_FOR_PYINSTALLER_BUILD}/{CHANGELOG_FILE}', 'w'
            ) as f:
        # WRITE THE CHANGELOG HERE
        f.write(f"{VERSION}\n")
        f.write(f"First build. Basic UI and functionality. \n")

        f.write(f"\n")


def build():
    # Write the changelog
    write_changelog()

    # Get the directory of the build.py script (this script)
    build_script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"built script directory:'{build_script_dir}'")

    # Define the path to main.py based on the build.py path (this script)
    # go back one level and then go to main.py in 'src' directory
    main_py_path = os.path.join(build_script_dir, '..', 'main.py')
    print(f"main.py file path: {main_py_path}")

    main_dir_path = os.path.dirname(main_py_path)
    print(f"main_dir_path: {main_dir_path}")

    # Define the path to the assets directory
    resources_dir = os.path.join(main_dir_path, 'resources')
    print(f"resources_dir: {resources_dir}")

    # Define the path to the others icons directory inside resources directory
    others_icons_dir = os.path.join(resources_dir, 'icons/others')
    print(f"others_icons_dir: {others_icons_dir}")

    # Define the path to the left bar icons directory inside resources directory
    left_bar_icons_dir = os.path.join(resources_dir, 'icons/left_bar_icons')
    print(f"left_bar_icons_dir: {left_bar_icons_dir}")

    # Define the path to the title bar icons directory inside resources directory
    title_bar_icons_dir = os.path.join(resources_dir, 'icons/title_bar_icons')
    print(f"title_bar_icons_dir: {title_bar_icons_dir}")

    # Define the path to hooks directory
    hooks_dir = os.path.join(build_script_dir, '', 'hooks')
    print(f"hooks_dir: {hooks_dir}")

    # List of icons to add (only filenames since the complete path is appended below in the for loop)
    others_icons_list = [
        'dev_icon.png',
        'icon.png'
        ]

    left_bar_icons_list = [
        'settings_icon.png',
        'minimizetotray_icon.png',
        'newsubtask_icon.png',
        'newtask_icon.png',
        'open_icon.png',
        'save_icon.png',
        'saveas_icon.png'
        ]

    title_bar_icons_list = [
        'minimize_icon.png',
        'minimizetotray_icon.png',
        'max_icon.png',
        'close_icon.png',
        'dev_icon.png',
        'icon.png'
        ]

    # Build the PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        '--paths', resources_dir,
        '--paths', others_icons_dir,
        '--paths', left_bar_icons_dir,
        '--paths', title_bar_icons_dir,

        '--additional-hooks-dir', hooks_dir,
        '--hidden-import', 'ctypes.wintypes',
        '--distpath', PATH_FOR_PYINSTALLER_BUILD,
        '--workpath', f'{PATH_FOR_PYINSTALLER_BUILD}/build_files',
        '--name', f'{APP_EXE_NAME}',
        '--icon', os.path.join(resources_dir, 'icons/others/exe_icon.ico')  # Updated path to the icon
        ]

    # Add others icons to the cmd list
    for icon in others_icons_list:
        print(f"icon in 'FOR' loop in icons_list dict: {icon}")
        cmd.append('--add-data')
        cmd.append(f'{os.path.join(others_icons_dir, icon)};resources/icons/others/')

    for left_bar_icon in left_bar_icons_list:
        print(f"left_bar_icon in 'FOR' loop in icons_list dict: {left_bar_icon}")
        cmd.append('--add-data')
        cmd.append(f'{os.path.join(left_bar_icons_dir, left_bar_icon)};resources/icons/left_bar_icons/')

    for title_bar_icon in title_bar_icons_list:
        print(f"title_bar_icon in 'FOR' loop in icons_list dict: {title_bar_icon}")
        cmd.append('--add-data')
        cmd.append(f'{os.path.join(title_bar_icons_dir, title_bar_icon)};resources/icons/title_bar_icons/')

    # Add changelog data to cmd list
    cmd.extend(['--add-data', f'{PATH_FOR_PYINSTALLER_BUILD}/{CHANGELOG_FILE};.'])

    # Finally, append main.py path
    cmd.append(main_py_path)

    # Execute the command
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    build()
