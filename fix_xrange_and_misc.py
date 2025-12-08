#!/usr/bin/env python3
"""
Fix xrange, raw_input, and diamond operator (Python 2→3)

Converts:
- xrange() → range()
- raw_input() → input()
- <> → !=
- u"string" / u'string' → "string" / 'string' (Unicode literals)

These are auto-fixable issues that prevent Python 3 execution.
"""

import os
import re
from pathlib import Path


def fix_patterns(content):
    """Fix various Python 2 patterns."""
    changes = []

    # Fix xrange() → range()
    new_content, count = re.subn(r'\bxrange\(', 'range(', content)
    if count > 0:
        changes.append(f"xrange → range: {count}")
        content = new_content

    # Fix raw_input() → input()
    new_content, count = re.subn(r'\braw_input\(', 'input(', content)
    if count > 0:
        changes.append(f"raw_input → input: {count}")
        content = new_content

    # Fix <> operator → !=
    new_content, count = re.subn(r'(\s+)<>(\s+)', r'\1!=\2', content)
    if count > 0:
        changes.append(f"<> → !=: {count}")
        content = new_content

    # Fix unicode literals u"string" and u'string'
    # Only fix if not in a comment
    lines = content.split('\n')
    unicode_count = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            continue  # Skip comments

        # Match u"..." or u'...'
        new_line, count = re.subn(r'\bu(["\'])', r'\1', line)
        if count > 0:
            unicode_count += count
            lines[i] = new_line

    if unicode_count > 0:
        changes.append(f"u'' literals removed: {unicode_count}")
        content = '\n'.join(lines)

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

    print("Fixing xrange, raw_input, <>, and unicode literals...")
    print("=" * 80)

    for py_file in python_dir.rglob('*.py'):
        if should_skip(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                original = f.read()

            fixed, changes = fix_patterns(original)

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
