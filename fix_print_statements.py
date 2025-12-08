#!/usr/bin/env python3
"""
Fix Python 2 print statements to Python 3 print() function calls.

This script:
1. Finds all .py files with print statements
2. Converts print X to print(X)
3. Preserves comments and indentation
4. Reports all changes made
"""

import re
import sys
from pathlib import Path


def fix_print_in_file(file_path):
    """Fix Python 2 print statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return 0

    fixed_lines = []
    changes = 0

    for line_num, line in enumerate(lines, 1):
        original_line = line

        # Skip if line is just whitespace or starts with comment
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            fixed_lines.append(line)
            continue

        # Check if line contains print statement (not function call)
        # Pattern: 'print' followed by space/tab but NOT by '('
        # Must handle: print "msg", print x, print x,y, etc.

        # Split on # to separate code from comments
        if '#' in line:
            # Find first # that's not in a string
            in_string = False
            string_char = None
            hash_pos = -1

            for i, char in enumerate(line):
                if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                elif char == '#' and not in_string:
                    hash_pos = i
                    break

            if hash_pos >= 0:
                code_part = line[:hash_pos]
                comment_part = line[hash_pos:]
            else:
                code_part = line
                comment_part = ''
        else:
            code_part = line
            comment_part = ''

        # Check if code_part has print statement
        # Pattern: print followed by space/tab (but not by '(')
        pattern = r'(\s*)print\s+(?!\()'
        match = re.search(pattern, code_part)

        if match:
            # This is a print statement needing conversion
            indent = match.group(1)
            print_pos = match.start() + len(indent)

            # Extract what comes after 'print '
            after_print = code_part[print_pos + 6:].lstrip()  # 6 = len('print ')

            # Remove trailing whitespace/newline
            after_print = after_print.rstrip()

            # Build fixed line
            fixed_line = code_part[:print_pos] + f'print({after_print})' + comment_part

            if fixed_line != original_line:
                fixed_lines.append(fixed_line)
                changes += 1
            else:
                fixed_lines.append(original_line)
        else:
            fixed_lines.append(original_line)

    if changes > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return changes
        except Exception as e:
            print(f'Error writing {file_path}: {e}')
            return 0

    return 0


def main():
    """Find and fix all Python 2 print statements."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    if not python_root.exists():
        print(f'Error: {python_root} not found')
        sys.exit(1)

    print(f'Scanning {python_root} for print statements...\n')

    total_changes = 0
    files_changed = 0

    # Get all .py files
    for py_file in python_root.rglob('*.py'):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue

        changes = fix_print_in_file(py_file)
        if changes > 0:
            rel_path = py_file.relative_to(python_root)
            print(f'✅ {rel_path}: {changes} print statements fixed')
            total_changes += changes
            files_changed += 1

    print(f'\n{"="*70}')
    print(f'Summary: Fixed {total_changes} print statements in {files_changed} files')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
