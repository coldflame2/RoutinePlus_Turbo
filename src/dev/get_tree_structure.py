from src.utils.helper_fn import resource_path

import os


def list_files(startpath):
    prefix = '|-- '
    folder_prefix = '|   '

    for root, dirs, files in os.walk(startpath):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        level = root.replace(startpath, '').count(os.sep)
        indent = folder_prefix * level + prefix
        print('{}{}/'.format(indent, os.path.basename(root)))

        sub_indent = folder_prefix * (level + 1) + prefix
        for f in files:
            print('{}{}'.format(sub_indent, f))


start_directory = resource_path("")
list_files(start_directory)
