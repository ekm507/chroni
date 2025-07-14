# Chroni - Lightweight Version Control System

Chroni is a standalone local version control system for tracking and snapshotting text files. It provides a simple CLI interface for managing file versions and creating snapshots.

## Features

- Track files and folders for version control
- Automatic change detection and diff storage
- Named snapshots of project state
- File restoration to any previous version
- SQLite-based storage in `~/.vcdata/chroni.db`

## Installation

1. Ensure you have Python 3.6+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run from the chroni directory: `python -m chroni <command>`

## Usage

### Basic Commands

```bash
# Start tracking a file or folder
python -m chroni track myfile.txt
python -m chroni track src/

# List tracked items
python -m chroni list

# Scan for changes and store them
python -m chroni scan

# Stop tracking (keeps history)
python -m chroni untrack myfile.txt

# Remove all history
python -m chroni forget myfile.txt

# Restore file to specific version
python -m chroni restore myfile.txt --ver 2
```

### Snapshots

```bash
# Create a snapshot
python -m chroni snapshot-create v1.0 --note "Initial release"

# List snapshots
python -m chroni snapshot-list

# Restore to snapshot
python -m chroni snapshot-restore v1.0
```

## How It Works

1. **Tracking**: Files and folders are added to a tracking list
2. **Scanning**: Changes are detected by comparing current content with stored versions
3. **Diffs**: Only differences are stored using unified diff format
4. **Snapshots**: Named points in time capturing all file versions
5. **Restoration**: Files can be restored to any previous version or snapshot state

## Storage

- Database: `~/.vcdata/chroni.db` (SQLite)
- Tracks file paths, versions, diffs, and snapshots
- Efficient storage using differential compression