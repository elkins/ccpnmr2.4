#!/usr/bin/env python3
"""
Validate Remaining Python 2→3 Migration Patterns

Scans the CCPNMR codebase for common Python 2 patterns that need updating:
1. Unicode string literals (u'string')
2. Dictionary iteration patterns (.iterkeys(), .itervalues(), .iteritems())
3. Integer division ambiguities (/ vs //)
4. xrange() usage
5. raw_input() usage
6. execfile() usage
7. <> comparison operator
8. has_key() method
9. apply() function
10. reduce() without functools import

This builds on Tasks 1.1 (StandardError), 1.2 (Import validation),
and 1.3 (Smoke tests) to complete Python 3 migration.
"""

import os
import re
import sys
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class Python3PatternValidator:
    """Validate Python 2→3 migration patterns in CCPNMR codebase."""

    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.python_dir = self.root_dir / 'ccpnmr2.4' / 'python'

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'patterns': {},
            'files_scanned': 0,
            'total_issues': 0
        }

        # Patterns to check
        self.patterns = {
            'unicode_literals': {
                'regex': r"u['\"]",
                'description': 'Unicode string literals (u"string" or u\'string\')',
                'severity': 'low',
                'auto_fixable': True,
                'note': 'Python 3 strings are Unicode by default'
            },
            'iterkeys': {
                'regex': r'\.iterkeys\(\)',
                'description': 'dict.iterkeys() → dict.keys()',
                'severity': 'high',
                'auto_fixable': True,
                'note': 'Python 3 dict.keys() returns a view, not a list'
            },
            'itervalues': {
                'regex': r'\.itervalues\(\)',
                'description': 'dict.itervalues() → dict.values()',
                'severity': 'high',
                'auto_fixable': True,
                'note': 'Python 3 dict.values() returns a view, not a list'
            },
            'iteritems': {
                'regex': r'\.iteritems\(\)',
                'description': 'dict.iteritems() → dict.items()',
                'severity': 'high',
                'auto_fixable': True,
                'note': 'Python 3 dict.items() returns a view, not a list'
            },
            'xrange': {
                'regex': r'\bxrange\(',
                'description': 'xrange() → range()',
                'severity': 'high',
                'auto_fixable': True,
                'note': 'Python 3 range() is lazy like xrange()'
            },
            'raw_input': {
                'regex': r'\braw_input\(',
                'description': 'raw_input() → input()',
                'severity': 'medium',
                'auto_fixable': True,
                'note': 'Python 3 input() returns string, not bytes'
            },
            'execfile': {
                'regex': r'\bexecfile\(',
                'description': 'execfile() → exec(open().read())',
                'severity': 'medium',
                'auto_fixable': False,
                'note': 'Requires manual conversion'
            },
            'diamond_operator': {
                'regex': r'\s+<>\s+',
                'description': '<> operator → !=',
                'severity': 'high',
                'auto_fixable': True,
                'note': 'Python 3 removed <> comparison'
            },
            'has_key': {
                'regex': r'\.has_key\(',
                'description': 'dict.has_key(k) → k in dict',
                'severity': 'medium',
                'auto_fixable': False,
                'note': 'Requires rewriting expression'
            },
            'apply_function': {
                'regex': r'\bapply\(',
                'description': 'apply(f, args) → f(*args)',
                'severity': 'low',
                'auto_fixable': False,
                'note': 'Requires manual conversion'
            },
            'reduce_no_import': {
                'regex': r'\breduce\(',
                'description': 'reduce() needs: from functools import reduce',
                'severity': 'medium',
                'auto_fixable': False,
                'note': 'Check if functools.reduce is imported'
            },
            'int_division_ambiguous': {
                'regex': r'\b\w+\s*/\s*\w+',
                'description': 'Potential integer division (/ vs //)',
                'severity': 'low',
                'auto_fixable': False,
                'note': 'Python 3 / is float division, // is integer division'
            }
        }

        # Initialize results for each pattern
        for pattern_name in self.patterns:
            self.results['patterns'][pattern_name] = {
                'count': 0,
                'files': [],
                'occurrences': []
            }

    def should_skip_file(self, filepath):
        """Determine if file should be skipped."""
        path_str = str(filepath)

        # Skip non-Python files
        if not path_str.endswith('.py'):
            return True

        # Skip GUI/Tk modules (out of scope)
        skip_patterns = [
            '/gui/', '/editor/', '/popups/', '/frames/',
            'Popup.py', 'Frame.py', 'Gui.py', 'Window.py',
            '/examples/', '/workshop/', '/test/', '/doc/'
        ]

        for pattern in skip_patterns:
            if pattern in path_str:
                return True

        return False

    def scan_file(self, filepath):
        """Scan a single Python file for Python 2 patterns."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            relative_path = filepath.relative_to(self.python_dir)

            for pattern_name, pattern_info in self.patterns.items():
                regex = re.compile(pattern_info['regex'])

                for line_num, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue

                    matches = regex.findall(line)
                    if matches:
                        self.results['patterns'][pattern_name]['count'] += len(matches)

                        # Add file if not already tracked
                        if str(relative_path) not in self.results['patterns'][pattern_name]['files']:
                            self.results['patterns'][pattern_name]['files'].append(str(relative_path))

                        # Store occurrence
                        self.results['patterns'][pattern_name]['occurrences'].append({
                            'file': str(relative_path),
                            'line': line_num,
                            'content': line.strip()[:100]  # First 100 chars
                        })

        except Exception as e:
            print(f"Error scanning {filepath}: {e}")

    def scan_codebase(self):
        """Scan entire CCPNMR codebase."""
        print(f"Scanning {self.python_dir}")
        print("=" * 80)

        for py_file in self.python_dir.rglob('*.py'):
            if self.should_skip_file(py_file):
                continue

            self.results['files_scanned'] += 1
            self.scan_file(py_file)

            if self.results['files_scanned'] % 100 == 0:
                print(f"Scanned {self.results['files_scanned']} files...")

        # Calculate total issues
        self.results['total_issues'] = sum(
            p['count'] for p in self.results['patterns'].values()
        )

        print(f"\nScanned {self.results['files_scanned']} Python files")
        print(f"Found {self.results['total_issues']} potential issues")

    def print_summary(self):
        """Print summary of findings."""
        print("\n" + "=" * 80)
        print("PYTHON 2→3 PATTERN VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Files scanned: {self.results['files_scanned']}")
        print(f"Total issues found: {self.results['total_issues']}")
        print()

        # Group by severity
        by_severity = defaultdict(list)
        for pattern_name, pattern_info in self.patterns.items():
            count = self.results['patterns'][pattern_name]['count']
            if count > 0:
                by_severity[pattern_info['severity']].append({
                    'name': pattern_name,
                    'count': count,
                    'description': pattern_info['description'],
                    'auto_fixable': pattern_info['auto_fixable']
                })

        # Print by severity
        for severity in ['high', 'medium', 'low']:
            if severity not in by_severity:
                continue

            print(f"\n{severity.upper()} SEVERITY ISSUES:")
            print("-" * 80)

            for issue in sorted(by_severity[severity], key=lambda x: -x['count']):
                fixable = "✅ Auto-fixable" if issue['auto_fixable'] else "⚠️  Manual fix required"
                print(f"  {issue['name']}: {issue['count']} occurrences - {fixable}")
                print(f"    {issue['description']}")

        # Print files with most issues
        print(f"\n\nTOP 10 FILES WITH MOST ISSUES:")
        print("-" * 80)

        file_issue_count = defaultdict(int)
        for pattern_name, pattern_data in self.results['patterns'].items():
            for filepath in pattern_data['files']:
                file_issue_count[filepath] += pattern_data['count']

        top_files = sorted(file_issue_count.items(), key=lambda x: -x[1])[:10]
        for filepath, count in top_files:
            print(f"  {filepath}: {count} issues")

    def write_report(self):
        """Write detailed JSON report."""
        report_file = self.root_dir / 'python3_pattern_validation.json'

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n\nDetailed report written to: {report_file}")

    def generate_fixing_recommendations(self):
        """Generate recommendations for fixing issues."""
        print(f"\n\n" + "=" * 80)
        print("FIXING RECOMMENDATIONS")
        print("=" * 80)

        total_auto_fixable = sum(
            self.results['patterns'][p]['count']
            for p, info in self.patterns.items()
            if info['auto_fixable'] and self.results['patterns'][p]['count'] > 0
        )

        total_manual = sum(
            self.results['patterns'][p]['count']
            for p, info in self.patterns.items()
            if not info['auto_fixable'] and self.results['patterns'][p]['count'] > 0
        )

        print(f"\nAuto-fixable issues: {total_auto_fixable}")
        print(f"Manual fix required: {total_manual}")

        print("\nPriority order for fixes:")
        print("1. HIGH severity auto-fixable (iterkeys, itervalues, iteritems, xrange)")
        print("2. MEDIUM severity auto-fixable (raw_input, diamond operator)")
        print("3. LOW severity auto-fixable (unicode literals)")
        print("4. Manual fixes (has_key, execfile, apply, reduce)")

        print("\nEstimated effort:")
        print(f"  - Auto-fixes: 1-2 hours (create scripts, test)")
        print(f"  - Manual fixes: {total_manual * 2} minutes ({total_manual} issues × 2 min each)")
        print(f"  - Total: 2-4 hours")


def main():
    """Main entry point."""
    root_dir = Path(__file__).parent

    validator = Python3PatternValidator(root_dir)
    validator.scan_codebase()
    validator.print_summary()
    validator.generate_fixing_recommendations()
    validator.write_report()

    # Exit with error code if issues found
    sys.exit(0 if validator.results['total_issues'] == 0 else 1)


if __name__ == '__main__':
    main()
