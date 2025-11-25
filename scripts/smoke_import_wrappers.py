"""
Try importing all generated `py_*.py` wrapper modules and report success/failure.
"""
import os
import fnmatch
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

wrapper_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if fnmatch.fnmatch(fn, 'py_*.py') and '/c/' in dirpath.replace('\\', '/'):
            wrapper_files.append(Path(dirpath) / fn)

print(f"Found {len(wrapper_files)} generated wrapper files to test")

success = []
failures = []

import importlib.util

for p in wrapper_files:
    name = p.stem
    try:
        spec = importlib.util.spec_from_file_location(name, str(p))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        success.append((p, None))
    except Exception as e:
        failures.append((p, traceback.format_exc()))

print(f"\nImported: {len(success)} success, {len(failures)} failures")
if failures:
    print('\nFailed modules:')
    for p, tb in failures:
        print('-', p)
        print(tb.splitlines()[-2])

print('Done.')
