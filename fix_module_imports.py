#!/usr/bin/env python3
"""
Fix Python 2 to Python 3 module import renames.

Common renames:
- urllib2 → urllib.request, urllib.error
- anydbm → dbm
- UserDict → collections.UserDict
- email.MIMEText → email.mime.text
- cPickle → pickle
"""

import re
import sys
from pathlib import Path


def fix_imports_in_file(file_path):
    """Fix Python 2 → 3 module imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return 0

    original_content = content
    changes = 0

    # Fix urllib2 imports
    # Pattern 1: import urllib2
    if re.search(r'^import urllib2\s*$', content, re.MULTILINE):
        content = re.sub(
            r'^import urllib2\s*$',
            'import urllib.request as urllib2',
            content,
            flags=re.MULTILINE
        )
        changes += 1

    # Pattern 2: from urllib2 import X
    if re.search(r'^from urllib2 import', content, re.MULTILINE):
        # Replace from urllib2 import X with from urllib.request import X
        content = re.sub(
            r'^from urllib2 import',
            'from urllib.request import',
            content,
            flags=re.MULTILINE
        )
        changes += 1

    # Fix anydbm → dbm
    if 'import anydbm' in content:
        content = re.sub(
            r'\bimport anydbm\b',
            'import dbm as anydbm',
            content
        )
        changes += 1

    if 'from anydbm' in content:
        content = re.sub(
            r'\bfrom anydbm import',
            'from dbm import',
            content
        )
        changes += 1

    # Fix UserDict → collections.UserDict
    if re.search(r'^import UserDict\s*$', content, re.MULTILINE):
        content = re.sub(
            r'^import UserDict\s*$',
            'from collections import UserDict',
            content,
            flags=re.MULTILINE
        )
        changes += 1

    if re.search(r'^from UserDict import', content, re.MULTILINE):
        content = re.sub(
            r'^from UserDict import',
            'from collections import',
            content,
            flags=re.MULTILINE
        )
        changes += 1

    # Fix email.MIMEText → email.mime.text
    if 'email.MIMEText' in content or 'email.MIMEMultipart' in content:
        # Pattern: from email.MIMEText import MIMEText
        content = re.sub(
            r'from email\.MIMEText import',
            'from email.mime.text import',
            content
        )
        content = re.sub(
            r'from email\.MIMEMultipart import',
            'from email.mime.multipart import',
            content
        )
        content = re.sub(
            r'from email\.MIMEBase import',
            'from email.mime.base import',
            content
        )
        changes += 1

    # Fix cPickle → pickle
    if 'cPickle' in content:
        content = re.sub(
            r'\bimport cPickle\b',
            'import pickle as cPickle',
            content
        )
        content = re.sub(
            r'\bfrom cPickle import',
            'from pickle import',
            content
        )
        changes += 1

    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        except Exception as e:
            print(f'Error writing {file_path}: {e}')
            return 0

    return 0


def main():
    """Find and fix all Python 2 → 3 module imports."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    if not python_root.exists():
        print(f'Error: {python_root} not found')
        sys.exit(1)

    print(f'Scanning for Python 2 module imports...\n')

    # Patterns to search for
    search_patterns = [
        'urllib2',
        'anydbm',
        'UserDict',
        'email.MIMEText',
        'cPickle',
    ]

    files_to_fix = set()

    # Find files containing these patterns
    for pattern in search_patterns:
        for py_file in python_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if pattern in content:
                    files_to_fix.add(py_file)
            except:
                pass

    total_changes = 0
    files_changed = 0

    for py_file in sorted(files_to_fix):
        changes = fix_imports_in_file(py_file)
        if changes > 0:
            rel_path = py_file.relative_to(python_root)
            print(f'✅ {rel_path}: fixed {changes} import(s)')
            total_changes += changes
            files_changed += 1

    print(f'\n{"="*70}')
    print(f'Summary: Fixed imports in {files_changed} files ({total_changes} changes)')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
