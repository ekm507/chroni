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

def parse_date(date_str):
    """
    Parse date string in various formats and return datetime object.
    Supports: YYYY-MM-DD, YYYY-MM-DD HH:MM, YYYY-MM-DD HH:MM:SS
    """
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None