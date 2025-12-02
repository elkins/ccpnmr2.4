"""
======================COPYRIGHT/LICENSE START==========================

hash_list.py: Part of the CcpNmr Analysis program

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

Python implementation of hash-list hybrid data structure.

This combines a hash table (for O(1) lookup) with a doubly-linked list
(for maintaining insertion order and supporting priority operations).

The Python implementation uses a dict for the hash table and a collections.OrderedDict
or custom list for ordering, which is faster than the C linked list implementation.
"""

from typing import Any, Callable, Optional, Dict, Tuple
from collections import OrderedDict


class HashList:
    """Hybrid hash table + doubly-linked list data structure.
    
    Provides O(1) lookup by key while maintaining insertion order.
    Supports promote/demote operations for LRU-style caching.
    
    This Python implementation is faster than the C version because:
    - Python's dict is implemented in C with optimized hashing
    - OrderedDict provides O(1) move-to-end operations
    - Better memory layout and cache efficiency
    """
    
    def __init__(self, equal_func: Optional[Callable[[Any, Any], bool]] = None,
                 hash_func: Optional[Callable[[Any], int]] = None):
        """Initialize a new hash-list.
        
        Args:
            equal_func: Optional custom equality function. If None, uses ==.
            hash_func: Optional custom hash function. If None, uses hash().
        """
        # Use OrderedDict to maintain insertion order while providing O(1) lookup
        self._data: OrderedDict[Any, Any] = OrderedDict()
        self._equal_func = equal_func if equal_func is not None else lambda a, b: a == b
        self._hash_func = hash_func if hash_func is not None else hash
        
        # For custom hash functions, we need a mapping from custom keys to actual keys
        self._key_map: Optional[Dict[int, Any]] = {} if hash_func is not None else None
    
    def is_empty(self) -> bool:
        """Check if the hash-list is empty."""
        return len(self._data) == 0
    
    def insert(self, key: Any, data: Any) -> bool:
        """Insert a key-data pair at the front of the list.
        
        Args:
            key: The key for lookup
            data: The associated data
            
        Returns:
            True on success, False on failure
        """
        if key in self._data:
            # Key already exists, don't insert duplicate
            return False
        
        # Insert and move to front
        self._data[key] = data
        self._data.move_to_end(key, last=False)
        
        if self._key_map is not None:
            custom_hash = self._hash_func(key)
            self._key_map[custom_hash] = key
        
        return True
    
    def append(self, key: Any, data: Any) -> bool:
        """Append a key-data pair to the end of the list.
        
        Args:
            key: The key for lookup
            data: The associated data
            
        Returns:
            True on success, False on failure
        """
        if key in self._data:
            # Key already exists, don't insert duplicate
            return False
        
        self._data[key] = data
        
        if self._key_map is not None:
            custom_hash = self._hash_func(key)
            self._key_map[custom_hash] = key
        
        return True
    
    def find_key(self, key: Any) -> Optional[Any]:
        """Find data associated with a key.
        
        Args:
            key: The key to search for
            
        Returns:
            The associated data, or None if not found
        """
        return self._data.get(key, None)
    
    def remove_key(self, key: Any) -> Optional[Any]:
        """Remove and return data associated with a key.
        
        Args:
            key: The key to remove
            
        Returns:
            The associated data, or None if not found
        """
        if key not in self._data:
            return None
        
        data = self._data.pop(key)
        
        if self._key_map is not None:
            custom_hash = self._hash_func(key)
            self._key_map.pop(custom_hash, None)
        
        return data
    
    def remove_first(self) -> Optional[Tuple[Any, Any]]:
        """Remove and return the first (key, data) pair.
        
        Returns:
            Tuple of (key, data), or None if empty
        """
        if self.is_empty():
            return None
        
        key, data = self._data.popitem(last=False)
        
        if self._key_map is not None:
            custom_hash = self._hash_func(key)
            self._key_map.pop(custom_hash, None)
        
        return (key, data)
    
    def remove_last(self) -> Optional[Tuple[Any, Any]]:
        """Remove and return the last (key, data) pair.
        
        Returns:
            Tuple of (key, data), or None if empty
        """
        if self.is_empty():
            return None
        
        key, data = self._data.popitem(last=True)
        
        if self._key_map is not None:
            custom_hash = self._hash_func(key)
            self._key_map.pop(custom_hash, None)
        
        return (key, data)
    
    def promote(self, key: Any) -> Optional[Any]:
        """Move a key to the front of the list (most recently used).
        
        This is useful for LRU cache implementations.
        
        Args:
            key: The key to promote
            
        Returns:
            The associated data, or None if key not found
        """
        if key not in self._data:
            return None
        
        self._data.move_to_end(key, last=False)
        return self._data[key]
    
    def demote(self, key: Any) -> Optional[Any]:
        """Move a key to the end of the list (least recently used).
        
        This is useful for LRU cache implementations.
        
        Args:
            key: The key to demote
            
        Returns:
            The associated data, or None if key not found
        """
        if key not in self._data:
            return None
        
        self._data.move_to_end(key, last=True)
        return self._data[key]
    
    def traverse(self, func: Callable[[Any, Optional[Any]], Tuple[bool, bool]], 
                 forward: bool = True, user_data: Any = None) -> bool:
        """Traverse the list and apply a function to each element.
        
        Args:
            func: Function to call for each element. Should return (status, done).
                 If done is True, traversal stops.
            forward: If True, traverse from first to last; if False, reverse
            user_data: Optional user data passed to func
            
        Returns:
            True if traversal completed successfully, False on error
        """
        items = list(self._data.items())
        if not forward:
            items = reversed(items)
        
        for key, data in items:
            try:
                status, done = func(data, user_data)
                if not status:
                    return False
                if done:
                    break
            except Exception:
                return False
        
        return True
    
    def clear(self, cleanup_func: Optional[Callable[[Any], None]] = None) -> None:
        """Clear all entries from the hash-list.
        
        Args:
            cleanup_func: Optional function to call on each data element before clearing
        """
        if cleanup_func is not None:
            for data in self._data.values():
                cleanup_func(data)
        
        self._data.clear()
        if self._key_map is not None:
            self._key_map.clear()
    
    def __len__(self) -> int:
        """Return the number of elements."""
        return len(self._data)
    
    def __contains__(self, key: Any) -> bool:
        """Check if a key exists."""
        return key in self._data
    
    def __iter__(self):
        """Iterate over keys in order."""
        return iter(self._data)
    
    def keys(self):
        """Return an iterator over keys."""
        return self._data.keys()
    
    def values(self):
        """Return an iterator over values."""
        return self._data.values()
    
    def items(self):
        """Return an iterator over (key, data) pairs."""
        return self._data.items()
    
    def __repr__(self) -> str:
        """Return string representation."""
        return f"HashList({len(self._data)} items)"


