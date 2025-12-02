"""
Hash table implementation - Python implementation of hash_table.c

This module provides a hash table data structure with:
- Dynamic resizing (grows when full, shrinks when sparse)
- Custom hash and equality functions
- Collision resolution via linear probing
- Iteration and clearing operations

Original: ccpnmr2.4/c/memops/global/hash_table.c
Python: Uses dict as base with custom hashing when needed

Note: Python's built-in dict is generally faster and more robust than this
implementation. This exists for compatibility with C code and for cases
where custom hash/equality functions are needed.
"""

from typing import Any, Callable, Optional, Tuple, List


# Type aliases
HashKey = Any
HashData = Any
HashValue = int
EqualFunc = Callable[[HashKey, HashKey], bool]
HashFunc = Callable[[HashKey], HashValue]
HashClearFunc = Callable[[HashKey, HashData, Any], None]
HashIterFunc = Callable[[HashKey, HashData, Any], bool]


# Constants
TABLE_INITIAL_SIZE = 931
GROW_FACTOR = 2
RESIZE_FACTOR = 3
SHRINK_FACTOR = 64
HASH_MASK = (1 << 30) - 1


# ============================================================================
# Hash Functions
# ============================================================================

def combine_hash(hash1: HashValue, hash2: HashValue) -> HashValue:
    """Combine two hash values.
    
    Args:
        hash1: First hash value
        hash2: Second hash value
        
    Returns:
        Combined hash value
    """
    # HASH_MASK ensures no overflow
    return ((hash1 & HASH_MASK) + 123456789) ^ hash2


def create_hash(value: int) -> HashValue:
    """Create hash from integer value.
    
    Args:
        value: Integer to hash
        
    Returns:
        Hash value
    """
    return value ^ (value << 3) ^ (value << 7)


def equal_pointers(key1: HashKey, key2: HashKey) -> bool:
    """Default equality function (pointer/identity comparison).
    
    Args:
        key1: First key
        key2: Second key
        
    Returns:
        True if keys are identical (same object)
    """
    return key1 is key2


def hash_pointers(key: HashKey) -> HashValue:
    """Default hash function (based on id/pointer).
    
    Args:
        key: Key to hash
        
    Returns:
        Hash value based on object id
    """
    return create_hash(id(key))


def string_hash(value: str) -> HashValue:
    """Hash function for strings.
    
    Args:
        value: String to hash
        
    Returns:
        Hash value
    """
    hash_val = 0
    length = len(value)
    
    # Process in 4-byte chunks
    for i in range(0, length, 4):
        h = 0
        for j in range(i, min(length, i + 4)):
            k = 8 * (j % 4)
            v = ord(value[j])
            h = h | (v << k)
        
        hash_val = combine_hash(hash_val, h)
    
    return hash_val


def array_hash(values: List[int]) -> HashValue:
    """Hash function for integer arrays.
    
    Args:
        values: List of integers to hash
        
    Returns:
        Hash value
    """
    hash_val = 0
    
    for v in values:
        h = create_hash(v)
        hash_val = combine_hash(hash_val, h)
    
    return hash_val


# ============================================================================
# Hash Table Entry
# ============================================================================

class HashEntry:
    """Entry in hash table."""
    
    def __init__(self):
        self.used = False
        self.key = None
        self.data = None
        self.hash = 0


# ============================================================================
# Hash Table
# ============================================================================

