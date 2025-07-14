"""
File scanning and change detection functionality.
"""

import os
from db.access import DatabaseAccess
from storage.files import FileStorage
from storage.diffs import DiffStorage
from utils.time import get_timestamp

class Scanner:
    def __init__(self):
        self.db = DatabaseAccess()
        self.file_storage = FileStorage()
        self.diff_storage = DiffStorage()
    
    def scan_all(self):
        """
        Scan all tracked files for changes.
        Returns list of changed files.
        """
        tracked_items = self.db.get_tracked_items()
        changes = []
        
        for path in tracked_items:
            if os.path.isfile(path):
                if self._scan_file(path):
                    changes.append(path)
            elif os.path.isdir(path):
                # Scan all files in directory
                from utils.paths import get_text_files_in_directory
                text_files = get_text_files_in_directory(path)
                for file_path in text_files:
                    if self.db.is_tracked(file_path) and self._scan_file(file_path):
                        changes.append(file_path)
        
        return changes
    
    def _scan_file(self, file_path):
        """
        Scan a single file for changes.
        Returns True if changes were detected and stored.
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            current_content = self.file_storage.read_file(file_path)
        except Exception:
            return False
        
        # Get the latest version
        latest_version = self.db.get_latest_version(file_path)
        
        if latest_version is None:
            # First time tracking this file
            self._store_initial_version(file_path, current_content)
            return True
        
        # Check if content has changed
        if current_content != latest_version['content']:
            self._store_new_version(file_path, current_content, latest_version)
            return True
        
        return False
    
    def _store_initial_version(self, file_path, content):
        """Store the initial version of a file."""
        version = 1
        timestamp = get_timestamp()
        
        self.db.add_file_version(
            path=file_path,
            version=version,
            diff=None,
            content=content,
            timestamp=timestamp
        )
    
    def _store_new_version(self, file_path, new_content, previous_version):
        """Store a new version of a file with diff."""
        version = previous_version['version'] + 1
        timestamp = get_timestamp()
        
        # Create diff
        diff = self.diff_storage.create_diff(
            previous_version['content'],
            new_content
        )
        
        self.db.add_file_version(
            path=file_path,
            version=version,
            diff=diff,
            content=new_content,
            timestamp=timestamp
        )