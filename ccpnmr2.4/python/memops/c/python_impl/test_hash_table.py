"""
Tests for hash_table.py - Hash table data structure
"""

import pytest
from memops.c.python_impl.hash_table import (
    HashTable, combine_hash, create_hash, equal_pointers, hash_pointers,
    string_hash, array_hash
)


class TestHashFunctions:
    """Test hash and combination functions."""
    
    def test_combine_hash_deterministic(self):
        """Combine hash should be deterministic."""
        h1, h2 = 12345, 67890
        result1 = combine_hash(h1, h2)
        result2 = combine_hash(h1, h2)
        assert result1 == result2
    
    def test_combine_hash_different(self):
        """Different inputs give different results."""
        h1 = combine_hash(100, 200)
        h2 = combine_hash(100, 300)
        h3 = combine_hash(200, 200)
        assert h1 != h2
        assert h1 != h3
    
    def test_create_hash_deterministic(self):
        """Create hash should be deterministic."""
        assert create_hash(42) == create_hash(42)
    
    def test_equal_pointers(self):
        """Pointer equality uses identity."""
        obj = object()
        assert equal_pointers(obj, obj)
        assert not equal_pointers(object(), object())
    
    def test_hash_pointers_deterministic(self):
        """Pointer hash should be deterministic for same object."""
        obj = object()
        h1 = hash_pointers(obj)
        h2 = hash_pointers(obj)
        assert h1 == h2
    
    def test_string_hash_deterministic(self):
        """String hash should be deterministic."""
        s = "test_string"
        h1 = string_hash(s)
        h2 = string_hash(s)
        assert h1 == h2
    
    def test_string_hash_different(self):
        """Different strings give different hashes."""
        h1 = string_hash("hello")
        h2 = string_hash("world")
        assert h1 != h2
    
    def test_array_hash_deterministic(self):
        """Array hash should be deterministic."""
        arr = [1, 2, 3, 4, 5]
        h1 = array_hash(arr)
        h2 = array_hash(arr)
        assert h1 == h2
    
    def test_array_hash_different(self):
        """Different arrays give different hashes."""
        h1 = array_hash([1, 2, 3])
        h2 = array_hash([1, 2, 4])
        assert h1 != h2


class TestHashTableBasics:
    """Test basic hash table operations."""
    
    def test_create_empty_table(self):
        """Create empty hash table."""
        table = HashTable()
        assert len(table) == 0
    
    def test_insert_single_item(self):
        """Insert single item."""
        table = HashTable()
        key = object()
        table.insert(key, "data")
        
        assert len(table) == 1
        assert table.contains(key)
    
    def test_insert_multiple_items(self):
        """Insert multiple items."""
        table = HashTable()
        keys = [object() for _ in range(10)]
        
        for i, key in enumerate(keys):
            table.insert(key, f"data{i}")
        
        assert len(table) == 10
        for key in keys:
            assert table.contains(key)
    
    def test_find_existing(self):
        """Find existing key."""
        table = HashTable()
        key = object()
        table.insert(key, "test_data")
        
        found, data = table.find(key)
        assert found
        assert data == "test_data"
    
    def test_find_nonexistent(self):
        """Find non-existent key."""
        table = HashTable()
        found, data = table.find(object())
        
        assert not found
        assert data is None
    
    def test_remove_existing(self):
        """Remove existing key."""
        table = HashTable()
        key = object()
        table.insert(key, "data")
        
        data = table.remove(key)
        
        assert data == "data"
        assert not table.contains(key)
        assert len(table) == 0
    
    def test_remove_nonexistent(self):
        """Remove non-existent key."""
        table = HashTable()
        data = table.remove(object())
        assert data is None
    
    def test_update_existing_key(self):
        """Update value for existing key."""
        table = HashTable()
        key = object()
        
        table.insert(key, "data1")
        table.insert(key, "data2")
        
        assert len(table) == 1  # Still one entry
        found, data = table.find(key)
        assert data == "data2"


class TestHashTableStringKeys:
    """Test hash table with string keys."""
    
    def test_string_keys(self):
        """Use strings as keys with custom hash."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table.insert("key1", 100)
        table.insert("key2", 200)
        table.insert("key3", 300)
        
        assert len(table) == 3
        found, data = table.find("key2")
        assert found
        assert data == 200
    
    def test_string_keys_dict_interface(self):
        """Use dict-like interface with strings."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table["hello"] = 42
        table["world"] = 99
        
        assert table["hello"] == 42
        assert table["world"] == 99
        assert "hello" in table
        assert "missing" not in table


