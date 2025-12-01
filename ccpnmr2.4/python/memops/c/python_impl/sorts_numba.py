"""
Numba-accelerated heap sort implementation.

Uses JIT compilation for high-performance sorting.
"""

from typing import List, TypeVar

try:
    from numba import jit
    import numpy as np
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]

T = TypeVar('T')


@jit(nopython=True)
def heap_sort_floats(arr, ascending=True):
    """
    Heap sort for float arrays (JIT-compiled).
    
    Args:
        arr: NumPy array of floats
        ascending: Sort direction
    
    Returns:
        Sorted array
    """
    # Work with a copy
    pointer = arr.copy()
    n = len(pointer)
    
    if n <= 1:
        return pointer
    
    # Comparison direction
    c = -1 if ascending else 1
    
    p = n // 2
    m = n - 1
    
    while m > 0:
        if p > 0:
            p -= 1
            ptr = pointer[p]
        else:
            ptr = pointer[m]
            pointer[m] = pointer[0]
            m -= 1
        
        i = p
        j = 2*p + 1
        
        while j < m:
            # Compare pointer[j] with pointer[j+1]
            if ascending:
                if pointer[j] < pointer[j+1]:
                    j += 1
            else:
                if pointer[j] > pointer[j+1]:
                    j += 1
            
            # Compare ptr with pointer[j]
            if ascending:
                if ptr < pointer[j]:
                    pointer[i] = pointer[j]
                    i = j
                    j = 2*i + 1
                else:
                    j = m + 1
            else:
                if ptr > pointer[j]:
                    pointer[i] = pointer[j]
                    i = j
                    j = 2*i + 1
                else:
                    j = m + 1
        
        if j == m:
            if ascending:
                if ptr < pointer[m]:
                    pointer[i] = pointer[m]
                    i = m
            else:
                if ptr > pointer[m]:
                    pointer[i] = pointer[m]
                    i = m
        
        pointer[i] = ptr
    
    return pointer


@jit(nopython=True)
def heap_sort_ints(arr, ascending=True):
    """
    Heap sort for integer arrays (JIT-compiled).
    
    Args:
        arr: NumPy array of ints
        ascending: Sort direction
    
    Returns:
        Sorted array
    """
    pointer = arr.copy()
    n = len(pointer)
    
    if n <= 1:
        return pointer
    
    c = -1 if ascending else 1
    p = n // 2
    m = n - 1
    
    while m > 0:
        if p > 0:
            p -= 1
            ptr = pointer[p]
        else:
            ptr = pointer[m]
            pointer[m] = pointer[0]
            m -= 1
        
        i = p
        j = 2*p + 1
        
        while j < m:
            if ascending:
                if pointer[j] < pointer[j+1]:
                    j += 1
            else:
                if pointer[j] > pointer[j+1]:
                    j += 1
            
            if ascending:
                if ptr < pointer[j]:
                    pointer[i] = pointer[j]
                    i = j
                    j = 2*i + 1
                else:
                    j = m + 1
            else:
                if ptr > pointer[j]:
                    pointer[i] = pointer[j]
                    i = j
                    j = 2*i + 1
                else:
                    j = m + 1
        
        if j == m:
            if ascending:
                if ptr < pointer[m]:
                    pointer[i] = pointer[m]
                    i = m
            else:
                if ptr > pointer[m]:
                    pointer[i] = pointer[m]
                    i = m
        
        pointer[i] = ptr
    
    return pointer


# High-level API
def heap_sort(items: List, ascending: bool = True):
    """
    Sort items using Numba-accelerated heap sort.
    
    Args:
        items: List of items to sort
        ascending: Sort direction
    
    Returns:
        Sorted list
    """
    if not NUMBA_AVAILABLE:
        # Fallback to Python's built-in sort
        result = items[:]
        result.sort(reverse=not ascending)
        return result
    
    # Convert to numpy array
    arr = np.array(items)
    
    # Choose appropriate sort based on type
    if arr.dtype == np.float32 or arr.dtype == np.float64:
        sorted_arr = heap_sort_floats(arr, ascending)
    elif arr.dtype == np.int32 or arr.dtype == np.int64:
        sorted_arr = heap_sort_ints(arr, ascending)
    else:
        # For other types, use float sort
        arr_float = arr.astype(np.float64)
        sorted_arr = heap_sort_floats(arr_float, ascending)
    
    return sorted_arr.tolist()


def sort_ascending(items: List):
    """Sort in ascending order."""
    return heap_sort(items, ascending=True)


def sort_descending(items: List):
    """Sort in descending order."""
    return heap_sort(items, ascending=False)
