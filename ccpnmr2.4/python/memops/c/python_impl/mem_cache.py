"""
Pure Python implementation of mem_cache.c

A thread-safe LRU cache with size limits and lock counts.
This implementation matches the C API for drop-in compatibility.
"""

import threading
from collections import OrderedDict
from typing import Callable, Optional, Any, Hashable


class CacheEntry:
    """Represents a cached object with metadata."""
    
    def __init__(self, obj: Any, size: int, 
                 delete_func: Optional[Callable] = None,
                 delete_data: Any = None):
        self.object = obj
        self.size = size
        self.delete_func = delete_func
        self.delete_data = delete_data
        self.lock_count = 0
    
    def lock(self):
        """Increment lock count (prevents eviction)."""
        self.lock_count += 1
    
    def unlock(self):
        """Decrement lock count."""
        self.lock_count = max(0, self.lock_count - 1)
    
    def is_locked(self) -> bool:
        """Check if entry is locked."""
        return self.lock_count > 0
    
    def cleanup(self):
        """Call delete function if provided."""
        if self.delete_func:
            self.delete_func(self.object, self.delete_data)


class MemCache:
    """
    Thread-safe LRU cache with size-based eviction.
    
    Matches the C implementation API:
    - new_mem_cache(max_size, equal_func, hash_func)
    - add_mem_cache(mem_cache, object, size, delete_func, delete_data)
    - remove_mem_cache(mem_cache, object)
    - lock_mem_cache(mem_cache, object)
    - unlock_mem_cache(mem_cache, object)
    - resize_mem_cache(mem_cache, max_size)
    - clear_mem_cache(mem_cache)
    - delete_mem_cache(mem_cache)
    """
    
    def __init__(self, max_size: int, 
                 equal_func: Optional[Callable] = None,
                 hash_func: Optional[Callable] = None):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum total size in bytes
            equal_func: Custom equality function (unused in Python, uses ==)
            hash_func: Custom hash function (unused in Python, uses hash())
        """
        self.max_size = max_size
        self.size = 0
        # OrderedDict provides LRU ordering
        self._cache: OrderedDict[Hashable, CacheEntry] = OrderedDict()
        self._mutex = threading.RLock()
    
    def add(self, obj: Any, size: int,
            delete_func: Optional[Callable] = None,
            delete_data: Any = None) -> bool:
        """
        Add object to cache (automatically locks it).
        
        Args:
            obj: Object to cache (must be hashable)
            size: Size in bytes
            delete_func: Optional cleanup function
            delete_data: Optional data for cleanup function
            
        Returns:
            True on success, False on error
        """
        with self._mutex:
            # Create entry
            entry = CacheEntry(obj, size, delete_func, delete_data)
            
            # Add to cache
            self._cache[obj] = entry
            self.size += size
            
            # Automatically lock when added
            entry.lock()
            
            # Make room if needed
            if self.size > self.max_size:
                self._make_room()
            
            return True
    
    def remove(self, obj: Any) -> bool:
        """
        Remove object from cache.
        
        Args:
            obj: Object to remove
            
        Returns:
            True on success, False if not found or locked
        """
        with self._mutex:
            entry = self._cache.get(obj)
            
            if entry and not entry.is_locked():
                del self._cache[obj]
                self.size -= entry.size
                entry.cleanup()
                return True
            
            return False
    
    def lock(self, obj: Any) -> bool:
        """
        Lock object and promote to front (most recently used).
        
        Args:
            obj: Object to lock
            
        Returns:
            True on success, False if not found
        """
        with self._mutex:
            if obj in self._cache:
                # Promote to end (most recently used in OrderedDict)
                self._cache.move_to_end(obj)
                self._cache[obj].lock()
                return True
            return False
    
    def unlock(self, obj: Any) -> bool:
        """
        Unlock object.
        
        Args:
            obj: Object to unlock
            
        Returns:
            True on success, False if not found
        """
        with self._mutex:
            if obj in self._cache:
                self._cache[obj].unlock()
                return True
            return False
    
    def resize(self, max_size: int) -> bool:
        """
        Change maximum cache size.
        
        Args:
            max_size: New maximum size in bytes
            
        Returns:
            True on success
        """
        with self._mutex:
            self.max_size = max_size
            if self.size > max_size:
                self._make_room()
            return True
    
    def clear(self):
        """Remove all entries from cache."""
        with self._mutex:
            for entry in self._cache.values():
                entry.cleanup()
            self._cache.clear()
            self.size = 0
    
    def delete(self):
        """Clean up and delete cache."""
        self.clear()
        # Mutex cleanup is automatic in Python
    
    def _make_room(self):
        """Evict unlocked entries until size <= 70% of max."""
        threshold = (7 * self.max_size) // 10
        
        # Iterate over items from oldest to newest
        # Must create list copy since we're modifying dict
        items_to_remove = []
        
        for obj, entry in list(self._cache.items()):
            if self.size <= threshold:
                break
            
            if not entry.is_locked():
                items_to_remove.append(obj)
        
        # Remove unlocked items
        for obj in items_to_remove:
            self.remove(obj)
    
    def check(self, error_msg: str = "") -> bool:
        """
        Debug function to check cache state.
        
        Args:
            error_msg: Optional error message
            
        Returns:
            True (for compatibility)
        """
        with self._mutex:
            print(f"check_mem_cache: {error_msg}")
            for obj, entry in self._cache.items():
                print(f"  Object {id(obj):x}: size={entry.size}, locks={entry.lock_count}")
        return True
    
    def get_stats(self) -> dict:
        """Get cache statistics (not in C API, but useful for testing)."""
        with self._mutex:
            return {
                'max_size': self.max_size,
                'current_size': self.size,
                'num_entries': len(self._cache),
                'locked_entries': sum(1 for e in self._cache.values() if e.is_locked())
            }


# C-style API functions for compatibility
def new_mem_cache(max_size: int, 
                  equal_func: Optional[Callable] = None,
                  hash_func: Optional[Callable] = None) -> MemCache:
    """Create a new memory cache."""
    return MemCache(max_size, equal_func, hash_func)


def delete_mem_cache(mem_cache: MemCache):
    """Delete a memory cache."""
    mem_cache.delete()


def clear_mem_cache(mem_cache: MemCache):
    """Clear all entries from cache."""
    mem_cache.clear()


def add_mem_cache(mem_cache: MemCache, obj: Any, size: int,
                  delete_func: Optional[Callable] = None,
                  delete_data: Any = None) -> bool:
    """Add object to cache."""
    return mem_cache.add(obj, size, delete_func, delete_data)


def remove_mem_cache(mem_cache: MemCache, obj: Any) -> bool:
    """Remove object from cache."""
    return mem_cache.remove(obj)


def lock_mem_cache(mem_cache: MemCache, obj: Any) -> bool:
    """Lock object in cache."""
    return mem_cache.lock(obj)


def unlock_mem_cache(mem_cache: MemCache, obj: Any) -> bool:
    """Unlock object in cache."""
    return mem_cache.unlock(obj)


def resize_mem_cache(mem_cache: MemCache, max_size: int) -> bool:
    """Resize cache."""
    return mem_cache.resize(max_size)


def check_mem_cache(mem_cache: MemCache, error_msg: str = "") -> bool:
    """Check cache state (debug)."""
    return mem_cache.check(error_msg)


# Export public API
__all__ = [
    'MemCache',
    'new_mem_cache',
    'delete_mem_cache',
    'clear_mem_cache',
    'add_mem_cache',
    'remove_mem_cache',
    'lock_mem_cache',
    'unlock_mem_cache',
    'resize_mem_cache',
    'check_mem_cache',
]
