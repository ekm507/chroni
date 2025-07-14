"""
Time and timestamp utilities.
"""

from datetime import datetime

def get_timestamp():
    """Get current timestamp as string."""
    return datetime.now().isoformat()

def format_timestamp(timestamp):
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return timestamp