"""
Pure Python implementation of heap sort.

Custom heap sort implementation for sorting with comparison functions.
"""

from typing import List, Callable, Any, TypeVar

T = TypeVar('T')


def heap_sort(items: List[T], ascending: bool = True, 
              key: Callable[[T], Any] = None) -> List[T]:
    """
    Sort items using heap sort algorithm.
    
    Args:
        items: List of items to sort
        ascending: If True, sort in ascending order; otherwise descending
        key: Optional key function for comparison
    
    Returns:
        Sorted list (sorts in-place and returns reference)
    """
    # Make a copy to avoid modifying original
    pointer = items[:]
    n = len(pointer)
    
    if n <= 1:
        return pointer
    
    # Define comparison function
    if key is None:
        def cmp_func(a, b):
            if a < b:
                return -1
            elif a > b:
                return 1
            return 0
    else:
        def cmp_func(a, b):
            ka, kb = key(a), key(b)
            if ka < kb:
                return -1
            elif ka > kb:
                return 1
            return 0
    
    # Set comparison direction
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
            if cmp_func(pointer[j], pointer[j+1]) == c:
                j += 1
            
            if cmp_func(ptr, pointer[j]) == c:
                pointer[i] = pointer[j]
                i = j
                j = 2*i + 1
            else:
                j = m + 1
        
        if (j == m) and (cmp_func(ptr, pointer[m]) == c):
            pointer[i] = pointer[m]
            i = m
        
        pointer[i] = ptr
    
    return pointer


def heap_sort_with_indices(items: List[T], ascending: bool = True) -> List[int]:
    """
    Sort items and return indices of sorted order.
    
    Args:
        items: List of items to sort
        ascending: If True, sort in ascending order
    
    Returns:
        List of indices representing sorted order
    """
    # Create list of (index, value) pairs
    indexed = list(enumerate(items))
    
    # Sort by value
    sorted_indexed = heap_sort(indexed, ascending=ascending, key=lambda x: x[1])
    
    # Extract indices
    return [idx for idx, val in sorted_indexed]


# C-style API for compatibility
def sort_ascending(items: List[T]) -> List[T]:
    """Sort in ascending order."""
    return heap_sort(items, ascending=True)


def sort_descending(items: List[T]) -> List[T]:
    """Sort in descending order."""
    return heap_sort(items, ascending=False)