class HashTable:
    """Hash table with dynamic resizing and linear probing.
    
    Attributes:
        equal_func: Function to compare keys for equality
        hash_func: Function to compute hash from key
        nentries: Total number of slots in table
        nused: Number of slots currently used
        entries: Array of hash entries
    """
    
    def __init__(self, 
                 equal_func: Optional[EqualFunc] = None,
                 hash_func: Optional[HashFunc] = None):
        """Create new hash table.
        
        Args:
            equal_func: Custom equality function (default: equal_pointers)
            hash_func: Custom hash function (default: hash_pointers)
        """
        self.equal_func = equal_func if equal_func else equal_pointers
        self.hash_func = hash_func if hash_func else hash_pointers
        self.nentries = 0
        self.nused = 0
        self.entries = []
    
    def _next_entry(self, index: int) -> int:
        """Get next entry index (wraps around).
        
        Args:
            index: Current index
            
        Returns:
            Next index (wraps to 0 at end)
        """
        return (index + 1) % self.nentries if self.nentries > 0 else 0
    
    def _table_entry(self, key: HashKey, hash_val: HashValue) -> Optional[int]:
        """Find entry for key (or empty slot for insertion).
        
        Args:
            key: Key to find
            hash_val: Hash value of key
            
        Returns:
            Index of entry, or None if table empty
        """
        if self.nentries == 0:
            return None
        
        # Start at hash position
        index = hash_val % self.nentries
        
        # Linear probing
        while self.entries[index].used:
            entry = self.entries[index]
            if entry.hash == hash_val and self.equal_func(entry.key, key):
                return index
            index = self._next_entry(index)
        
        return index
    
    def _insert_table(self, key: HashKey, data: HashData, hash_val: HashValue):
        """Insert entry into table (internal, assumes space available).
        
        Args:
            key: Key to insert
            data: Data to associate with key
            hash_val: Hash value of key
        """
        index = self._table_entry(key, hash_val)
        
        if index is not None:
            entry = self.entries[index]
            
            if not entry.used:
                entry.used = True
                self.nused += 1
            
            entry.key = key
            entry.data = data
            entry.hash = hash_val
    
    def _resize_table(self):
        """Resize table (grow or shrink based on usage)."""
        # Calculate new size
        if self.nentries == 0:
            new_size = TABLE_INITIAL_SIZE
        else:
            new_size = TABLE_INITIAL_SIZE + RESIZE_FACTOR * self.nused
        
        # Save old entries
        old_entries = self.entries
        old_nentries = self.nentries
        
        # Create new table
        self.entries = [HashEntry() for _ in range(new_size)]
        self.nentries = new_size
        self.nused = 0
        
        # Rehash all old entries
        for entry in old_entries:
            if entry.used:
                self._insert_table(entry.key, entry.data, entry.hash)
    
    def insert(self, key: HashKey, data: HashData) -> bool:
        """Insert key-data pair into hash table.
        
        Args:
            key: Key to insert
            data: Data to associate with key
            
        Returns:
            True on success
        """
        # Resize if getting full
        if self.nused >= self.nentries // GROW_FACTOR:
            self._resize_table()
        
        hash_val = self.hash_func(key)
        self._insert_table(key, data, hash_val)
        
        return True
    
    def remove(self, key: HashKey) -> Optional[HashData]:
        """Remove key from hash table.
        
        Args:
            key: Key to remove
            
        Returns:
            Data associated with key, or None if not found
        """
        hash_val = self.hash_func(key)
        index = self._table_entry(key, hash_val)
        
        if index is None or not self.entries[index].used:
            return None
        
        entry = self.entries[index]
        data = entry.data
        entry.used = False
        
        # Rehash subsequent entries to fill gap
        ne_index = self._next_entry(index)
        
        while self.entries[ne_index].used:
            ne = self.entries[ne_index]
            pe_index = ne.hash % self.nentries
            
            # Check if entry should be moved
            if index < ne_index:
                should_move = pe_index <= index or pe_index > ne_index
            else:
                should_move = pe_index <= index and pe_index > ne_index
            
            if should_move:
                # Move entry to fill gap (copy values, not reference)
                self.entries[index].used = True
                self.entries[index].key = ne.key
                self.entries[index].data = ne.data
                self.entries[index].hash = ne.hash
                ne.used = False
                index = ne_index
            
            ne_index = self._next_entry(ne_index)
        
        self.nused -= 1
        
        # Shrink if getting sparse
        if self.nused < self.nentries // SHRINK_FACTOR:
            self._resize_table()
        
        return data
    
    def contains(self, key: HashKey) -> bool:
        """Check if key is in hash table.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists
        """
        hash_val = self.hash_func(key)
        index = self._table_entry(key, hash_val)
        
        return index is not None and self.entries[index].used
    
    def find(self, key: HashKey) -> Tuple[bool, Optional[HashData]]:
        """Find data associated with key.
        
        Args:
            key: Key to find
            
        Returns:
            (found, data) tuple
        """
        hash_val = self.hash_func(key)
        index = self._table_entry(key, hash_val)
        
        if index is not None and self.entries[index].used:
            return (True, self.entries[index].data)
        
        return (False, None)
    
    def get(self, key: HashKey, default=None) -> Optional[HashData]:
        """Get data for key (dict-like interface).
        
        Args:
            key: Key to get
            default: Default value if not found
            
        Returns:
            Data associated with key, or default
        """
        found, data = self.find(key)
        return data if found else default
    
    def clear(self, clear_func: Optional[HashClearFunc] = None, 
              user_data: Any = None):
        """Clear all entries from hash table.
        
        Args:
            clear_func: Optional callback for each entry
            user_data: User data passed to callback
        """
        for entry in self.entries:
            if entry.used:
                entry.used = False
                if clear_func:
                    clear_func(entry.key, entry.data, user_data)
        
        self.nused = 0
        self._resize_table()
    
    def iterate(self, iter_func: HashIterFunc, user_data: Any = None) -> bool:
        """Iterate over all entries in hash table.
        
        Args:
            iter_func: Function called for each entry
            user_data: User data passed to function
            
        Returns:
            True if all iterations successful
        """
        for entry in self.entries:
            if entry.used:
                if not iter_func(entry.key, entry.data, user_data):
                    return False
        
        return True
    
    def items(self):
        """Iterate over (key, data) pairs (dict-like interface).
        
        Yields:
            (key, data) tuples
        """
        for entry in self.entries:
            if entry.used:
                yield (entry.key, entry.data)
    
    def keys(self):
        """Iterate over keys (dict-like interface).
        
        Yields:
            Keys
        """
        for entry in self.entries:
            if entry.used:
                yield entry.key
    
    def values(self):
        """Iterate over values (dict-like interface).
        
        Yields:
            Values
        """
        for entry in self.entries:
            if entry.used:
                yield entry.data
    
    def __len__(self) -> int:
        """Get number of entries."""
        return self.nused
    
    def __contains__(self, key: HashKey) -> bool:
        """Check if key in table (enables 'in' operator)."""
        return self.contains(key)
    
    def __getitem__(self, key: HashKey) -> HashData:
        """Get item by key (enables table[key])."""
        found, data = self.find(key)
        if not found:
            raise KeyError(key)
        return data
    
    def __setitem__(self, key: HashKey, data: HashData):
        """Set item by key (enables table[key] = data)."""
        self.insert(key, data)
    
    def __delitem__(self, key: HashKey):
        """Delete item by key (enables del table[key])."""
        data = self.remove(key)
        if data is None:
            raise KeyError(key)


# Example usage
if __name__ == "__main__":
    # Test with default hash/equal functions
    table = HashTable()
    
    # Insert some data
    obj1, obj2, obj3 = object(), object(), object()
    table.insert(obj1, "data1")
    table.insert(obj2, "data2")
    table.insert(obj3, "data3")
    
    print(f"Table size: {len(table)}")
    print(f"Contains obj1: {table.contains(obj1)}")
    
    found, data = table.find(obj2)
    print(f"Found obj2: {found}, data: {data}")
    
    # Test with string hash
    def equal_strings(s1, s2):
        return s1 == s2
    
    str_table = HashTable(equal_func=equal_strings, hash_func=string_hash)
    str_table["hello"] = 42
    str_table["world"] = 99
    
    print(f"\nString table:")
    print(f"hello -> {str_table['hello']}")
    print(f"world -> {str_table['world']}")
    
    # Iterate
    print("\nAll entries:")
    for key, value in str_table.items():
        print(f"  {key} -> {value}")
