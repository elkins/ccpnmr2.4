"""
Python wrapper for store_handler - mimics C extension interface.

This module provides a Python-based implementation of the StoreHandler
C extension module, allowing it to be used as a drop-in replacement
for the compiled C extension.

Module: py_store_handler
Original: ccpnmr2.4/c/memops/global/py_store_handler.c (251 lines)
Purpose: Python C extension wrapper for store_handler
"""

from typing import Optional
from .store_handler import StoreHandler as PythonStoreHandler


class StoreHandlerWrapper:
    """
    Wrapper class that mimics the C extension interface.
    
    This provides the same interface as the C extension, allowing code
    written for the C extension to work with the pure Python implementation.
    
    The C extension has minimal functionality - it just wraps the StoreHandler
    object without exposing additional attributes or methods beyond those
    in the core implementation.
    """
    
    def __init__(self, file_name: str, swap: bool = False):
        """
        Initialize store handler for writing.
        
        Args:
            file_name: Path to output file
            swap: Whether to byte-swap data (for cross-platform compatibility)
            
        Raises:
            IOError: If file cannot be created
        """
        self._store_handler = PythonStoreHandler(file_name, swap)
    
    def __getattr__(self, name: str):
        """
        Forward attribute access to underlying store handler.
        
        This allows the wrapper to transparently expose all methods and
        attributes of the underlying StoreHandler implementation.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute value from underlying handler
            
        Raises:
            AttributeError: If attribute doesn't exist
        """
        return getattr(self._store_handler, name)
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, '_store_handler') and hasattr(self._store_handler, 'fp'):
            if self._store_handler.fp and not self._store_handler.fp.closed:
                self._store_handler.close()


def StoreHandler(file_name: str, swap: bool = False) -> StoreHandlerWrapper:
    """
    Create store handler for writing (mimics C extension factory function).
    
    This function provides the same interface as the C extension's
    StoreHandler factory function, making it a drop-in replacement.
    
    Args:
        file_name: Path to output file
        swap: Whether to byte-swap data (default: False)
        
    Returns:
        StoreHandlerWrapper instance
        
    Raises:
        IOError: If file cannot be created
        
    Example:
        >>> handler = StoreHandler("contours.dat")
        >>> handler.init_store_save(2, 0, 1, npoints, first, last,
        ...                         block_size, nblocks, 1, levels)
        >>> handler.init_store_block([0, 0])
        >>> handler.init_store_plane([0, 0])
        >>> handler.init_store_level(1.0)
        >>> handler.draw_polyline(vertices)
        >>> handler.end_store_plane()
        >>> handler.end_store_save()
    """
    return StoreHandlerWrapper(file_name, swap)


# Module-level error class (mimics C extension)
class error(Exception):
    """StoreHandler module error."""
    pass


# Module initialization
def __getattr__(name: str):
    """
    Handle dynamic attribute access.
    
    This allows the module to mimic the C extension's attribute access
    patterns while providing pure Python implementations.
    
    Args:
        name: Attribute name
        
    Returns:
        Attribute value
        
    Raises:
        AttributeError: If attribute doesn't exist
    """
    if name == "error":
        return error
    raise AttributeError(f"module 'py_store_handler' has no attribute '{name}'")


# For backwards compatibility with code that imports the C extension
__all__ = ['StoreHandler', 'StoreHandlerWrapper', 'error']
