#!/usr/bin/env python3
"""
Bulk Python 2→3 Syntax Fixer
=============================

Fixes common Python 2 syntax issues across all Python files.
"""

import os
import re
import sys
from pathlib import Path

def fix_file(filepath):
    """Fix Python 2 syntax in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        original = content

        # Fix 1: print statements (various patterns)
        content = re.sub(r'\bprint\s+"([^"]+)"([^\n]*)', r'print("\1"\2)', content)
        content = re.sub(r"\bprint\s+'([^']+)'([^\n]*)", r"print('\1'\2)", content)

        # Fix 2: except syntax
        content = re.sub(r'\bexcept\s+(\w+(?:\.\w+)*)\s*,\s*(\w+)\s*:', r'except \1 as \2:', content)

        # Fix 3: raise with 3 arguments
        content = re.sub(r'\braise\s+(\w+)\s*,\s*([^,]+)\s*,\s*(\w+)', r'raise \1(\2).with_traceback(\3)', content)

        # Only write if changes were made
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Fix all Python files in ccpnmr2.4/python directory."""
    root_dir = Path('ccpnmr2.4/python')

    if not root_dir.exists():
        print(f"Error: {root_dir} not found", file=sys.stderr)
        sys.exit(1)

    files_fixed = 0
    files_processed = 0

    # Find all .py files
    for pyfile in root_dir.rglob('*.py'):
        files_processed += 1
        if fix_file(pyfile):
            files_fixed += 1
            print(f"Fixed: {pyfile}")

    print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")

if __name__ == '__main__':
    main()
