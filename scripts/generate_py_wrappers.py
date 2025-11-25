"""
Scan repository for `py_*.c` wrapper files and generate Python replacements `py_*.py` next to them.
Strategy for each `py_*.c`:
 - target = filename without 'py_' prefix and without '.c'
 - search the repo for a pure-Python file named `target.py`
 - if found: generate a wrapper that dynamically imports that file and re-exports its public symbols
 - elif not found: generate a wrapper that tries to import a compiled extension module named `target` and re-exports it
 - else: generate a module that raises ImportError with clear instructions

Run this script from the repo root.
"""
import os
import fnmatch
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

py_c_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if fnmatch.fnmatch(fn, 'py_*.c'):
            py_c_files.append(Path(dirpath) / fn)

print(f"Found {len(py_c_files)} py_*.c files")

for cpath in py_c_files:
    base = cpath.stem  # py_whatever
    if not base.startswith('py_'):
        continue
    target = base[3:]
    wrapper_path = cpath.with_suffix('.py')

    # Search for potential Python implementation files named target.py
    impl_matches = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            if fn == f"{target}.py":
                impl_matches.append(Path(dirpath) / fn)

    if impl_matches:
        impl_path = impl_matches[0]
        # Try to construct a package import that will work when the project's `python/`
        # directory is placed on sys.path. If the implementation file lives under a
        # top-level `python/` directory, compute the dotted module name from the
        # path after `python/`.
        parts = list(impl_path.parts)
        dotted = None
        if 'python' in parts:
            idx = parts.index('python')
            module_parts = parts[idx+1:]
            # turn last filename into module name without .py
            module_parts[-1] = module_parts[-1].rsplit('.', 1)[0]
            dotted = '.'.join(module_parts)

        if dotted:
            # generate wrapper that inserts the repo `python` dir into sys.path
            content = f"""# Auto-generated wrapper for {cpath.name}
# Loads package-style implementation found at: {impl_path}
import importlib
import sys
import os

# Locate nearest ancestor containing a `python` directory and add it to sys.path
_here = os.path.dirname(__file__)
_cur = _here
_python_dir = None
while True:
    candidate = os.path.join(_cur, 'python')
    if os.path.isdir(candidate):
        _python_dir = os.path.normpath(candidate)
        break
    parent = os.path.dirname(_cur)
    if parent == _cur:
        break
    _cur = parent
if _python_dir and _python_dir not in sys.path:
    sys.path.insert(0, _python_dir)

try:
    _impl = importlib.import_module('{dotted}')
except Exception as _e:
    raise ImportError(f"Failed to import implementation module '{dotted}': {{_e}}")

# Re-export public names
__all__ = [name for name in dir(_impl) if not name.startswith('_')]
for _name in __all__:
    globals()[_name] = getattr(_impl, _name)
"""
        else:
            # Fallback to file-loader if package import not detected
            impl_path = impl_matches[0]
            content = f"""# Auto-generated wrapper for {cpath.name}
# Loads the pure-Python implementation found at: {impl_path}
import importlib.util
import importlib.machinery
import sys
import os

_impl_path = os.path.normpath(r'''{impl_path}''')
_spec = importlib.util.spec_from_file_location('{target}_impl_auto', _impl_path)
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

# Re-export public names from implementation
__all__ = [name for name in dir(_impl) if not name.startswith('_')]
for _name in __all__:
    globals()[_name] = getattr(_impl, _name)
"""
    else:
        # No pure-Python implementation found; generate fallback that prefers repo-level
        # pure-Python stubs, then tries the compiled module.
        # Embed the repository root path so wrapper will search it first at runtime.
        content = f"""# Auto-generated wrapper for {cpath.name}
# No pure-Python implementation found for '{target}'.
# Prefer any repo-level stub module, then fall back to compiled extension '{target}'.
import sys
import os
import importlib

# Ensure the repository root is on sys.path so top-level stubs are importable
_repo_root = os.path.normpath(r'''{ROOT}''')
if _repo_root and _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

try:
    # First try a normal import of the target (this will pick up a stub `target.py` at repo root)
    _mod = importlib.import_module('{target}')
    # Re-export public names
    __all__ = [name for name in dir(_mod) if not name.startswith('_')]
    for _name in __all__:
        globals()[_name] = getattr(_mod, _name)
except Exception:
    # Fall back to compiled extension (or raise original error)
    try:
        from {target} import *
        __all__ = [name for name in globals() if not name.startswith('_')]
    except Exception as _e:
        raise ImportError(
            "No pure-Python implementation found for '{target}', and importing the compiled extension failed: "
            + str(_e)
        )
"""

    # Write the wrapper file if not exists or if content differs
    write = True
    if wrapper_path.exists():
        existing = wrapper_path.read_text()
        if existing == content:
            write = False
    if write:
        wrapper_path.write_text(content)
        print(f"Wrote wrapper: {wrapper_path} -> impl: {impl_matches[0] if impl_matches else 'compiled:'+target}")
    else:
        print(f"Unchanged: {wrapper_path}")

print("Done.")
