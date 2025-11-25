"""
Generate a CSV/markdown failure report for generated `py_*.py` wrappers.
For each wrapper this writes: wrapper_path, expected_module (heuristic), import_result, traceback, recommendation
"""
import os
import fnmatch
import csv
import re
import traceback
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]

wrapper_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if fnmatch.fnmatch(fn, 'py_*.py') and '/c/' in dirpath.replace('\\', '/'):
            wrapper_files.append(Path(dirpath) / fn)

out_csv = ROOT / 'scripts' / 'failure_report.csv'
with out_csv.open('w', newline='') as fh:
    writer = csv.writer(fh)
    writer.writerow(['wrapper_path', 'expected_module', 'result', 'traceback', 'recommendation'])

    for p in wrapper_files:
        content = p.read_text()
        # Heuristic: look for "No pure-Python implementation found for 'NAME'"
        m = re.search(r"No pure-Python implementation found for ['\"]([^'\"]+)['\"]", content)
        expected = m.group(1) if m else ''
        try:
            spec = importlib.util.spec_from_file_location(p.stem, str(p))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            res = 'OK'
            tb = ''
            rec = 'None'
        except Exception:
            tb = traceback.format_exc()
            res = 'FAIL'
            # Recommend: if expected module present in repo, recommend stub/port; else suggest manual port
            if expected:
                rec = f"Ensure module '{expected}' exists as pure-Python (create stub or port C)."
            else:
                rec = 'Investigate wrapper; may reference package-style implementation.'
        writer.writerow([str(p), expected, res, tb.replace('\n', '\\n'), rec])

print('Wrote', out_csv)
