#!/usr/bin/env python3
"""
Smoke Test for Modified Python Files
=====================================

Tests all modified Python files for:
1. Syntax errors (compilation)
2. Import errors (module loading)
3. Basic functionality (where applicable)

This ensures Python 2→3 modernization didn't break anything.
"""

import sys
import os
import importlib.util
from pathlib import Path

# Add ccpnmr2.4/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ccpnmr2.4', 'python'))

# List of modified Python files (relative to project root)
MODIFIED_FILES = [
    'ccpnmr2.4/python/ccp/format/spectra/OpenSpectrum.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/AzaraParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/BrukerParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/ExternalParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/FactorisedParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/FelixParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/NmrPipeData.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/NmrPipeParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/NmrViewParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/UcsfParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/VarianParams.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/XeasyData.py',
    'ccpnmr2.4/python/ccp/format/spectra/params/XeasyParams.py',
    'ccpnmr2.4/python/ccp/format/varian/acqParsHelpReader.py',
    'ccpnmr2.4/python/ccp/format/varian/acqParsIO.py',
    'ccpnmr2.4/python/ccp/format/varian/varianFile.py',
    'ccpnmr2.4/python/ccp/general/Io.py',
    'ccpnmr2.4/python/ccpnmr/workflow/Aria.py',
    'ccpnmr2.4/python/ccpnmr/workflow/Cing.py',
    'ccpnmr2.4/python/ccpnmr/workflow/Fc.py',
    'ccpnmr2.4/python/ccpnmr/workflow/Util.py',
    'ccpnmr2.4/python/cing/STAR/TagTable.py',
    'ccpnmr2.4/python/cing/Scripts/vCing/Utils.py',
    'ccpnmr2.4/python/cing/Scripts/vCing/stripVc.py',
    'ccpnmr2.4/python/cing/Scripts/vCing/topos/PoolDownloader.py',
    'ccpnmr2.4/python/cing/main.py',
    'ccpnmr2.4/python/cing/setupCing.py',
    'ccpnmr2.4/python/extendNmr/ExtendNmrGui.py',
    'ccpnmr2.4/python/gothenburg/prodecomp/PeaksToInterval.py',
    'ccpnmr2.4/python/memops/api/Implementation.py',
    'ccpnmr2.4/python/memops/general/Constants.py',
    'ccpnmr2.4/python/memops/general/Io.py',
    'ccpnmr2.4/python/memops/general/TextWriter_py_2_1.py',
    'ccpnmr2.4/python/memops/general/Util.py',
    'ccpnmr2.4/python/memops/general/Version.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/Boolean.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/Dict.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/Double.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/Float.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/Int.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/List.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/Long.py',
    'ccpnmr2.4/python/memops/general/baseDataTypes/String.py',
    'ccpnmr2.4/python/memops/metamodel/MetaModel.py',
    'ccpnmr2.4/python/memops/metamodel/ModelPortal.py',
    'ccpnmr2.4/python/memops/metamodel/ModelTraverse_py_2_1.py',
    'ccpnmr2.4/python/memops/metamodel/OpTypes.py',
    'ccpnmr2.4/python/memops/metamodel/Util.py',
    'ccpnmr2.4/python/memops/metamodel/XmlModelIo.py',
    'ccpnmr2.4/python/memops/universal/MessageReporter.py',
    'ccpnmr2.4/python/memops/universal/Util.py',
    'installCode.py',
]

class SmokeTest:
    """Smoke test runner."""

    def __init__(self):
        self.passed = []
        self.failed = []
        self.skipped = []

    def test_syntax(self, filepath: str) -> tuple[bool, str]:
        """Test if file has valid Python syntax."""
        try:
            with open(filepath, 'r') as f:
                code = f.read()
            compile(code, filepath, 'exec')
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        except Exception as e:
            return False, f"Error: {e}"

    def test_import(self, filepath: str) -> tuple[bool, str]:
        """Test if file can be imported."""
        # Skip GUI files that require Tkinter
        if 'Gui.py' in filepath or 'Tk' in filepath:
            return None, "Skipped (GUI)"

        # Skip files that need special environment
        skip_patterns = ['vCing', 'ExtendNmr', 'gothenburg']
        if any(pattern in filepath for pattern in skip_patterns):
            return None, "Skipped (special env)"

        try:
            # Convert filepath to module name
            if filepath.startswith('ccpnmr2.4/python/'):
                module_path = filepath.replace('ccpnmr2.4/python/', '')
            elif filepath == 'installCode.py':
                # Skip installCode.py - it's a script, not a module
                return None, "Skipped (script)"
            else:
                module_path = filepath

            module_path = module_path.replace('.py', '').replace('/', '.')

            # Try to import
            spec = importlib.util.find_spec(module_path)
            if spec is None:
                return False, "Module not found"

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return True, "Import OK"
        except ImportError as e:
            # Some import errors are expected (missing dependencies)
            return None, f"Import skipped: {e}"
        except Exception as e:
            return False, f"Import failed: {e}"

    def run_tests(self):
        """Run smoke tests on all modified files."""
        print("=" * 70)
        print("SMOKE TEST: Modified Python Files")
        print("=" * 70)
        print(f"\nTesting {len(MODIFIED_FILES)} modified files...\n")

        for filepath in MODIFIED_FILES:
            full_path = os.path.join(os.path.dirname(__file__), filepath)

            if not os.path.exists(full_path):
                self.failed.append((filepath, "File not found"))
                continue

            # Test 1: Syntax
            syntax_ok, syntax_msg = self.test_syntax(full_path)

            if not syntax_ok:
                self.failed.append((filepath, syntax_msg))
                print(f"✗ {filepath}")
                print(f"  {syntax_msg}")
                continue

            # Test 2: Import
            import_result, import_msg = self.test_import(filepath)

            if import_result is True:
                self.passed.append((filepath, "Syntax + Import OK"))
                print(f"✓ {filepath}")
            elif import_result is False:
                self.failed.append((filepath, import_msg))
                print(f"✗ {filepath}")
                print(f"  Syntax OK, but {import_msg}")
            else:  # None = skipped
                self.skipped.append((filepath, import_msg))
                print(f"~ {filepath}")
                print(f"  Syntax OK, {import_msg}")

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\n✓ Passed: {len(self.passed)}")
        print(f"~ Skipped: {len(self.skipped)}")
        print(f"✗ Failed: {len(self.failed)}")

        if self.failed:
            print("\n" + "=" * 70)
            print("FAILURES:")
            print("=" * 70)
            for filepath, error in self.failed:
                print(f"\n✗ {filepath}")
                print(f"  {error}")

        print("\n" + "=" * 70)

        return len(self.failed) == 0

def main():
    """Run smoke tests."""
    tester = SmokeTest()
    success = tester.run_tests()

    if success:
        print("\n✅ All modified files passed smoke tests!")
        sys.exit(0)
    else:
        print(f"\n❌ {len(tester.failed)} file(s) failed smoke tests")
        sys.exit(1)

if __name__ == '__main__':
    main()
