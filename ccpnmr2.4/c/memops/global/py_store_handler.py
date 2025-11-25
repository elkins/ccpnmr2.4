# Auto-generated wrapper for py_store_handler.c
# Loads the pure-Python implementation found at: /Users/georgeelkins/nmr/ccpnmr2.4/store_handler.py
import importlib.util
import importlib.machinery
import sys
import os

_impl_path = os.path.normpath(r'''/Users/georgeelkins/nmr/ccpnmr2.4/store_handler.py''')
_spec = importlib.util.spec_from_file_location('store_handler_impl_auto', _impl_path)
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)

# Re-export public names from implementation
__all__ = [name for name in dir(_impl) if not name.startswith('_')]
for _name in __all__:
    globals()[_name] = getattr(_impl, _name)
