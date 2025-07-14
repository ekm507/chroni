"""
File and folder tracking functionality.
"""

import os
from db.access import DatabaseAccess
from utils.paths import get_text_files_in_directory

class Tracker:
    def __init__(self):
        self.db = DatabaseAccess()
    
    def track_path(self, path):
        """
        Start tracking a file or folder.
        Returns True if newly tracked, False if already tracked.
        """
        if self.is_tracked(path):
            return False
        
        self.db.add_tracked_item(path)
        
        # If it's a directory, track all text files in it
        if os.path.isdir(path):
            text_files = get_text_files_in_directory(path)
            for file_path in text_files:
                if not self.is_tracked(file_path):
                    self.db.add_tracked_item(file_path)
        
        return True
    
    def untrack_path(self, path):
        """
        Stop tracking a path but keep its history.
        Returns True if was tracked, False if not.
        """
        if not self.is_tracked(path):
            return False
        
        self.db.deactivate_tracked_item(path)
        
        # If it's a directory, untrack all files in it
        if os.path.isdir(path):
            text_files = get_text_files_in_directory(path)
            for file_path in text_files:
                if self.is_tracked(file_path):
                    self.db.deactivate_tracked_item(file_path)
        
        return True
    
    def forget_path(self, path):
        """
        Remove all history of a path.
        Returns True if had history, False if not.
        """
        if not self.db.path_exists_in_history(path):
            return False
        
        self.db.remove_all_history(path)
        
        # If it's a directory, forget all files in it
        if os.path.isdir(path):
            text_files = get_text_files_in_directory(path)
            for file_path in text_files:
                if self.db.path_exists_in_history(file_path):
                    self.db.remove_all_history(file_path)
        
        return True
    
    def is_tracked(self, path):
        """Check if a path is currently being tracked."""
        return self.db.is_tracked(path)
    
    def list_tracked(self):
        """Get list of all currently tracked paths."""
        return self.db.get_tracked_items()