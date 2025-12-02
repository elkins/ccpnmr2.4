"""
======================COPYRIGHT/LICENSE START==========================

list.py: Part of the CcpNmr Analysis program

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

Python implementation of generic linked list functionality.

This replaces the C implementation with Python's built-in list, which is
more efficient due to better cache locality from contiguous memory storage.
"""

from typing import Any, Callable, Optional, List as ListType


class CcpnList:
    """Generic list data structure wrapping Python's built-in list.
    
    Provides a C-compatible API while using Python's optimized list
    implementation internally. Python lists are faster than linked lists
    for most operations due to better cache locality.
    """
    
    def __init__(self):
        """Initialize an empty list."""
        self._data: ListType[Any] = []
    
    def is_empty(self) -> bool:
        """Check if the list is empty.
        
        Returns:
            True if list has no elements, False otherwise
        """
        return len(self._data) == 0
    
    def insert(self, data: Any) -> None:
        """Insert data at the front of the list (prepend).
        
        Args:
            data: The data to insert
        """
        self._data.insert(0, data)
    
    def append(self, data: Any) -> None:
        """Append data to the end of the list.
        
        Args:
            data: The data to append
        """
        self._data.append(data)
    
    def delete_key(self, key: Any) -> bool:
        """Delete the first occurrence of key from the list.
        
        Args:
            key: The key to delete
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        try:
            self._data.remove(key)
            return True
        except ValueError:
            return False
    
    def delete_front(self) -> Optional[Any]:
        """Remove and return the first element.
        
        Returns:
            The first element, or None if list is empty
        """
        if self.is_empty():
            return None
        return self._data.pop(0)
    
    def traverse(self, func: Callable[[Any], None]) -> None:
        """Traverse the list and apply a function to each element.
        
        Args:
            func: Function to apply to each element
        """
        for item in self._data:
            func(item)
    
    def find_key(self, key: Any, cmp_func: Optional[Callable[[Any, Any], bool]] = None) -> Optional[Any]:
        """Find an element in the list using a comparison function.
        
        Args:
            key: The key to search for
            cmp_func: Optional comparison function. If None, uses equality.
                     Should return True if the two arguments match.
            
        Returns:
            The matching element, or None if not found
        """
        if cmp_func is None:
            cmp_func = lambda k, item: k == item
        
        for item in self._data:
            if cmp_func(key, item):
                return item
        return None
    
    def destroy(self, cleanup_func: Optional[Callable[[Any], None]] = None) -> None:
        """Destroy the list and optionally clean up each element.
        
        Args:
            cleanup_func: Optional function to call on each element before destruction
        """
        if cleanup_func is not None:
            for item in self._data:
                cleanup_func(item)
        self._data.clear()
    
    def __len__(self) -> int:
        """Get the number of elements in the list."""
        return len(self._data)
    
    def __iter__(self):
        """Return an iterator over the list elements."""
        return iter(self._data)
    
    def __contains__(self, item: Any) -> bool:
        """Check if an item is in the list."""
        return item in self._data
    
    def __getitem__(self, index: int) -> Any:
        """Get an element by index."""
        return self._data[index]
    
    def __repr__(self) -> str:
        """Return a string representation of the list."""
        return f"CcpnList({self._data!r})"


# C-compatible function interface
def init_list() -> CcpnList:
    """Create and initialize a new list.
    
    Returns:
        A new CcpnList instance
    """
    return CcpnList()


def empty_list(lst: CcpnList) -> bool:
    """Check if a list is empty.
    
    Args:
        lst: The list to check
        
    Returns:
        True if empty, False otherwise
    """
    return lst.is_empty()


def insert_list(lst: CcpnList, data: Any) -> None:
    """Insert data at the front of the list.
    
    Args:
        lst: The list to insert into
        data: The data to insert
    """
    lst.insert(data)


def append_list(lst: CcpnList, data: Any) -> None:
    """Append data to the end of the list.
    
    Args:
        lst: The list to append to
        data: The data to append
    """
    lst.append(data)


def delete_key(lst: CcpnList, key: Any) -> bool:
    """Delete the first occurrence of a key.
    
    Args:
        lst: The list to delete from
        key: The key to delete
        
    Returns:
        True if key was found and deleted, False otherwise
    """
    return lst.delete_key(key)


def delete_list(lst: CcpnList) -> Optional[Any]:
    """Remove and return the first element.
    
    Args:
        lst: The list to delete from
        
    Returns:
        The first element, or None if empty
    """
    return lst.delete_front()


def traverse_list(lst: CcpnList, func: Callable[[Any], None]) -> None:
    """Traverse the list and apply a function to each element.
    
    Args:
        lst: The list to traverse
        func: Function to apply to each element
    """
    lst.traverse(func)


def find_key(lst: CcpnList, key: Any, cmp_func: Optional[Callable[[Any, Any], bool]] = None) -> Optional[Any]:
    """Find an element using a comparison function.
    
    Args:
        lst: The list to search
        key: The key to search for
        cmp_func: Optional comparison function
        
    Returns:
        The matching element, or None if not found
    """
    return lst.find_key(key, cmp_func)


def destroy_list(lst: CcpnList, cleanup_func: Optional[Callable[[Any], None]] = None) -> None:
    """Destroy the list and optionally clean up elements.
    
    Args:
        lst: The list to destroy
        cleanup_func: Optional cleanup function
    """
    lst.destroy(cleanup_func)
