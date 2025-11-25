# Auto-generated wrapper for py_fit.c
# Loads package-style implementation found at: /Users/georgeelkins/nmr/ccpnmr2.4/ccpnmr2.4/python/memops/math/fit/fit.py
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
    _impl = importlib.import_module('memops.math.fit.fit')
except Exception as _e:
    raise ImportError(f"Failed to import implementation module 'memops.math.fit.fit': {_e}")

# Re-export public names
__all__ = [name for name in dir(_impl) if not name.startswith('_')]
for _name in __all__:
    globals()[_name] = getattr(_impl, _name)
