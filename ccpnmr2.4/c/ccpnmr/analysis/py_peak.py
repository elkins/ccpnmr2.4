# Auto-generated wrapper for py_peak.c
# Loads the pure-Python implementation from python_impl package
import importlib.util
import importlib.machinery
import sys
import os

# Calculate path relative to this wrapper file
_wrapper_dir = os.path.dirname(os.path.abspath(__file__))
_impl_path = os.path.normpath(os.path.join(_wrapper_dir, '..', '..', '..', 'python', 'ccpnmr', 'analysis', 'python_impl', 'peak.py'))
_spec = importlib.util.spec_from_file_location('peak_impl_auto', _impl_path)
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

# Re-export public names from implementation
__all__ = [name for name in dir(_impl) if not name.startswith('_')]
for _name in __all__:
    globals()[_name] = getattr(_impl, _name)
