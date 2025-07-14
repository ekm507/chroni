"""
File history viewing and date-based navigation functionality.
"""

import os
from datetime import datetime
from db.access import DatabaseAccess
from storage.files import FileStorage
from utils.time import format_timestamp, parse_date

class HistoryViewer:
    def __init__(self):
        self.db = DatabaseAccess()
        self.file_storage = FileStorage()
    
    def get_file_history(self, file_path, limit=None):
        """
        Get full history of a file with formatted timestamps.
        Returns list of version info dictionaries.
        """
        if not self.db.path_exists_in_history(file_path):
            return []
        
        versions = self.db.get_all_file_versions(file_path, limit)
        
        # Add formatted timestamps
        for version in versions:
            version['formatted_timestamp'] = format_timestamp(version['timestamp'])
        
        return versions
    
    def get_file_version_info(self, file_path, version):
        """
        Get detailed info for a specific version of a file.
        """
        version_info = self.db.get_file_version(file_path, version)
        
        if not version_info:
            return None
        
        # If this version doesn't have full content, reconstruct it
        if not version_info['content']:
            from core.restore import Restorer
            restorer = Restorer()
            version_info['content'] = restorer._reconstruct_content(file_path, version)
        
        version_info['formatted_timestamp'] = format_timestamp(version_info['timestamp'])
        return version_info
    
    def get_latest_version_info(self, file_path):
        """
        Get info for the latest version of a file.
        """
        latest = self.db.get_latest_version(file_path)
        
        if not latest:
            return None
        
        latest['formatted_timestamp'] = format_timestamp(latest['timestamp'])
        return latest
    
    def find_version_by_date(self, file_path, date_str):
        """
        Find the version of a file closest to a specific date.
        Date can be in formats: YYYY-MM-DD, YYYY-MM-DD HH:MM, or YYYY-MM-DD HH:MM:SS
        """
        target_date = parse_date(date_str)
        
        if not target_date:
            return None
        
        versions = self.db.get_all_file_versions(file_path)
        
        if not versions:
            return None
        
        # Find the version with timestamp closest to but not after the target date
        best_version = None
        best_diff = None
        
        for version in versions:
            version_date = datetime.fromisoformat(version['timestamp'])
            
            if version_date <= target_date:
                diff = abs((target_date - version_date).total_seconds())
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    best_version = version
        
        if best_version:
            best_version['formatted_timestamp'] = format_timestamp(best_version['timestamp'])
        
        return best_version
"""
Snapshot management functionality.
"""

from db.access import DatabaseAccess
from core.restore import Restorer
from utils.time import get_timestamp

class SnapshotManager:
    def __init__(self):
        self.db = DatabaseAccess()
        self.restorer = Restorer()
    
    def create_snapshot(self, name, note=None):
        """
        Create a named snapshot of the current state.
        Returns True if successful, False otherwise.
        """
        # Check if snapshot name already exists
        if self.db.snapshot_exists(name):
            return False
        
        # Get current version of all tracked files
        tracked_items = self.db.get_tracked_items()
        file_versions = {}
        
        for path in tracked_items:
            if self.db.is_file_tracked(path):
                latest_version = self.db.get_latest_version(path)
                if latest_version:
                    file_versions[path] = latest_version['version']
        
        # Create snapshot
        timestamp = get_timestamp()
        self.db.create_snapshot(name, note, timestamp)
        
        # Store file versions for this snapshot
        for path, version in file_versions.items():
            self.db.add_snapshot_file(name, path, version)
        
        return True
    
    def list_snapshots(self):
        """Get list of all snapshots."""
        return self.db.get_all_snapshots()
    
    def restore_snapshot(self, name):
        """
        Restore all files to a snapshot state.
        Returns True if successful, False otherwise.
        """
        snapshot_files = self.db.get_snapshot_files(name)
        
        if not snapshot_files:
            return False
        
        # Restore each file to its snapshot version
        success = True
        for file_info in snapshot_files:
            if not self.restorer.restore_file(file_info['path'], file_info['version']):
                success = False
        
        return success