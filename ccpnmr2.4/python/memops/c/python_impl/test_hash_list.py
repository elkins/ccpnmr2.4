"""
Tests for hash_list.py - Hybrid hash table + doubly-linked list
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hash_list import (
    HashList, new_hash_list, delete_hash_list, clear_hash_list, empty_hash_list,
    insert_hash_list, append_hash_list, find_key_hash_list, remove_key_hash_list,
    remove_first_hash_list, remove_last_hash_list, promote_hash_list, demote_hash_list,
    traverse_hash_list
)


class TestHashList:
    """Test the HashList class."""
    
    def test_init(self):
        """Test hash-list initialization."""
        hl = HashList()
        assert hl.is_empty()
        assert len(hl) == 0
    
    def test_insert_front(self):
        """Test inserting at front."""
        hl = HashList()
        hl.insert('a', 1)
        hl.insert('b', 2)
        hl.insert('c', 3)
        
        # Should be in reverse order: c, b, a
        assert list(hl.keys()) == ['c', 'b', 'a']
        assert list(hl.values()) == [3, 2, 1]
    
    def test_append_back(self):
        """Test appending to back."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        # Should be in order: a, b, c
        assert list(hl.keys()) == ['a', 'b', 'c']
        assert list(hl.values()) == [1, 2, 3]
    
    def test_mixed_insert_append(self):
        """Test mixing insert and append."""
        hl = HashList()
        hl.append('b', 2)  # [b]
        hl.insert('a', 1)  # [a, b]
        hl.append('c', 3)  # [a, b, c]
        hl.insert('x', 0)  # [x, a, b, c]
        
        assert list(hl.keys()) == ['x', 'a', 'b', 'c']
    
    def test_find_key(self):
        """Test finding by key."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        assert hl.find_key('b') == 2
        assert hl.find_key('z') is None
    
    def test_remove_key(self):
        """Test removing by key."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        removed = hl.remove_key('b')
        assert removed == 2
        assert list(hl.keys()) == ['a', 'c']
        
        # Removing non-existent key
        removed = hl.remove_key('z')
        assert removed is None
    
    def test_remove_first(self):
        """Test removing first element."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        key, data = hl.remove_first()
        assert key == 'a' and data == 1
        assert list(hl.keys()) == ['b', 'c']
        
        key, data = hl.remove_first()
        assert key == 'b' and data == 2
        assert list(hl.keys()) == ['c']
    
    def test_remove_last(self):
        """Test removing last element."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        key, data = hl.remove_last()
        assert key == 'c' and data == 3
        assert list(hl.keys()) == ['a', 'b']
    
    def test_promote(self):
        """Test promoting to front (LRU behavior)."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        # Promote 'b' to front
        data = hl.promote('b')
        assert data == 2
        assert list(hl.keys()) == ['b', 'a', 'c']
        
        # Promote 'c' to front
        data = hl.promote('c')
        assert data == 3
        assert list(hl.keys()) == ['c', 'b', 'a']
    
    def test_demote(self):
        """Test demoting to back (LRU behavior)."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        # Demote 'b' to back
        data = hl.demote('b')
        assert data == 2
        assert list(hl.keys()) == ['a', 'c', 'b']
        
        # Demote 'a' to back
        data = hl.demote('a')
        assert data == 1
        assert list(hl.keys()) == ['c', 'b', 'a']
    
    def test_promote_already_first(self):
        """Test promoting element already at front."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        
        data = hl.promote('a')
        assert data == 1
        assert list(hl.keys()) == ['a', 'b']  # No change
    
    def test_demote_already_last(self):
        """Test demoting element already at back."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        
        data = hl.demote('b')
        assert data == 2
        assert list(hl.keys()) == ['a', 'b']  # No change
    
    def test_contains(self):
        """Test membership checking."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        
        assert 'a' in hl
        assert 'b' in hl
        assert 'z' not in hl
    
    def test_clear(self):
        """Test clearing the hash-list."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        hl.clear()
        assert hl.is_empty()
        assert len(hl) == 0
    
    def test_clear_with_cleanup(self):
        """Test clearing with cleanup function."""
        cleaned = []
        
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        hl.clear(lambda x: cleaned.append(x))
        
        assert hl.is_empty()
        assert set(cleaned) == {1, 2, 3}
    
    def test_traverse_forward(self):
        """Test forward traversal."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        collected = []
        def collector(data, user_data):
            collected.append(data)
            return (True, False)  # Continue
        
        result = hl.traverse(collector, forward=True)
        assert result is True
        assert collected == [1, 2, 3]
    
    def test_traverse_reverse(self):
        """Test reverse traversal."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        collected = []
        def collector(data, user_data):
            collected.append(data)
            return (True, False)
        
        result = hl.traverse(collector, forward=False)
        assert result is True
        assert collected == [3, 2, 1]
    
    def test_traverse_early_termination(self):
        """Test early termination of traversal."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        collected = []
        def collector(data, user_data):
            collected.append(data)
            done = (data == 2)  # Stop after 2
            return (True, done)
        
        result = hl.traverse(collector, forward=True)
        assert result is True
        assert collected == [1, 2]
    
    def test_iterate(self):
        """Test iteration over keys."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        keys = list(hl)
        assert keys == ['a', 'b', 'c']


