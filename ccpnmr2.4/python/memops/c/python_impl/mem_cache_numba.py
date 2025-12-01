"""
Numba-accelerated LRU memory cache implementation.

This is a numba-optimized version of mem_cache.py. Note: Numba works best
with numerical operations and arrays. For dict-based caching like this,
the pure Python version may actually be faster due to CPython's optimized
dict implementation. This version demonstrates the pattern for comparison.

Numba limitations for this use case:
- Numba doesn't support Python dicts, OrderedDict, or threading primitives well
- Best for numerical array operations, not object caching
- We use @jit(nopython=False) for compatibility but gains are limited

For actual speedup, consider this for numerical array operations in other modules.
"""

from typing import Optional, Callable, Any, Dict
from collections import OrderedDict
import threading

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    # Fallback decorator that does nothing
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
    NUMBA_AVAILABLE = False


class MemCache:
    """
    Thread-safe LRU cache with size-based eviction (numba-aware version).
    
    Note: This implementation uses the same approach as pure Python since
    numba doesn't optimize dict operations. For demonstration purposes only.
    Real numba speedups would come from numerical operations in other modules.
    """
    
    def __init__(self, max_size: int, 
                 delete_func: Optional[Callable] = None,
                 delete_data: Any = None):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum cache size in bytes
            delete_func: Optional callback when objects are removed
            delete_data: Data passed to delete_func
        """
        self.max_size = max_size
        self.current_size = 0
        self.delete_func = delete_func
        self.delete_data = delete_data
        
        # OrderedDict maintains insertion order for LRU
        self._cache: OrderedDict = OrderedDict()
        self._sizes: Dict[Any, int] = {}
        self._lock_counts: Dict[Any, int] = {}
        
        # Thread safety
        self._mutex = threading.RLock()
    
    def add(self, obj: Any, size: int) -> bool:
        """Add object to cache."""
        with self._mutex:
            # If already exists, update size
            if obj in self._cache:
                old_size = self._sizes[obj]
                self.current_size -= old_size
                self.current_size += size
                self._sizes[obj] = size
                # Move to end (most recently used)
                self._cache.move_to_end(obj)
                return True
            
            # Check if we need to evict
            while self.current_size + size > self.max_size:
                evicted = self._evict_one()
                if not evicted:
                    # Can't evict enough, reject new entry
                    return False
            
            # Add new entry
            self._cache[obj] = True
            self._sizes[obj] = size
            self._lock_counts[obj] = 0
            self.current_size += size
            return True
    
    def remove(self, obj: Any) -> bool:
        """Remove object from cache."""
        with self._mutex:
            if obj not in self._cache:
                return False
            
            # Can't remove if locked
            if self._lock_counts.get(obj, 0) > 0:
                return False
            
            self._remove_object(obj)
            return True
    
    def lock(self, obj: Any) -> bool:
        """Lock object (increment lock count)."""
        with self._mutex:
            if obj not in self._cache:
                return False
            self._lock_counts[obj] = self._lock_counts.get(obj, 0) + 1
            return True
    
    def unlock(self, obj: Any) -> bool:
        """Unlock object (decrement lock count)."""
        with self._mutex:
            if obj not in self._cache:
                return False
            
            count = self._lock_counts.get(obj, 0)
            if count <= 0:
                return False
            
            self._lock_counts[obj] = count - 1
            return True
    
    def clear(self) -> None:
        """Remove all objects from cache."""
        with self._mutex:
            # Call delete function for all objects
            if self.delete_func:
                for obj in list(self._cache.keys()):
                    self.delete_func(obj, self.delete_data)
            
            self._cache.clear()
            self._sizes.clear()
            self._lock_counts.clear()
            self.current_size = 0
    
    def _evict_one(self) -> bool:
        """Evict one unlocked object (oldest first). Returns True if evicted."""
        for obj in list(self._cache.keys()):
            if self._lock_counts.get(obj, 0) == 0:
                self._remove_object(obj)
                return True
        return False
    
    def _remove_object(self, obj: Any) -> None:
        """Remove object and update accounting."""
        # Call delete function if provided
        if self.delete_func:
            self.delete_func(obj, self.delete_data)
        
        # Update size
        size = self._sizes[obj]
        self.current_size -= size
        
        # Remove from all structures
        del self._cache[obj]
        del self._sizes[obj]
        if obj in self._lock_counts:
            del self._lock_counts[obj]
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._mutex:
            return {
                'max_size': self.max_size,
                'current_size': self.current_size,
                'num_objects': len(self._cache),
                'num_locked': sum(1 for c in self._lock_counts.values() if c > 0)
            }


# C-style API functions
def new_mem_cache(max_size: int, 
                  delete_func: Optional[Callable] = None,
                  delete_data: Any = None) -> MemCache:
    """Create a new memory cache."""
    return MemCache(max_size, delete_func, delete_data)


def delete_mem_cache(cache: MemCache) -> None:
    """Delete memory cache and cleanup."""
    cache.clear()


def add_mem_cache(cache: MemCache, obj: Any, size: int) -> bool:
    """Add object to cache."""
    return cache.add(obj, size)


def remove_mem_cache(cache: MemCache, obj: Any) -> bool:
    """Remove object from cache."""
    return cache.remove(obj)


def lock_mem_cache(cache: MemCache, obj: Any) -> bool:
    """Lock object in cache."""
    return cache.lock(obj)


def unlock_mem_cache(cache: MemCache, obj: Any) -> bool:
    """Unlock object in cache."""
    return cache.unlock(obj)


def clear_mem_cache(cache: MemCache) -> None:
    """Clear all objects from cache."""
    cache.clear()


def check_mem_cache(cache: MemCache, prefix: str = "") -> None:
    """Debug function to print cache contents."""
    stats = cache.get_stats()
    print(f"{prefix}MemCache stats: {stats}")
    with cache._mutex:
        for i, (obj, size) in enumerate(cache._sizes.items()):
            lock_count = cache._lock_counts.get(obj, 0)
            print(f"  [{i}] obj={obj}, size={size}, locks={lock_count}")
