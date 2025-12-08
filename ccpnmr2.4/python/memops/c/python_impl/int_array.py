"""
Integer array implementation - Python implementation of int_array.c

This module provides a fixed-size integer array data structure used as
a key in hash tables and for storing multi-dimensional indices.

Original: ccpnmr2.4/c/memops/global/int_array.c
Python: Simple class wrapping list/tuple with hash and equality

Note: Python tuples provide similar functionality and are generally preferred.
This class exists for compatibility with C code patterns.
"""

from typing import List, Optional
from .hash_table import array_hash


# Constants
MAX_NDIM = 16  # Maximum dimensions


# ============================================================================
# Integer Array Class
# ============================================================================

class IntArray:
    """Fixed-size integer array (like C struct).
    
    Used primarily as keys in hash tables and for multi-dimensional indices.
    
    Attributes:
        ndim: Number of dimensions
        values: List of integer values
    """
    
    def __init__(self, values: List[int]):
        """Create new integer array.
        
        Args:
            values: List of integer values
            
        Raises:
            ValueError: If too many dimensions
        """
        if len(values) > MAX_NDIM:
            raise ValueError(f"Too many dimensions: {len(values)} > {MAX_NDIM}")
        
        self.ndim = len(values)
        self.values = list(values)  # Make a copy
    
    def copy(self) -> 'IntArray':
        """Create a copy of this array.
        
        Returns:
            New IntArray with same values
        """
        return IntArray(self.values)
    
    def get(self, dim: int) -> int:
        """Get value at dimension.
        
        Args:
            dim: Dimension index (0-based)
            
        Returns:
            Value at dimension, or 0 if out of bounds
        """
        if 0 <= dim < self.ndim:
            return self.values[dim]
        return 0
    
    def set(self, dim: int, value: int):
        """Set value at dimension.
        
        Args:
            dim: Dimension index (0-based)
            value: Value to set
        """
        if 0 <= dim < self.ndim:
            self.values[dim] = value
    
    def __eq__(self, other) -> bool:
        """Check equality with another IntArray.
        
        Args:
            other: Another IntArray
            
        Returns:
            True if dimensions and values match
        """
        if not isinstance(other, IntArray):
            return False
        
        if self.ndim != other.ndim:
            return False
        
        return self.values == other.values
    
    def __hash__(self) -> int:
        """Compute hash value.
        
        Returns:
            Hash value based on array contents
        """
        return array_hash(self.values)
    
    def __len__(self) -> int:
        """Get number of dimensions."""
        return self.ndim
    
    def __getitem__(self, index: int) -> int:
        """Get value by index (enables arr[i])."""
        return self.get(index)
    
    def __setitem__(self, index: int, value: int):
        """Set value by index (enables arr[i] = value)."""
        self.set(index, value)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"IntArray({self.values})"
    
    def __str__(self) -> str:
        """Human-readable string."""
        return f"({', '.join(map(str, self.values))})"
    
    def to_tuple(self) -> tuple:
        """Convert to immutable tuple.
        
        Returns:
            Tuple of values
        """
        return tuple(self.values)
    
    def to_list(self) -> List[int]:
        """Convert to list.
        
        Returns:
            Copy of values as list
        """
        return list(self.values)


# ============================================================================
# Factory Functions
# ============================================================================

def new_int_array(values: List[int]) -> IntArray:
    """Create new integer array (C-style function).
    
    Args:
        values: List of integer values
        
    Returns:
        New IntArray
    """
    return IntArray(values)


def copy_int_array(int_array: IntArray) -> IntArray:
    """Copy integer array (C-style function).
    
    Args:
        int_array: Array to copy
        
    Returns:
        New copy of array
    """
    return int_array.copy()


def delete_int_array(int_array: IntArray):
    """Delete integer array (C-style function, no-op in Python).
    
    Args:
        int_array: Array to delete
    """
    pass  # Python handles memory automatically


def equal_int_array(arr1: IntArray, arr2: IntArray) -> bool:
    """Check if two arrays are equal (C-style function).
    
    Args:
        arr1: First array
        arr2: Second array
        
    Returns:
        True if arrays have same dimensions and values
    """
    return arr1 == arr2


def hash_int_array(int_array: IntArray) -> int:
    """Compute hash of integer array (C-style function).
    
    Args:
        int_array: Array to hash
        
    Returns:
        Hash value
    """
    return hash(int_array)


# Example usage
if __name__ == "__main__":
    # Create integer arrays
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([1, 2, 3])
    arr3 = IntArray([4, 5, 6])
    
    print(f"arr1: {arr1}")
    print(f"arr2: {arr2}")
    print(f"arr3: {arr3}")
    
    # Test equality
    print(f"\narr1 == arr2: {arr1 == arr2}")
    print(f"arr1 == arr3: {arr1 == arr3}")
    
    # Test hashing (same arrays have same hash)
    print(f"\nhash(arr1): {hash(arr1)}")
    print(f"hash(arr2): {hash(arr2)}")
    print(f"hash(arr3): {hash(arr3)}")
    
    # Test as dict key
    data = {arr1: "first", arr3: "third"}
    print(f"\nDict with IntArray keys:")
    print(f"  arr1 -> {data[arr1]}")
    print(f"  arr2 -> {data[arr2]}")
    # Should work (arr2 == arr1)
    print(f"  arr3 -> {data[arr3]}")
    
    # Test indexing
    print(f"\narr1[0] = {arr1[0]}")
    arr1[1] = 99
    print(f"After arr1[1] = 99: {arr1}")
    
    # Copy
    arr4 = arr1.copy()
    arr4[0] = 100
    print(f"\nOriginal arr1: {arr1}")
    print(f"Modified copy: {arr4}")
