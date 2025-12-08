#!/usr/bin/env python3
"""
Fix Dictionary Iteration Methods (Python 2→3)

Converts:
- .iteritems() → .items()
- .itervalues() → .values()
- .iterkeys() → .keys()

These are high-severity issues (547 total occurrences) that prevent
code from running in Python 3.
"""

import os
import re
from pathlib import Path


def fix_dict_iteration(content):
    """Fix dictionary iteration methods."""
    changes = []

    # Fix .iteritems()
    new_content, count = re.subn(r'\.iteritems\(\)', '.items()', content)
    if count > 0:
        changes.append(f"iteritems → items: {count}")
        content = new_content

    # Fix .itervalues()
    new_content, count = re.subn(r'\.itervalues\(\)', '.values()', content)
    if count > 0:
        changes.append(f"itervalues → values: {count}")
        content = new_content

    # Fix .iterkeys()
    new_content, count = re.subn(r'\.iterkeys\(\)', '.keys()', content)
    if count > 0:
        changes.append(f"iterkeys → keys: {count}")
        content = new_content

    return content, changes


def should_skip(filepath):
    """Determine if file should be skipped."""
    path_str = str(filepath)
    skip_patterns = ['/test/', '/examples/', '/workshop/', '/doc/']
    return any(pattern in path_str for pattern in skip_patterns)


def main():
    """Main entry point."""
    root_dir = Path(__file__).parent
    python_dir = root_dir / 'ccpnmr2.4' / 'python'

    files_modified = 0
    total_changes = 0

    print("Fixing dictionary iteration methods...")
    print("=" * 80)

    for py_file in python_dir.rglob('*.py'):
        if should_skip(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                original = f.read()

            fixed, changes = fix_dict_iteration(original)

            if changes:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(fixed)

                files_modified += 1
                change_count = sum(int(c.split(': ')[1]) for c in changes)
                total_changes += change_count

                relative_path = py_file.relative_to(python_dir)
                print(f"✓ {relative_path}: {', '.join(changes)}")

        except Exception as e:
            print(f"✗ Error processing {py_file}: {e}")

    print("=" * 80)
    print(f"Modified {files_modified} files")
    print(f"Total changes: {total_changes}")


if __name__ == '__main__':
    main()
