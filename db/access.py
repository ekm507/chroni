"""
Database access layer for Chroni version control system.
"""

import sqlite3
from utils.paths import get_db_path

class DatabaseAccess:
    def __init__(self):
        self.db_path = get_db_path()
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def add_tracked_item(self, path):
        """Add a path to tracked items."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO tracked_items (path, active) VALUES (?, 1)',
            (path,)
        )
        conn.commit()
        conn.close()
    
    def deactivate_tracked_item(self, path):
        """Deactivate a tracked item."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE tracked_items SET active = 0 WHERE path = ?',
            (path,)
        )
        conn.commit()
        conn.close()
    
    def remove_all_history(self, path):
        """Remove all history for a path."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Remove from tracked items
        cursor.execute('DELETE FROM tracked_items WHERE path = ?', (path,))
        
        # Remove file versions
        cursor.execute('DELETE FROM file_versions WHERE path = ?', (path,))
        
        # Remove from snapshot files
        cursor.execute('DELETE FROM snapshot_files WHERE path = ?', (path,))
        
        conn.commit()
        conn.close()
    
    def is_tracked(self, path):
        """Check if a path is actively tracked."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM tracked_items WHERE path = ? AND active = 1',
            (path,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def path_exists_in_history(self, path):
        """Check if a path exists in any history."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM tracked_items WHERE path = ?',
            (path,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_tracked_items(self):
        """Get all actively tracked items."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT path FROM tracked_items WHERE active = 1')
        result = [row[0] for row in cursor.fetchall()]
        conn.close()
        return result
    
    def add_file_version(self, path, version, diff, content, timestamp):
        """Add a file version."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO file_versions (path, version, diff, content, timestamp) VALUES (?, ?, ?, ?, ?)',
            (path, version, diff, content, timestamp)
        )
        conn.commit()
        conn.close()
    
    def get_latest_version(self, path):
        """Get the latest version of a file."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT version, diff, content, timestamp FROM file_versions WHERE path = ? ORDER BY version DESC LIMIT 1',
            (path,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'version': result[0],
                'diff': result[1],
                'content': result[2],
                'timestamp': result[3]
            }
        return None
    
    def get_file_version(self, path, version):
        """Get a specific version of a file."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT version, diff, content, timestamp FROM file_versions WHERE path = ? AND version = ?',
            (path, version)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'version': result[0],
                'diff': result[1],
                'content': result[2],
                'timestamp': result[3]
            }
        return None
    
    def get_file_versions_up_to(self, path, version):
        """Get all versions of a file up to a specific version."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT version, diff, content, timestamp FROM file_versions WHERE path = ? AND version <= ? ORDER BY version',
            (path, version)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'version': row[0],
                'diff': row[1],
                'content': row[2],
                'timestamp': row[3]
            }
            for row in results
        ]
    
    def is_file_tracked(self, path):
        """Check if a path is a file (not directory) and is tracked."""
        import os
        return self.is_tracked(path) and os.path.isfile(path)
    
    def snapshot_exists(self, name):
        """Check if a snapshot with the given name exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM snapshots WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def create_snapshot(self, name, note, timestamp):
        """Create a new snapshot."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO snapshots (name, note, timestamp) VALUES (?, ?, ?)',
            (name, note, timestamp)
        )
        conn.commit()
        conn.close()
    
    def add_snapshot_file(self, snapshot, path, version):
        """Add a file to a snapshot."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO snapshot_files (snapshot, path, version) VALUES (?, ?, ?)',
            (snapshot, path, version)
        )
        conn.commit()
        conn.close()
    
    def get_all_snapshots(self):
        """Get all snapshots."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name, note, timestamp FROM snapshots ORDER BY timestamp DESC')
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'name': row[0],
                'note': row[1],
                'timestamp': row[2]
            }
            for row in results
        ]
    
    def get_snapshot_files(self, name):
        """Get all files in a snapshot."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT path, version FROM snapshot_files WHERE snapshot = ?',
            (name,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'path': row[0],
                'version': row[1]
            }
            for row in results
        ]