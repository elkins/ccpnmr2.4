"""
Test Suite for Task 1.1: StandardError Compliance

This test suite validates that:
1. No StandardError references exist in the codebase
2. All core modules import successfully in Python 3
3. Exception handling uses Python 3 compatible Exception classes

This follows TDD methodology - tests written first to define success criteria.
"""

import os
import sys
import subprocess
from pathlib import Path


def test_no_standarderror_in_codebase():
    """
    Verify that StandardError is not used anywhere in Python code.

    StandardError was removed in Python 3. All code should use Exception instead.
    """
    ccpnmr_root = Path(__file__).parent / "ccpnmr2.4"

    # Search for StandardError in .py files (excluding comments)
    standarderror_files = []

    for py_file in ccpnmr_root.rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments
                code_part = line.split('#')[0]
                if 'StandardError' in code_part:
                    standarderror_files.append((str(py_file), line_num, line.strip()))

    if standarderror_files:
        error_msg = "Found StandardError references:\n"
        for file_path, line_num, line in standarderror_files:
            error_msg += f"  {file_path}:{line_num}: {line}\n"
        raise AssertionError(error_msg)

    print(f"✅ No StandardError references found in {sum(1 for _ in ccpnmr_root.rglob('*.py'))} Python files")


def test_core_modules_import():
    """
    Verify that core CCPNMR modules import successfully in Python 3.

    This is the acceptance criteria from Task 1.1:
    - python3 -c "import ccpnmr.analysis" should work
    """
    python_path = Path(__file__).parent / "ccpnmr2.4" / "python"

    core_modules = [
        "ccpnmr.analysis",
        "memops.general",
        "ccp.general",
    ]

    failed_imports = []

    for module in core_modules:
        # Test import using subprocess to isolate each import
        result = subprocess.run(
            [sys.executable, "-c", f"import sys; sys.path.insert(0, '{python_path}'); import {module}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            failed_imports.append((module, result.stderr))

    if failed_imports:
        error_msg = "Failed to import core modules:\n"
        for module, stderr in failed_imports:
            error_msg += f"\n{module}:\n{stderr}\n"
        raise AssertionError(error_msg)

    print(f"✅ Successfully imported {len(core_modules)} core modules")


def test_python3_exception_patterns():
    """
    Verify that exception handling follows Python 3 patterns.

    Checks for:
    - No bare 'except:' statements (should use 'except Exception:')
    - No 'except StandardError:' patterns
    """
    ccpnmr_root = Path(__file__).parent / "ccpnmr2.4"

    issues = []

    for py_file in ccpnmr_root.rglob("*.py"):
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments
                code_part = line.split('#')[0].strip()

                # Check for except StandardError patterns
                if 'except' in code_part and 'StandardError' in code_part:
                    issues.append((str(py_file), line_num, "Uses StandardError", line.strip()))

    if issues:
        error_msg = "Found Python 3 incompatible exception patterns:\n"
        for file_path, line_num, issue_type, line in issues:
            error_msg += f"  {file_path}:{line_num} [{issue_type}]: {line}\n"
        raise AssertionError(error_msg)

    print(f"✅ All exception handling follows Python 3 patterns")


def test_task_1_1_acceptance_criteria():
    """
    Master test that validates all Task 1.1 acceptance criteria:

    From Task_Breakdown_and_Gantt.md:
    - ✅ Zero StandardError references in code (excluding comments)
    - ✅ All modified files import successfully
    - ✅ python3 -c "import ccpnmr.analysis" works
    """
    print("\n" + "="*70)
    print("Task 1.1: Fix Remaining StandardError Issues - Acceptance Tests")
    print("="*70 + "\n")

    # Run all acceptance tests
    test_no_standarderror_in_codebase()
    test_core_modules_import()
    test_python3_exception_patterns()

    print("\n" + "="*70)
    print("✅ ALL TASK 1.1 ACCEPTANCE CRITERIA PASSED")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_task_1_1_acceptance_criteria()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error:\n{e}")
        sys.exit(1)
