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