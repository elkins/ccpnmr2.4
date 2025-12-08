#!/usr/bin/env python3
"""
Fix TabError issues by converting tabs to spaces consistently.

Python 3 is stricter about mixing tabs and spaces in indentation.
This script converts all tabs to 2 spaces (CCPN convention).
"""

import sys
from pathlib import Path


def fix_tabs_in_file(file_path, tab_size=2):
    """Convert tabs to spaces in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f'Error reading {file_path}: {e}')
        return 0

    fixed_lines = []
    changes = 0

    for line in lines:
        if '\t' in line:
            # Convert tabs to spaces
            fixed_line = line.expandtabs(tab_size)
            fixed_lines.append(fixed_line)
            changes += 1
        else:
            fixed_lines.append(line)

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
    """Fix tab errors in specified files."""
    python_root = Path(__file__).parent / 'ccpnmr2.4' / 'python'

    if not python_root.exists():
        print(f'Error: {python_root} not found')
        sys.exit(1)

    # Files reported with TabErrors
    problem_files = [
        'memops/format/compatibility/downgrade/v_3_0_a1/General.py',
        'ccp/format/pales/rdcConstraintsIO.py',
        'ccpnmr/analysis/core/ChemicalShiftBasic.py',
        'ccpnmr/analysis/core/ChemicalShiftRef.py',
        'ccpnmr/analysis/wrappers/Shiftx.py',
        'ccpnmr/clouds/CloudThreaderPopup.py',
        'ccpnmr/clouds/NoeRelaxation.py',
        'ccpnmr/format/converters/PalesFormat.py',
        'ccpnmr/nexus/AutoBackbonePopup.py',
    ]

    print(f'Fixing tab errors...\n')

    total_changes = 0
    files_changed = 0

    for rel_path in problem_files:
        file_path = python_root / rel_path
        if file_path.exists():
            changes = fix_tabs_in_file(file_path)
            if changes > 0:
                print(f'✅ {rel_path}: {changes} lines with tabs converted')
                total_changes += changes
                files_changed += 1
        else:
            print(f'⚠️  {rel_path}: not found')

    print(f'\n{"="*70}')
    print(f'Summary: Fixed tabs in {files_changed} files ({total_changes} lines)')
    print(f'{"="*70}\n')


if __name__ == '__main__':
    main()
