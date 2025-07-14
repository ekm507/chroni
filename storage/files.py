"""
File storage and reading functionality.
"""

import os

class FileStorage:
    def read_file(self, path):
        """Read a text file and return its content."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                raise ValueError(f"Unable to read file as text: {path}")
    
    def write_file(self, path, content):
        """Write content to a file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def is_text_file(self, path):
        """Check if a file is a text file."""
        if not os.path.isfile(path):
            return False
        
        try:
            with open(path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return False
            
            # Try to read as text
            with open(path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except (UnicodeDecodeError, PermissionError):
            return False