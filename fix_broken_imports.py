#!/usr/bin/env python3
"""
Fix broken import statements like:
from ccp.api.lims.ExpBlueprint(import ExpBlueprintStore)

Should be:
from ccp.api.lims.ExpBlueprint import ExpBlueprintStore
"""

import re
from pathlib import Path


def fix_broken_imports(file_path):
    """Fix broken import statements in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return 0

    original_content = content

    # Pattern: from X(import Y)  -->  from X import Y
    # Matches: from module.path(import name) or from module.path(import name as alias)
    pattern = r'from\s+([a-zA-Z0-9_.]+)\(import\s+([a-zA-Z0-9_]+(?:\s+as\s+[a-zA-Z0-9_]+)?)\)'
    replacement = r'from \1 import \2'

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
    """Find and fix all broken imports."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    total_changes = 0
    files_changed = 0

    for py_file in python_root.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        changes = fix_broken_imports(py_file)
        if changes > 0:
            rel_path = py_file.relative_to(python_root)
            print(f'✅ {rel_path}')
            total_changes += changes
            files_changed += 1

    print(f'\n{"="*70}')
    print(f'Summary: Fixed broken imports in {files_changed} files')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
