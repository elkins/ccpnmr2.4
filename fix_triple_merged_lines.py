#!/usr/bin/env python3
"""
Fix lines where three statements were merged together.

Pattern: for X in Y:      if COND:        STATEMENT
Should be split into 3 lines with proper indentation.
"""

import re
from pathlib import Path


def fix_triple_merged(file_path):
    """Fix triple-merged statements in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return 0

    fixed_lines = []
    changes = 0

    for line in lines:
        original_line = line

        # Pattern: for X in Y:  <spaces>  if COND:  <spaces>  STATEMENT
        # Look for lines with multiple colons and lots of spaces
        if line.count(':') >= 2 and '      ' in line:
            # Try to split on multiple spaces followed by keywords
            # Pattern 1: for ... :      if ... :        statement
            pattern = r'^(\s*)for\s+(\w+)\s+in\s+([^:]+):\s{2,}if\s+([^:]+):\s{2,}(.+)$'
            match = re.match(pattern, line.rstrip())

            if match:
                indent = match.group(1)
                var = match.group(2)
                iterable = match.group(3)
                condition = match.group(4)
                statement = match.group(5)

                # Fix (in issue in condition
                condition = condition.replace('(in ', 'in ')

                # Create three properly indented lines
                fixed_lines.append(f'{indent}for {var} in {iterable}:\n')
                fixed_lines.append(f'{indent}  if {condition}:\n')
                fixed_lines.append(f'{indent}    {statement}\n')
                changes += 1
                continue

        fixed_lines.append(original_line)

    if changes > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return changes
        except Exception as e:
            return 0

    return 0


def main():
    """Find and fix all triple-merged lines."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    total_changes = 0
    files_changed = 0

    for py_file in python_root.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        changes = fix_triple_merged(py_file)
        if changes > 0:
            rel_path = py_file.relative_to(python_root)
            print(f'✅ {rel_path}: fixed {changes} triple-merged lines')
            total_changes += changes
            files_changed += 1

    print(f'\n{"="*70}')
    print(f'Summary: Fixed {total_changes} triple-merged lines in {files_changed} files')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
