"""
Database schema initialization and management.
"""

import os
import sqlite3
from utils.paths import get_db_path

def init_database():
    """Initialize the database with required tables."""
    db_path = get_db_path()
    
    # Create .vcdata directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_items (
            path TEXT PRIMARY KEY,
            active INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_versions (
            path TEXT,
            version INTEGER,
            diff TEXT,
            content TEXT,
            timestamp TEXT,
            PRIMARY KEY (path, version)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            name TEXT PRIMARY KEY,
            note TEXT,
            timestamp TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshot_files (
            snapshot TEXT,
            path TEXT,
            version INTEGER,
            PRIMARY KEY (snapshot, path),
            FOREIGN KEY (snapshot) REFERENCES snapshots(name)
        )
    ''')
    
    conn.commit()
    conn.close()