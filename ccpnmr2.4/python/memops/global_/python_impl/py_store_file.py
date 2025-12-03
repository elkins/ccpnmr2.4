"""
Python wrapper for store_file - mimics C extension interface.

This module provides a Python-based implementation of the StoreFile
C extension module, allowing it to be used as a drop-in replacement
for the compiled C extension.

Module: py_store_file
Original: ccpnmr2.4/c/memops/global/py_store_file.c (266 lines)
Purpose: Python C extension wrapper for store_file
"""

from typing import Optional, Any, Callable, Sequence
import numpy as np

from .store_file import StoreFile as PythonStoreFile, StorePolyFunc


class StoreFileWrapper:
    """
    Wrapper class that mimics the C extension interface.
    
    This provides the same attribute access patterns as the C extension,
    allowing code written for the C extension to work with the pure Python
    implementation.
    
    Attributes:
        have_pos: Whether file contains positive contours
        have_neg: Whether file contains negative contours
        dir_size: Size of directory array
    """
    
    def __init__(self, file_name: str, ndim: int, xdim: int, ydim: int,
                 block_size: Sequence[int]):
        """
        Initialize store file reader.
        
        Args:
            file_name: Path to storage file
            ndim: Number of dimensions
            xdim: Display dimension index (x)
            ydim: Display dimension index (y)
            block_size: Block size for each dimension
            
        Raises:
            IOError: If file cannot be opened
            ValueError: If file format is invalid
        """
        # Convert block_size to numpy array if needed
        if not isinstance(block_size, np.ndarray):
            block_size = np.array(block_size, dtype=np.int32)
        
        # Create the underlying store file
        self._store_file = PythonStoreFile(file_name, ndim, xdim, ydim, block_size)
    
    @property
    def have_pos(self) -> bool:
        """Whether file contains positive contours."""
        return bool(self._store_file.have_pos)
    
    @property
    def have_neg(self) -> bool:
        """Whether file contains negative contours."""
        return bool(self._store_file.have_neg)
    
    @property
    def dir_size(self) -> int:
        """Size of directory array."""
        return int(self._store_file.dir_size)
    
    def process_contours(self, block: Sequence[int], plane: Sequence[int],
                        poly_func: StorePolyFunc, user_data: Any = None,
                        transposed: bool = False) -> bool:
        """
        Process contours for given block and plane.
        
        Args:
            block: Block indices
            plane: Plane indices
            poly_func: Callback function for polylines
            user_data: User data passed to callback
            transposed: Whether to transpose coordinates
            
        Returns:
            True if successful
        """
        # Convert to numpy arrays if needed
        if not isinstance(block, np.ndarray):
            block = np.array(block, dtype=np.int32)
        if not isinstance(plane, np.ndarray):
            plane = np.array(plane, dtype=np.int32)
        
        return self._store_file.process_contours(block, plane, poly_func,
                                                 user_data, transposed)
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, '_store_file'):
            self._store_file.close()


def StoreFile(file_name: str, ndim: int, xdim: int, ydim: int,
              block_size: Sequence[int]) -> StoreFileWrapper:
    """
    Create store file reader (mimics C extension factory function).
    
    This function provides the same interface as the C extension's
    StoreFile factory function, making it a drop-in replacement.
    
    Args:
        file_name: Path to storage file
        ndim: Number of dimensions
        xdim: Display dimension index (x)
        ydim: Display dimension index (y)
        block_size: Block size for each dimension
        
    Returns:
        StoreFileWrapper instance
        
    Raises:
        IOError: If file cannot be opened
        ValueError: If file format is invalid
        
    Example:
        >>> store = StoreFile("contours.dat", 2, 0, 1, [100, 100])
        >>> print(store.have_pos, store.have_neg)
        True False
    """
    return StoreFileWrapper(file_name, ndim, xdim, ydim, block_size)


# Module-level error class (mimics C extension)
class error(Exception):
    """StoreFile module error."""
    pass


# Module initialization
def __getattr__(name: str) -> Any:
    """
    Handle dynamic attribute access.
    
    This allows the module to mimic the C extension's attribute access
    patterns while providing pure Python implementations.
    """
    if name == "error":
        return error
    raise AttributeError(f"module 'py_store_file' has no attribute '{name}'")


# For backwards compatibility with code that imports the C extension
__all__ = ['StoreFile', 'StoreFileWrapper', 'error']
