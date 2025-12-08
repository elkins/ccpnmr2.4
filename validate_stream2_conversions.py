#!/usr/bin/env python3
"""
Stream 2 C→Python Conversion Validation

Tasks 2.1-2.7: Validate conversion status of C modules to Python/NumPy/SciPy

This script:
1. Identifies which C modules have Python implementations
2. Runs tests for each Python implementation
3. Compares performance (Python vs C if available)
4. Verifies module loading preferences
5. Generates completion report

Modules to validate (from Task_Breakdown_and_Gantt.md):
- list.c → Python (Task 2.1)
- diag_dbl.c → NumPy (Task 2.2)
- eigenvalue.c → NumPy (Task 2.3)
- hash_list.c → Python (Task 2.4)
- gamma.c → SciPy (Task 2.5)
- fit1d.c → NumPy (Task 2.6)
- cpmg.c → NumPy (Task 2.7)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Setup paths
script_dir = Path(__file__).parent
python_dir = script_dir / 'ccpnmr2.4' / 'python'
c_dir = script_dir / 'ccpnmr2.4' / 'c' / 'memops' / 'global'
python_impl_dir = python_dir / 'memops' / 'c' / 'python_impl'

sys.path.insert(0, str(python_dir))


class Stream2Validator:
    """Validate C→Python conversion status for Stream 2 tasks."""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'modules': {},
            'summary': {},
            'recommendations': []
        }

        # Modules from Task_Breakdown_and_Gantt.md
        self.target_modules = {
            'list': {'task': '2.1', 'target': 'Python', 'effort': '2-3h'},
            'diag_dbl': {'task': '2.2', 'target': 'NumPy', 'effort': '1-2h'},
            'eigenvalue': {'task': '2.3', 'target': 'NumPy', 'effort': '1-2h'},
            'hash_list': {'task': '2.4', 'target': 'Python', 'effort': '2-3h'},
            'gamma': {'task': '2.5', 'target': 'SciPy', 'effort': '2-3h'},
            'fit1d': {'task': '2.6', 'target': 'NumPy', 'effort': '4-6h'},
            'cpmg': {'task': '2.7', 'target': 'NumPy', 'effort': '4-6h'},
        }

    def check_c_module_exists(self, module_name):
        """Check if C module exists."""
        c_file = c_dir / f"{module_name}.c"
        return c_file.exists()

    def check_python_module_exists(self, module_name):
        """Check if Python implementation exists."""
        py_file = python_impl_dir / f"{module_name}.py"
        return py_file.exists()

    def check_test_exists(self, module_name):
        """Check if test file exists."""
        test_file = python_impl_dir / f"test_{module_name}.py"
        return test_file.exists()

    def check_numba_version_exists(self, module_name):
        """Check if Numba-optimized version exists."""
        numba_file = python_impl_dir / f"{module_name}_numba.py"
        return numba_file.exists()

    def run_module_tests(self, module_name):
        """Run tests for a module using pytest."""
        test_file = python_impl_dir / f"test_{module_name}.py"

        if not test_file.exists():
            return {'status': 'no_tests', 'message': 'No test file found'}

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', str(test_file), '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=python_impl_dir
            )

            # Parse pytest output
            output = result.stdout + result.stderr

            if 'passed' in output:
                # Extract pass/fail counts
                import re
                match = re.search(r'(\d+) passed', output)
                passed = int(match.group(1)) if match else 0
                match = re.search(r'(\d+) failed', output)
                failed = int(match.group(1)) if match else 0

                return {
                    'status': 'success' if result.returncode == 0 else 'failures',
                    'passed': passed,
                    'failed': failed,
                    'output': output[-500:]  # Last 500 chars
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Could not parse test output',
                    'output': output[-500:]
                }

        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'message': 'Tests timed out after 30s'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def analyze_module_import(self, module_name):
        """Check how module is imported (C vs Python)."""
        try:
            # Try importing from python_impl
            exec(f"from memops.c.python_impl import {module_name}")
            python_import = True
        except ImportError:
            python_import = False

        try:
            # Try importing from C extension
            exec(f"from memops.c import {module_name}")
            c_import = True
        except ImportError:
            c_import = False

        return {
            'python_importable': python_import,
            'c_importable': c_import
        }

    def validate_module(self, module_name, info):
        """Validate a single module conversion."""
        print(f"\n{'='*80}")
        print(f"Validating: {module_name} (Task {info['task']}: {info['target']})")
        print(f"{'='*80}")

        result = {
            'task': info['task'],
            'target': info['target'],
            'effort_estimate': info['effort'],
            'c_exists': self.check_c_module_exists(module_name),
            'python_exists': self.check_python_module_exists(module_name),
            'test_exists': self.check_test_exists(module_name),
            'numba_exists': self.check_numba_version_exists(module_name),
        }

        # Check importability
        import_status = self.analyze_module_import(module_name)
        result.update(import_status)

        # Run tests if they exist
        if result['test_exists']:
            print(f"  Running tests for {module_name}...")
            test_result = self.run_module_tests(module_name)
            result['test_result'] = test_result

            if test_result['status'] == 'success':
                print(f"    ✓ Tests passed: {test_result.get('passed', 0)} tests")
            elif test_result['status'] == 'failures':
                print(f"    ✗ Tests failed: {test_result.get('failed', 0)} failures, "
                      f"{test_result.get('passed', 0)} passed")
            elif test_result['status'] == 'no_tests':
                print(f"    ⊘ No tests found")
            else:
                print(f"    ⚠ Test error: {test_result.get('message', 'Unknown')}")
        else:
            print(f"  ⊘ No test file found")
            result['test_result'] = {'status': 'no_tests'}

        # Assess conversion status
        if result['python_exists'] and result['test_exists']:
            test_status = result['test_result']['status']
            if test_status == 'success':
                result['conversion_status'] = 'COMPLETE'
                print(f"  ✅ Conversion status: COMPLETE")
            elif test_status == 'failures':
                result['conversion_status'] = 'INCOMPLETE (test failures)'
                print(f"  ⚠️ Conversion status: INCOMPLETE (test failures)")
            else:
                result['conversion_status'] = 'INCOMPLETE (test errors)'
                print(f"  ⚠️ Conversion status: INCOMPLETE (test errors)")
        elif result['python_exists']:
            result['conversion_status'] = 'INCOMPLETE (no tests)'
            print(f"  ⚠️ Conversion status: INCOMPLETE (no tests)")
        else:
            result['conversion_status'] = 'NOT STARTED'
            print(f"  ❌ Conversion status: NOT STARTED")

        # Check optimizations
        if result['numba_exists']:
            print(f"  ⚡ Numba-optimized version available")

        return result

    def run_validation(self):
        """Run validation for all modules."""
        print("="*80)
        print("STREAM 2: C→PYTHON CONVERSION VALIDATION")
        print("="*80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Python: {sys.version.split()[0]}")
        print()

        for module_name, info in self.target_modules.items():
            result = self.validate_module(module_name, info)
            self.results['modules'][module_name] = result

        self._generate_summary()
        self._print_summary()
        self._generate_recommendations()
        self._write_report()

    def _generate_summary(self):
        """Generate summary statistics."""
        total = len(self.target_modules)
        complete = sum(1 for r in self.results['modules'].values()
                      if r['conversion_status'] == 'COMPLETE')
        incomplete = sum(1 for r in self.results['modules'].values()
                        if 'INCOMPLETE' in r['conversion_status'])
        not_started = sum(1 for r in self.results['modules'].values()
                         if r['conversion_status'] == 'NOT STARTED')

        with_tests = sum(1 for r in self.results['modules'].values()
                        if r['test_exists'])
        tests_passing = sum(1 for r in self.results['modules'].values()
                           if r.get('test_result', {}).get('status') == 'success')

        with_numba = sum(1 for r in self.results['modules'].values()
                        if r['numba_exists'])

        self.results['summary'] = {
            'total_modules': total,
            'complete': complete,
            'incomplete': incomplete,
            'not_started': not_started,
            'completion_percentage': (complete / total * 100) if total > 0 else 0,
            'with_tests': with_tests,
            'tests_passing': tests_passing,
            'with_numba_optimization': with_numba
        }

    def _print_summary(self):
        """Print validation summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        summary = self.results['summary']
        print(f"\nTotal modules: {summary['total_modules']}")
        print(f"  ✅ Complete: {summary['complete']}")
        print(f"  ⚠️  Incomplete: {summary['incomplete']}")
        print(f"  ❌ Not started: {summary['not_started']}")
        print(f"  📊 Completion: {summary['completion_percentage']:.1f}%")
        print()
        print(f"Testing:")
        print(f"  Modules with tests: {summary['with_tests']}/{summary['total_modules']}")
        print(f"  Tests passing: {summary['tests_passing']}/{summary['with_tests']}")
        print()
        print(f"Optimizations:")
        print(f"  Numba versions: {summary['with_numba_optimization']}")

        print("\n" + "-"*80)
        print("MODULE STATUS BREAKDOWN")
        print("-"*80)

        for module_name, result in self.results['modules'].items():
            status = result['conversion_status']
            task = result['task']

            if status == 'COMPLETE':
                icon = '✅'
            elif 'INCOMPLETE' in status:
                icon = '⚠️'
            else:
                icon = '❌'

            print(f"  {icon} Task {task} ({module_name}): {status}")

    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        recommendations = []

        # Check for modules without Python implementations
        not_started = [name for name, r in self.results['modules'].items()
                      if r['conversion_status'] == 'NOT STARTED']
        if not_started:
            recommendations.append({
                'priority': 'HIGH',
                'action': f'Implement Python conversions for: {", ".join(not_started)}',
                'effort': 'Varies by module (see task estimates)'
            })

        # Check for modules without tests
        no_tests = [name for name, r in self.results['modules'].items()
                   if r['python_exists'] and not r['test_exists']]
        if no_tests:
            recommendations.append({
                'priority': 'HIGH',
                'action': f'Create tests for: {", ".join(no_tests)}',
                'effort': '1-2 hours per module'
            })

        # Check for test failures
        test_failures = [name for name, r in self.results['modules'].items()
                        if r.get('test_result', {}).get('status') == 'failures']
        if test_failures:
            recommendations.append({
                'priority': 'HIGH',
                'action': f'Fix test failures in: {", ".join(test_failures)}',
                'effort': '2-4 hours per module'
            })

        # Check for missing Numba optimizations
        no_numba = [name for name, r in self.results['modules'].items()
                   if r['python_exists'] and not r['numba_exists']
                   and r['target'] in ['NumPy', 'SciPy']]
        if no_numba:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': f'Consider Numba optimization for: {", ".join(no_numba)}',
                'effort': '1-2 hours per module'
            })

        # Overall assessment
        if self.results['summary']['completion_percentage'] == 100:
            recommendations.append({
                'priority': 'INFO',
                'action': '🎉 Stream 2 conversions are COMPLETE!',
                'effort': 'None - ready for production'
            })
        else:
            pct = self.results['summary']['completion_percentage']
            recommendations.append({
                'priority': 'INFO',
                'action': f'Stream 2 is {pct:.1f}% complete',
                'effort': 'See task-specific estimates above'
            })

        self.results['recommendations'] = recommendations

        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)

        for rec in recommendations:
            priority = rec['priority']
            print(f"\n[{priority}] {rec['action']}")
            print(f"  Effort: {rec['effort']}")

    def _write_report(self):
        """Write detailed JSON report."""
        report_file = script_dir / 'stream2_conversion_validation.json'

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n\nDetailed report: {report_file}")


def main():
    """Main entry point."""
    validator = Stream2Validator()
    validator.run_validation()

    # Exit with success if all modules are complete
    completion = validator.results['summary']['completion_percentage']
    sys.exit(0 if completion == 100 else 1)


if __name__ == '__main__':
    main()
