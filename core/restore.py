"""
File restoration functionality.
"""

import os
from db.access import DatabaseAccess
from storage.files import FileStorage
from storage.diffs import DiffStorage

class Restorer:
    def __init__(self):
        self.db = DatabaseAccess()
        self.file_storage = FileStorage()
        self.diff_storage = DiffStorage()
    
    def restore_file(self, file_path, version):
        """
        Restore a file to a specific version.
        Returns True if successful, False otherwise.
        """
        file_version = self.db.get_file_version(file_path, version)
        
        if file_version is None:
            return False
        
        try:
            # If this version has full content, use it directly
            if file_version['content']:
                content = file_version['content']
            else:
                # Reconstruct content from diffs
                content = self._reconstruct_content(file_path, version)
            
            # Write the content to the file
            self.file_storage.write_file(file_path, content)
            return True
        
        except Exception:
            return False
    
    def _reconstruct_content(self, file_path, target_version):
        """
        Reconstruct file content for a specific version using diffs.
        """
        # Get all versions up to target version
        versions = self.db.get_file_versions_up_to(file_path, target_version)
        
        if not versions:
            return ""
        
        # Start with the first version (should have full content)
        content = versions[0]['content']
        
        # Apply diffs sequentially
        for i in range(1, len(versions)):
            version = versions[i]
            if version['diff']:
                content = self.diff_storage.apply_diff(content, version['diff'])
        
        return content