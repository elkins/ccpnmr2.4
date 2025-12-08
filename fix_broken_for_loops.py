#!/usr/bin/env python3
"""
Fix broken for loop syntax like:
for x(in y:) → for x in y:
"""

import re
from pathlib import Path


def fix_for_loops(file_path):
    """Fix broken for loops in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return 0

    original_content = content

    # Pattern: for VAR(in EXPR:)  -->  for VAR in EXPR:
    # Matches: for x(in y:) or for item(in items:)
    pattern = r'for\s+(\w+)\(in\s+([^:]+):\)'
    replacement = r'for \1 in \2:'

    content = re.sub(pattern, replacement, content)

    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return 1
        except Exception as e:
            return 0

    return 0


def main():
    """Find and fix all broken for loops."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    total_changes = 0
    files_changed = 0

    for py_file in python_root.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        changes = fix_for_loops(py_file)
        if changes > 0:
            rel_path = py_file.relative_to(python_root)
            print(f'✅ {rel_path}')
            total_changes += changes
            files_changed += 1

    print(f'\n{"="*70}')
    print(f'Summary: Fixed broken for loops in {files_changed} files')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
