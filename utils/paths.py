"""
Path manipulation and resolution utilities with config file support.
"""
import os
import json
from pathlib import Path
from storage.files import FileStorage

# Default configuration
DEFAULT_CONFIG = {
    "app_dir": "~/.chroni",
    "db_filename": "chroni.db",
    "excluded_dirs": [".chroni", ".git", "__pycache__", "node_modules"]
}

def get_config_path():
    """Get the path to the configuration file."""
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, '.chroni')
    return os.path.join(config_dir, 'config.json')

def load_config():
    """Load configuration from file, create with defaults if not exists."""
    config_path = get_config_path()

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        except (json.JSONDecodeError, IOError):
            # If config is corrupted, fall back to defaults
            return DEFAULT_CONFIG.copy()
    else:
        # Create config file with defaults
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    config_dir = os.path.dirname(config_path)

    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save config file: {e}")

def resolve_path(path):
    """Resolve a path to absolute path."""
    return os.path.abspath(os.path.expanduser(path))

def get_app_dir():
    """Get the application directory path from config."""
    config = load_config()
    return resolve_path(config['app_dir'])

def get_db_path():
    """Get the path to the database file from config."""
    config = load_config()
    app_dir = resolve_path(config['app_dir'])
    return os.path.join(app_dir, config['db_filename'])

def get_excluded_dirs():
    """Get list of directories to exclude from scanning."""
    config = load_config()
    return config.get('excluded_dirs', DEFAULT_CONFIG['excluded_dirs'])

def get_text_files_in_directory(directory):
    """Get all text files in a directory recursively, excluding configured directories."""
    file_storage = FileStorage()
    text_files = []
    excluded_dirs = get_excluded_dirs()

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            if file_storage.is_text_file(file_path):
                text_files.append(file_path)
    return text_files

def update_config(**kwargs):
    """Update specific configuration values."""
    config = load_config()
    config.update(kwargs)
    save_config(config)
    return config

def get_config():
    """Get current configuration."""
    return load_config()

# Example usage functions
def set_app_directory(new_path):
    """Set the application directory in config."""
    return update_config(app_dir=new_path)

def set_db_filename(new_filename):
    """Set the database filename in config."""
    return update_config(db_filename=new_filename)

def add_excluded_dir(dirname):
    """Add a directory to the exclusion list."""
    config = load_config()
    excluded_dirs = config.get('excluded_dirs', [])
    if dirname not in excluded_dirs:
        excluded_dirs.append(dirname)
        return update_config(excluded_dirs=excluded_dirs)
    return config

def remove_excluded_dir(dirname):
    """Remove a directory from the exclusion list."""
    config = load_config()
    excluded_dirs = config.get('excluded_dirs', [])
    if dirname in excluded_dirs:
        excluded_dirs.remove(dirname)
        return update_config(excluded_dirs=excluded_dirs)
    return config
