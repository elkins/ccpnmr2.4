"""
Generate a detailed mapping report of generated py_*.py wrappers and
attempt to modernize Python-2 implementations with lib2to3 where needed.

Outputs:
 - scripts/wrapper_mapping_report.txt : human-readable mapping and import errors
 - for each converted file: original path plus a .new file with converted content
"""
import os
import fnmatch
import traceback
from pathlib import Path
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'scripts' / 'wrapper_mapping_report.txt'

# Find generated wrapper files under c/ directories named py_*.py
wrapper_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if fnmatch.fnmatch(fn, 'py_*.py') and '/c/' in dirpath.replace('\\', '/'):
            wrapper_files.append(Path(dirpath) / fn)

# Setup lib2to3 refactor tool
fixers = get_fixers_from_package('lib2to3.fixes')
tool = RefactoringTool(fixers)

report_lines = []
converted = []

import importlib.util

report_lines.append(f'Found {len(wrapper_files)} wrapper files\n')

for p in wrapper_files:
    name = p.stem
    line = [f'Wrapper: {p}']
    # attempt to read first 10 lines to detect implementation hint
    try:
        head = p.read_text().splitlines()[:40]
    except Exception as e:
        head = []
    impl_path = None
    dotted = None
    for h in head:
        if 'Loads package-style implementation found at:' in h:
            # previous generator wrote: comment then the path
            # but the impl path is in next lines? parse alternative
            pass
        if "Loads package-style implementation found at:" in h:
            # try to parse the full path from that line
            try:
                impl_path = h.split(':',1)[1].strip()
            except:
                impl_path = None
        if "Loads the pure-Python implementation found at:" in h:
            try:
                impl_path = h.split(':',1)[1].strip()
            except:
                impl_path = None
    # fallback: look for a literal path inside the file
    if not impl_path:
        text = p.read_text()
        import re
        m = re.search(r"implementation module '([\w\.]+)'", text)
        if m:
            dotted = m.group(1)
    if impl_path:
        impl_path = impl_path.strip()
        if impl_path == '':
            impl_path = None
    line.append(f'  Found impl path: {impl_path or dotted or "(none)"}')

    # Try importing the wrapper module to capture errors
    try:
        spec = importlib.util.spec_from_file_location(name, str(p))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        line.append('  Import: SUCCESS')
    except Exception as e:
        tb = traceback.format_exc()
        line.append('  Import: FAILED')
        # capture last meaningful line of traceback
        last = tb.splitlines()[-1]
        line.append(f'  Error: {last}')
        # If we have a referenced impl file path, and the error indicates SyntaxError
        # attempt to modernize the implementation file
        target_impl = None
        if impl_path and os.path.isabs(impl_path) and os.path.exists(impl_path):
            target_impl = impl_path
        else:
            # try to resolve dotted to file
            if dotted:
                parts = dotted.split('.')
                for root in [ROOT / 'python', ROOT]:
                    cand = root.joinpath(*parts)
                    if cand.with_suffix('.py').exists():
                        target_impl = str(cand.with_suffix('.py'))
                        break
        if target_impl and 'SyntaxError' in tb or 'Missing parentheses' in tb or 'invalid syntax' in tb:
            try:
                src = Path(target_impl).read_text()
                new = str(tool.refactor_string(src, target_impl))
                new_path = Path(target_impl + '.new')
                new_path.write_text(new)
                converted.append((target_impl, str(new_path)))
                line.append(f'  Converted: wrote {new_path}')
            except Exception as e2:
                line.append(f'  Conversion FAILED: {e2}')
    report_lines.extend(line)
    report_lines.append('')

# Summarize converted files
report_lines.append('\nConverted files:')
for orig, new in converted:
    report_lines.append(f'- {orig} -> {new}')

REPORT.write_text('\n'.join(report_lines))
print(f'Wrote report to {REPORT}')
if converted:
    print('Converted files:')
    for orig,new in converted:
        print(orig, '->', new)
else:
    print('No files converted')