class TestCFunctionInterface:
    """Test C-compatible function interface."""
    
    def test_new_hash_list(self):
        """Test creating new hash-list."""
        hl = new_hash_list()
        assert empty_hash_list(hl)
    
    def test_insert_append_functions(self):
        """Test insert and append functions."""
        hl = new_hash_list()
        
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        insert_hash_list(hl, 'x', 0)
        
        assert list(hl.keys()) == ['x', 'a', 'b']
    
    def test_find_key_function(self):
        """Test find_key function."""
        hl = new_hash_list()
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        
        result = find_key_hash_list(hl, 'b')
        assert result == 2
        
        result = find_key_hash_list(hl, 'z')
        assert result is None
    
    def test_remove_key_function(self):
        """Test remove_key function."""
        hl = new_hash_list()
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        
        removed = remove_key_hash_list(hl, 'a')
        assert removed == 1
        assert list(hl.keys()) == ['b']
    
    def test_remove_first_last_functions(self):
        """Test remove_first and remove_last functions."""
        hl = new_hash_list()
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        append_hash_list(hl, 'c', 3)
        
        key, data = remove_first_hash_list(hl)
        assert key == 'a' and data == 1
        
        key, data = remove_last_hash_list(hl)
        assert key == 'c' and data == 3
        
        assert list(hl.keys()) == ['b']
    
    def test_promote_demote_functions(self):
        """Test promote and demote functions."""
        hl = new_hash_list()
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        append_hash_list(hl, 'c', 3)
        
        data = promote_hash_list(hl, 'c')
        assert data == 3
        assert list(hl.keys()) == ['c', 'a', 'b']
        
        data = demote_hash_list(hl, 'c')
        assert data == 3
        assert list(hl.keys()) == ['a', 'b', 'c']
    
    def test_traverse_function(self):
        """Test traverse function."""
        hl = new_hash_list()
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        append_hash_list(hl, 'c', 3)
        
        collected = []
        def collector(data, user_data):
            collected.append(data)
            return (True, False)
        
        result = traverse_hash_list(hl, True, collector)
        assert result is True
        assert collected == [1, 2, 3]
    
    def test_clear_delete_functions(self):
        """Test clear and delete functions."""
        hl = new_hash_list()
        append_hash_list(hl, 'a', 1)
        append_hash_list(hl, 'b', 2)
        
        clear_hash_list(hl)
        assert empty_hash_list(hl)
        
        # Add more items
        append_hash_list(hl, 'x', 10)
        
        delete_hash_list(hl)
        assert empty_hash_list(hl)


class TestLRUCacheBehavior:
    """Test LRU cache use case."""
    
    def test_lru_cache_scenario(self):
        """Test typical LRU cache operations."""
        # Simulate LRU cache with max size 3
        hl = HashList()
        max_size = 3
        
        # Add items
        hl.append('page1', 'data1')
        hl.append('page2', 'data2')
        hl.append('page3', 'data3')
        
        # Access page1 (promote to front - most recently used)
        data = hl.promote('page1')
        assert data == 'data1'
        assert list(hl.keys()) == ['page1', 'page2', 'page3']
        
        # Add new page (would evict LRU if at capacity)
        if len(hl) >= max_size:
            hl.remove_last()
            # Evict LRU
        hl.insert('page4', 'data4')  # Add as MRU
        
        assert list(hl.keys()) == ['page4', 'page1', 'page2']
        assert 'page3' not in hl  # Evicted
    
    def test_access_order_tracking(self):
        """Test tracking access order."""
        hl = HashList()
        hl.append('a', 1)
        hl.append('b', 2)
        hl.append('c', 3)
        
        # Access order: a, b, c
        # Access 'b'
        hl.promote('b')
        # Order now: b, a, c
        
        # Access 'c'
        hl.promote('c')
        # Order now: c, b, a
        
        # Access 'b' again
        hl.promote('b')
        # Order now: b, c, a
        
        assert list(hl.keys()) == ['b', 'c', 'a']


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_operations_on_empty(self):
        """Test operations on empty hash-list."""
        hl = HashList()
        
        assert hl.is_empty()
        assert hl.find_key('x') is None
        assert hl.remove_key('x') is None
        assert hl.remove_first() is None
        assert hl.remove_last() is None
        assert hl.promote('x') is None
        assert hl.demote('x') is None
    
    def test_single_element(self):
        """Test with single element."""
        hl = HashList()
        hl.append('a', 1)
        
        assert not hl.is_empty()
        assert len(hl) == 1
        
        # Promote single element
        hl.promote('a')
        assert list(hl.keys()) == ['a']
        
        # Remove it
        key, data = hl.remove_first()
        assert key == 'a' and data == 1
        assert hl.is_empty()
    
    def test_duplicate_key_insert(self):
        """Test inserting duplicate key (should fail)."""
        hl = HashList()
        result1 = hl.insert('a', 1)
        assert result1 is True
        
        result2 = hl.insert('a', 2)  # Duplicate
        assert result2 is False
        
        # Original value should remain
        assert hl.find_key('a') == 1
    
    def test_duplicate_key_append(self):
        """Test appending duplicate key (should fail)."""
        hl = HashList()
        result1 = hl.append('a', 1)
        assert result1 is True
        
        result2 = hl.append('a', 2)  # Duplicate
        assert result2 is False
        
        assert hl.find_key('a') == 1
    
    def test_complex_objects(self):
        """Test storing complex objects."""
        hl = HashList()
        
        obj1 = {'id': 1, 'data': [1, 2, 3]}
        obj2 = {'id': 2, 'data': [4, 5, 6]}
        
        hl.append('obj1', obj1)
        hl.append('obj2', obj2)
        
        retrieved = hl.find_key('obj1')
        assert retrieved == obj1
    
    def test_large_hash_list(self):
        """Test with large number of elements."""
        hl = HashList()
        
        n = 1000
        for i in range(n):
            hl.append(f'key{i}', i)
        
        assert len(hl) == n
        
        # Test finding
        assert hl.find_key('key500') == 500
        
        # Test promote
        hl.promote('key500')
        assert list(hl.keys())[0] == 'key500'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
