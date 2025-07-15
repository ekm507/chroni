"""
Path manipulation and resolution utilities.
"""

import os
from storage.files import FileStorage

def resolve_path(path):
    """Resolve a path to absolute path."""
    return os.path.abspath(os.path.expanduser(path))

def get_db_path():
    """Get the path to the database file."""
    home_dir = os.path.expanduser('~')
    vcdata_dir = os.path.join(home_dir, '.chroni')
    return os.path.join(vcdata_dir, 'chroni.db')

def get_text_files_in_directory(directory):
    """Get all text files in a directory recursively."""
    file_storage = FileStorage()
    text_files = []

    for root, dirs, files in os.walk(directory):
        # Skip .chroni directory
        if '.chroni' in dirs:
            dirs.remove('.chroni')

        for file in files:
            file_path = os.path.join(root, file)
            if file_storage.is_text_file(file_path):
                text_files.append(file_path)

    return text_files