# C-compatible function interface
def new_hash_list(equal_func: Optional[Callable[[Any, Any], bool]] = None,
                  hash_func: Optional[Callable[[Any], int]] = None) -> HashList:
    """Create a new hash-list.
    
    Args:
        equal_func: Optional custom equality function
        hash_func: Optional custom hash function
        
    Returns:
        A new HashList instance
    """
    return HashList(equal_func, hash_func)


def delete_hash_list(hash_list: HashList, cleanup_func: Optional[Callable[[Any], None]] = None) -> None:
    """Delete a hash-list and optionally clean up data.
    
    Args:
        hash_list: The hash-list to delete
        cleanup_func: Optional cleanup function for data elements
    """
    hash_list.clear(cleanup_func)


def clear_hash_list(hash_list: HashList, cleanup_func: Optional[Callable[[Any], None]] = None) -> None:
    """Clear all entries from a hash-list.
    
    Args:
        hash_list: The hash-list to clear
        cleanup_func: Optional cleanup function
    """
    hash_list.clear(cleanup_func)


def empty_hash_list(hash_list: HashList) -> bool:
    """Check if a hash-list is empty.
    
    Args:
        hash_list: The hash-list to check
        
    Returns:
        True if empty, False otherwise
    """
    return hash_list.is_empty()


def insert_hash_list(hash_list: HashList, key: Any, data: Any) -> bool:
    """Insert at the front of the hash-list.
    
    Args:
        hash_list: The hash-list
        key: The key
        data: The data
        
    Returns:
        True on success, False on failure
    """
    return hash_list.insert(key, data)


def append_hash_list(hash_list: HashList, key: Any, data: Any) -> bool:
    """Append to the end of the hash-list.
    
    Args:
        hash_list: The hash-list
        key: The key
        data: The data
        
    Returns:
        True on success, False on failure
    """
    return hash_list.append(key, data)


def find_key_hash_list(hash_list: HashList, key: Any) -> Optional[Any]:
    """Find data by key.
    
    Args:
        hash_list: The hash-list
        key: The key to find
        
    Returns:
        The data, or None if not found
    """
    return hash_list.find_key(key)


def remove_key_hash_list(hash_list: HashList, key: Any) -> Optional[Any]:
    """Remove and return data by key.
    
    Args:
        hash_list: The hash-list
        key: The key to remove
        
    Returns:
        The data, or None if not found
    """
    return hash_list.remove_key(key)


def remove_first_hash_list(hash_list: HashList) -> Optional[Tuple[Any, Any]]:
    """Remove and return the first entry.
    
    Args:
        hash_list: The hash-list
        
    Returns:
        Tuple of (key, data), or None if empty
    """
    return hash_list.remove_first()


def remove_last_hash_list(hash_list: HashList) -> Optional[Tuple[Any, Any]]:
    """Remove and return the last entry.
    
    Args:
        hash_list: The hash-list
        
    Returns:
        Tuple of (key, data), or None if empty
    """
    return hash_list.remove_last()


def promote_hash_list(hash_list: HashList, key: Any) -> Optional[Any]:
    """Promote a key to the front (most recently used).
    
    Args:
        hash_list: The hash-list
        key: The key to promote
        
    Returns:
        The data, or None if not found
    """
    return hash_list.promote(key)


def demote_hash_list(hash_list: HashList, key: Any) -> Optional[Any]:
    """Demote a key to the end (least recently used).
    
    Args:
        hash_list: The hash-list
        key: The key to demote
        
    Returns:
        The data, or None if not found
    """
    return hash_list.demote(key)


def traverse_hash_list(hash_list: HashList, forward: bool,
                      func: Callable[[Any, Optional[Any]], Tuple[bool, bool]],
                      user_data: Any = None) -> bool:
    """Traverse the hash-list.
    
    Args:
        hash_list: The hash-list
        forward: Direction (True = forward, False = reverse)
        func: Function to call for each element
        user_data: Optional user data
        
    Returns:
        True on success, False on error
    """
    return hash_list.traverse(func, forward, user_data)