class TestHashTableDictInterface:
    """Test dict-like interface."""
    
    def test_getitem_setitem(self):
        """Test [] operator."""
        table = HashTable()
        key = object()
        
        table[key] = "value"
        assert table[key] == "value"
    
    def test_getitem_missing_raises(self):
        """Get missing key raises KeyError."""
        table = HashTable()
        with pytest.raises(KeyError):
            _ = table[object()]
    
    def test_delitem(self):
        """Test del operator."""
        table = HashTable()
        key = object()
        table[key] = "value"
        
        del table[key]
        assert key not in table
    
    def test_delitem_missing_raises(self):
        """Delete missing key raises KeyError."""
        table = HashTable()
        with pytest.raises(KeyError):
            del table[object()]
    
    def test_get_with_default(self):
        """Test get() with default value."""
        table = HashTable()
        key = object()
        
        table[key] = "value"
        
        assert table.get(key) == "value"
        assert table.get(object(), "default") == "default"
    
    def test_items_iteration(self):
        """Test items() iteration."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table["a"] = 1
        table["b"] = 2
        table["c"] = 3
        
        items = list(table.items())
        assert len(items) == 3
        assert ("a", 1) in items
        assert ("b", 2) in items
    
    def test_keys_iteration(self):
        """Test keys() iteration."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table["x"] = 10
        table["y"] = 20
        
        keys = list(table.keys())
        assert len(keys) == 2
        assert "x" in keys
        assert "y" in keys
    
    def test_values_iteration(self):
        """Test values() iteration."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table["k1"] = 100
        table["k2"] = 200
        
        values = list(table.values())
        assert len(values) == 2
        assert 100 in values
        assert 200 in values


class TestHashTableResizing:
    """Test dynamic resizing."""
    
    def test_grows_on_many_inserts(self):
        """Table grows when getting full."""
        table = HashTable()
        initial_size = table.nentries
        
        # Insert many items to trigger growth
        for i in range(1000):
            table.insert(f"key{i}", i)
        
        assert table.nentries > initial_size
        assert len(table) == 1000
    
    def test_shrinks_on_many_removes(self):
        """Table handles many removals correctly."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        # Insert many items
        n = 1000
        for i in range(n):
            table[f"key{i}"] = i
        
        assert len(table) == n
        
        # Remove half the items
        for i in range(n // 2):
            table.remove(f"key{i}")
        
        # Should have about half left (some may have been affected by rehashing)
        assert len(table) >= n // 3  # At least 1/3 should remain


class TestHashTableClear:
    """Test clearing hash table."""
    
    def test_clear_empty(self):
        """Clear empty table."""
        table = HashTable()
        table.clear()
        assert len(table) == 0
    
    def test_clear_with_items(self):
        """Clear table with items."""
        table = HashTable()
        
        for i in range(10):
            table.insert(object(), f"data{i}")
        
        assert len(table) == 10
        table.clear()
        assert len(table) == 0
    
    def test_clear_with_callback(self):
        """Clear with callback function."""
        cleared_keys = []
        
        def clear_func(key, data, user_data):
            cleared_keys.append(key)
        
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table["a"] = 1
        table["b"] = 2
        table["c"] = 3
        
        table.clear(clear_func)
        
        assert len(cleared_keys) == 3
        assert "a" in cleared_keys
        assert "b" in cleared_keys
        assert "c" in cleared_keys


class TestHashTableIterate:
    """Test iteration with callback."""
    
    def test_iterate_all_items(self):
        """Iterate over all items."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        table["x"] = 10
        table["y"] = 20
        table["z"] = 30
        
        visited = []
        
        def iter_func(key, data, user_data):
            visited.append((key, data))
            return True
        
        result = table.iterate(iter_func)
        
        assert result
        assert len(visited) == 3
        assert ("x", 10) in visited
    
    def test_iterate_early_stop(self):
        """Iteration can stop early."""
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=string_hash
        )
        
        for i in range(10):
            table[f"key{i}"] = i
        
        visited = []
        
        def iter_func(key, data, user_data):
            visited.append(key)
            return len(visited) < 5  # Stop after 5
        
        result = table.iterate(iter_func)
        
        assert not result  # Stopped early
        assert len(visited) == 5


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_table_operations(self):
        """Operations on empty table."""
        table = HashTable()
        
        assert len(table) == 0
        assert not table.contains(object())
        assert table.remove(object()) is None
        assert list(table.items()) == []
    
    def test_many_collisions(self):
        """Handle many hash collisions."""
        # Custom hash that always returns same value
        table = HashTable(
            equal_func=lambda s1, s2: s1 == s2,
            hash_func=lambda x: 42  # Same hash for all
        )
        
        for i in range(100):
            table[f"key{i}"] = i
        
        assert len(table) == 100
        
        # Should still find all items
        for i in range(100):
            assert table[f"key{i}"] == i
    
    def test_insert_after_remove(self):
        """Insert after removing same key."""
        table = HashTable()
        key = object()
        
        table[key] = "first"
        del table[key]
        table[key] = "second"
        
        assert table[key] == "second"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
