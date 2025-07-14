"""
Diff creation and application functionality.
"""

import difflib

class DiffStorage:
    def create_diff(self, old_content, new_content):
        """Create a unified diff between two content strings."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='old',
            tofile='new',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def apply_diff(self, original_content, diff):
        """Apply a unified diff to original content."""
        original_lines = original_content.splitlines(keepends=True)
        
        # Parse the diff
        patch = difflib.unified_diff.__doc__  # This is just to import the module
        # We need to manually parse and apply the unified diff
        
        diff_lines = diff.splitlines()
        new_lines = []
        i = 0
        original_idx = 0
        
        while i < len(diff_lines):
            line = diff_lines[i]
            
            if line.startswith('@@'):
                # Parse hunk header
                parts = line.split()
                if len(parts) >= 3:
                    old_range = parts[1][1:]  # Remove the '-'
                    if ',' in old_range:
                        start, count = map(int, old_range.split(','))
                    else:
                        start, count = int(old_range), 1
                    
                    # Adjust for 0-based indexing
                    original_idx = start - 1
                
            elif line.startswith(' '):
                # Context line - copy from original
                if original_idx < len(original_lines):
                    new_lines.append(original_lines[original_idx])
                    original_idx += 1
                
            elif line.startswith('-'):
                # Deleted line - skip in original
                original_idx += 1
                
            elif line.startswith('+'):
                # Added line - add to new content
                new_lines.append(line[1:] + '\n')
            
            i += 1
        
        # Add any remaining original lines
        while original_idx < len(original_lines):
            new_lines.append(original_lines[original_idx])
            original_idx += 1
        
        return ''.join(new_lines)