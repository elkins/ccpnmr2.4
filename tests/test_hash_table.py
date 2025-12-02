"""
Tests for hash_table.py module

Test coverage:
- Hash table creation
- Insert/remove/find operations
- Dynamic resizing (grow and shrink)
- Custom hash and equality functions
- Iteration and clearing
- Dict-like interface
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.c.python_impl.hash_table import (
    HashTable,
    combine_hash, create_hash,
    equal_pointers, hash_pointers,
    string_hash, array_hash
)


# ============================================================================
# Hash Function Tests
# ============================================================================

def test_combine_hash():
    """Test hash combination."""
    h1 = create_hash(42)
    h2 = create_hash(99)
    combined = combine_hash(h1, h2)
    
    # Should produce different result than inputs
    assert combined != h1
    assert combined != h2


def test_create_hash_different():
    """Test that different values produce different hashes."""
    h1 = create_hash(1)
    h2 = create_hash(2)
    h3 = create_hash(1)
    
    assert h1 != h2
    assert h1 == h3  # Same input -> same hash


def test_equal_pointers():
    """Test pointer equality."""
    obj1 = object()
    obj2 = object()
    
    assert equal_pointers(obj1, obj1)
    assert not equal_pointers(obj1, obj2)


def test_hash_pointers():
    """Test pointer hashing."""
    obj1 = object()
    h1 = hash_pointers(obj1)
    h2 = hash_pointers(obj1)
    
    # Same object should give same hash
    assert h1 == h2


def test_string_hash():
    """Test string hashing."""
    h1 = string_hash("hello")
    h2 = string_hash("hello")
    h3 = string_hash("world")
    
    assert h1 == h2  # Same string -> same hash
    assert h1 != h3  # Different strings -> different hashes


def test_array_hash():
    """Test array hashing."""
    h1 = array_hash([1, 2, 3])
    h2 = array_hash([1, 2, 3])
    h3 = array_hash([4, 5, 6])
    
    assert h1 == h2  # Same array -> same hash
    assert h1 != h3  # Different arrays -> different hashes


# ============================================================================
# Basic Hash Table Tests
# ============================================================================

def test_create_hash_table():
    """Test hash table creation."""
    table = HashTable()
    assert len(table) == 0
    assert table.nentries == 0
    assert table.nused == 0


def test_insert_and_find():
    """Test basic insert and find."""
    table = HashTable()
    
    obj1 = object()
    table.insert(obj1, "data1")
    
    assert len(table) == 1
    assert table.contains(obj1)
    
    found, data = table.find(obj1)
    assert found
    assert data == "data1"


def test_insert_multiple():
    """Test inserting multiple items."""
    table = HashTable()
    
    objects = [object() for _ in range(10)]
    
    for i, obj in enumerate(objects):
        table.insert(obj, f"data{i}")
    
    assert len(table) == 10
    
    for i, obj in enumerate(objects):
        found, data = table.find(obj)
        assert found
        assert data == f"data{i}"


def test_insert_update():
    """Test updating existing key."""
    table = HashTable()
    
    obj = object()
    table.insert(obj, "data1")
    table.insert(obj, "data2")  # Update
    
    assert len(table) == 1  # Still one entry
    
    found, data = table.find(obj)
    assert data == "data2"  # Updated value


def test_remove():
    """Test removing entries."""
    table = HashTable()
    
    obj = object()
    table.insert(obj, "data1")
    
    data = table.remove(obj)
    assert data == "data1"
    assert len(table) == 0
    assert not table.contains(obj)


def test_remove_nonexistent():
    """Test removing nonexistent key."""
    table = HashTable()
    
    obj = object()
    data = table.remove(obj)
    assert data is None


def test_find_nonexistent():
    """Test finding nonexistent key."""
    table = HashTable()
    
    obj = object()
    found, data = table.find(obj)
    assert not found
    assert data is None


# ============================================================================
# Dynamic Resizing Tests
# ============================================================================

def test_resize_grow():
    """Test table grows when filled."""
    table = HashTable()
    
    initial_capacity = table.nentries
    
    # Insert many items to trigger resize
    objects = [object() for _ in range(1000)]
    for i, obj in enumerate(objects):
        table.insert(obj, i)
    
    # Table should have grown
    assert table.nentries > initial_capacity
    assert len(table) == 1000
    
    # All items should still be findable
    for i, obj in enumerate(objects):
        found, data = table.find(obj)
        assert found
        assert data == i


def test_resize_shrink():
    """Test table shrinks when sparse."""
    table = HashTable()
    
    # Insert many items
    objects = [object() for _ in range(1000)]
    for obj in objects:
        table.insert(obj, "data")
    
    capacity_after_insert = table.nentries
    
    # Remove most items
    for obj in objects[:-10]:
        table.remove(obj)
    
    # Table should have shrunk
    assert len(table) == 10
    assert table.nentries < capacity_after_insert


# ============================================================================
# Custom Hash/Equality Tests
# ============================================================================

def test_string_table():
    """Test hash table with string keys."""
    def equal_strings(s1, s2):
        return s1 == s2
    
    table = HashTable(equal_func=equal_strings, hash_func=string_hash)
    
    table.insert("hello", 42)
    table.insert("world", 99)
    
    assert len(table) == 2
    
    found, data = table.find("hello")
    assert found
    assert data == 42


def test_array_table():
    """Test hash table with array keys."""
    def equal_arrays(a1, a2):
        return a1 == a2
    
    table = HashTable(equal_func=equal_arrays, hash_func=array_hash)
    
    table.insert([1, 2, 3], "data1")
    table.insert([4, 5, 6], "data2")
    
    assert len(table) == 2
    
    found, data = table.find([1, 2, 3])
    assert found
    assert data == "data1"


# ============================================================================
# Iteration and Clearing Tests
# ============================================================================

def test_clear():
    """Test clearing hash table."""
    table = HashTable()
    
    objects = [object() for _ in range(10)]
    for obj in objects:
        table.insert(obj, "data")
    
    assert len(table) == 10
    
    table.clear()
    
    assert len(table) == 0
    for obj in objects:
        assert not table.contains(obj)


def test_clear_with_callback():
    """Test clearing with callback function."""
    table = HashTable()
    
    objects = [object() for _ in range(5)]
    for i, obj in enumerate(objects):
        table.insert(obj, i)
    
    cleared_keys = []
    
    def clear_func(key, data, user_data):
        cleared_keys.append((key, data))
    
    table.clear(clear_func=clear_func)
    
    assert len(cleared_keys) == 5
    assert len(table) == 0


def test_iterate():
    """Test iterating over hash table."""
    table = HashTable()
    
    objects = [object() for _ in range(5)]
    for i, obj in enumerate(objects):
        table.insert(obj, i)
    
    visited = []
    
    def iter_func(key, data, user_data):
        visited.append((key, data))
        return True
    
    result = table.iterate(iter_func)
    
    assert result
    assert len(visited) == 5


def test_iterate_early_stop():
    """Test stopping iteration early."""
    table = HashTable()
    
    objects = [object() for _ in range(10)]
    for obj in objects:
        table.insert(obj, "data")
    
    count = [0]
    
    def iter_func(key, data, user_data):
        count[0] += 1
        return count[0] < 5  # Stop after 5
    
    result = table.iterate(iter_func)
    
    assert not result  # Stopped early
    assert count[0] == 5


# ============================================================================
# Dict-like Interface Tests
# ============================================================================

def test_dict_interface_get_set():
    """Test dict-like get/set."""
    def equal_strings(s1, s2):
        return s1 == s2
    
    table = HashTable(equal_func=equal_strings, hash_func=string_hash)
    
    table["hello"] = 42
    table["world"] = 99
    
    assert table["hello"] == 42
    assert table["world"] == 99


def test_dict_interface_del():
    """Test dict-like delete."""
    def equal_strings(s1, s2):
        return s1 == s2
    
    table = HashTable(equal_func=equal_strings, hash_func=string_hash)
    
    table["hello"] = 42
    assert "hello" in table
    
    del table["hello"]
    assert "hello" not in table


def test_dict_interface_get_method():
    """Test dict-like get method."""
    def equal_strings(s1, s2):
        return s1 == s2
    
    table = HashTable(equal_func=equal_strings, hash_func=string_hash)
    
    table["hello"] = 42
    
    assert table.get("hello") == 42
    assert table.get("missing") is None
    assert table.get("missing", "default") == "default"


def test_dict_interface_items():
    """Test dict-like items iteration."""
    def equal_strings(s1, s2):
        return s1 == s2
    
    table = HashTable(equal_func=equal_strings, hash_func=string_hash)
    
    table["a"] = 1
    table["b"] = 2
    table["c"] = 3
    
    items = list(table.items())
    assert len(items) == 3
    
    # Check all items present
    items_dict = dict(items)
    assert items_dict["a"] == 1
    assert items_dict["b"] == 2
    assert items_dict["c"] == 3


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_combine_hash,
        test_create_hash_different,
        test_equal_pointers,
        test_hash_pointers,
        test_string_hash,
        test_array_hash,
        test_create_hash_table,
        test_insert_and_find,
        test_insert_multiple,
        test_insert_update,
        test_remove,
        test_remove_nonexistent,
        test_find_nonexistent,
        test_resize_grow,
        test_resize_shrink,
        test_string_table,
        test_array_table,
        test_clear,
        test_clear_with_callback,
        test_iterate,
        test_iterate_early_stop,
        test_dict_interface_get_set,
        test_dict_interface_del,
        test_dict_interface_get_method,
        test_dict_interface_items
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Hash Table Tests: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
