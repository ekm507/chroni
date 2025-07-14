#!/usr/bin/env python3
"""
Codebase Generator Script

This script parses a multi-file text content and generates the actual codebase structure
with all files in their proper locations.

Usage: python generate_codebase.py <input_file> [output_directory]
"""

import os
import sys
import re
from pathlib import Path

def parse_multifile_content(content):
    """
    Parse the multi-file content and extract individual files.
    Returns a dictionary mapping file paths to their content.
    """
    files = {}
    current_file = None
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Look for file markers like "# File: path/to/file.py"
        file_match = re.match(r'^# File: (.+)$', line)
        
        if file_match:
            # Save previous file if exists
            if current_file:
                files[current_file] = '\n'.join(current_content)
            
            # Start new file
            current_file = file_match.group(1)
            current_content = []
        else:
            # Add line to current file content
            if current_file:
                current_content.append(line)
    
    # Save the last file
    if current_file:
        files[current_file] = '\n'.join(current_content)
    
    return files

def clean_content(content):
    """Clean up the content by removing leading/trailing whitespace and empty lines at start/end."""
    lines = content.split('\n')
    
    # Remove empty lines at the beginning
    while lines and not lines[0].strip():
        lines.pop(0)
    
    # Remove empty lines at the end
    while lines and not lines[-1].strip():
        lines.pop()
    
    return '\n'.join(lines)

def create_directory_structure(base_dir, files):
    """Create the directory structure for all files."""
    for file_path in files.keys():
        full_path = os.path.join(base_dir, file_path)
        directory = os.path.dirname(full_path)
        
        if directory:
            os.makedirs(directory, exist_ok=True)

def write_files(base_dir, files):
    """Write all files to their respective locations."""
    for file_path, content in files.items():
        full_path = os.path.join(base_dir, file_path)
        
        # Clean the content
        cleaned_content = clean_content(content)
        
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"Created: {file_path}")

def make_executable(base_dir, files):
    """Make Python files executable if they have a shebang."""
    for file_path, content in files.items():
        if file_path.endswith('.py') and content.startswith('#!/'):
            full_path = os.path.join(base_dir, file_path)
            # Make file executable
            os.chmod(full_path, 0o755)
            print(f"Made executable: {file_path}")

def validate_python_syntax(base_dir, files):
    """Validate Python syntax for all .py files."""
    import ast
    
    for file_path, content in files.items():
        if file_path.endswith('.py'):
            try:
                ast.parse(clean_content(content))
                print(f"✓ Syntax valid: {file_path}")
            except SyntaxError as e:
                print(f"✗ Syntax error in {file_path}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_codebase.py <input_file> [output_directory]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "generated_codebase"
    
    # Read the input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    # Parse the multi-file content
    files = parse_multifile_content(content)
    
    if not files:
        print("No files found in the input. Make sure the format is correct.")
        sys.exit(1)
    
    print(f"Found {len(files)} files to generate:")
    for file_path in sorted(files.keys()):
        print(f"  - {file_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create directory structure
    create_directory_structure(output_dir, files)
    
    # Write all files
    write_files(output_dir, files)
    
    # Make Python files executable if needed
    make_executable(output_dir, files)
    
    # Validate Python syntax
    print("\nValidating Python syntax...")
    validate_python_syntax(output_dir, files)
    
    print(f"\nCodebase generated successfully in: {output_dir}")
    print(f"Total files created: {len(files)}")
    
    # Show directory structure
    print("\nGenerated structure:")
    for root, dirs, files_in_dir in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files_in_dir:
            print(f"{subindent}{file}")

if __name__ == "__main__":
    main()
