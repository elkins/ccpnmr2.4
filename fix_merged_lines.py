#!/usr/bin/env python3
"""
Fix lines where multiple statements were merged together.

This fixes issues created by the print statement conversion where
statements like "print X  return Y" need to become two lines.
"""

import re
import sys
from pathlib import Path


def fix_merged_lines(file_path):
    """Fix merged statements in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return 0

    fixed_lines = []
    changes = 0

    for line in lines:
        original_line = line

        # Pattern 1: print(...) followed by code on same line
        # Match: print(X)  Y where Y is another statement
        if 'print(' in line and not line.strip().startswith('#'):
            # Look for patterns like:  print(X)  return
            #                          print(X)  print(Y)
            #                          print(X)  var = value
            pattern = r'(.*print\([^)]*\))\s{2,}(\S.*)$'
            match = re.search(pattern, line.rstrip())

            if match:
                part1 = match.group(1)
                part2 = match.group(2)

                # Get indentation from original line
                indent = len(line) - len(line.lstrip())

                # Split into two lines
                fixed_lines.append(part1 + '\n')
                fixed_lines.append(' ' * indent + part2 + '\n')
                changes += 1
                continue

        # Pattern 2: Other merged statements (import X()  Y)
        # Match cases like: import X()  import Y()
        if '()  ' in line and not line.strip().startswith('#'):
            parts = line.split('()  ')
            if len(parts) > 1:
                indent = len(line) - len(line.lstrip())
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:
                        fixed_lines.append(' ' * indent + part.strip() + '()\n')
                    else:
                        fixed_lines.append(' ' * indent + part)
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
    """Find and fix merged lines."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    if not python_root.exists():
        print(f'Error: {python_root} not found')
        sys.exit(1)

    print(f'Scanning for merged statement lines...\n')

    total_changes = 0
    files_changed = 0

    # Find files with merged lines
    for py_file in python_root.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        changes = fix_merged_lines(py_file)
        if changes > 0:
            rel_path = py_file.relative_to(python_root)
            print(f'✅ {rel_path}: split {changes} merged lines')
            total_changes += changes
            files_changed += 1

    print(f'\n{"="*70}')
    print(f'Summary: Fixed {total_changes} merged lines in {files_changed} files')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
