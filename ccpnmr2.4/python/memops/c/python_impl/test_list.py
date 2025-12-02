"""
Tests for list.py - Python list wrapper with C-compatible API
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from list import (
    CcpnList, init_list, empty_list, insert_list, append_list,
    delete_key, delete_list, traverse_list, find_key, destroy_list
)


class TestCcpnList:
    """Test the CcpnList class."""
    
    def test_init(self):
        """Test list initialization."""
        lst = CcpnList()
        assert lst.is_empty()
        assert len(lst) == 0
    
    def test_insert_prepend(self):
        """Test inserting at front (prepend)."""
        lst = CcpnList()
        lst.insert(1)
        lst.insert(2)
        lst.insert(3)
        
        # Should be in reverse order: 3, 2, 1
        assert list(lst) == [3, 2, 1]
        assert len(lst) == 3
    
    def test_append(self):
        """Test appending to end."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        # Should be in order: 1, 2, 3
        assert list(lst) == [1, 2, 3]
        assert len(lst) == 3
    
    def test_mixed_insert_append(self):
        """Test mixing insert and append operations."""
        lst = CcpnList()
        lst.append(2)  # [2]
        lst.insert(1)  # [1, 2]
        lst.append(3)  # [1, 2, 3]
        lst.insert(0)  # [0, 1, 2, 3]
        
        assert list(lst) == [0, 1, 2, 3]
    
    def test_delete_key_found(self):
        """Test deleting an existing key."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        result = lst.delete_key(2)
        assert result is True
        assert list(lst) == [1, 3]
        assert len(lst) == 2
    
    def test_delete_key_not_found(self):
        """Test deleting a non-existent key."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        
        result = lst.delete_key(99)
        assert result is False
        assert list(lst) == [1, 2]
    
    def test_delete_front(self):
        """Test removing from front."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        item = lst.delete_front()
        assert item == 1
        assert list(lst) == [2, 3]
        
        item = lst.delete_front()
        assert item == 2
        assert list(lst) == [3]
    
    def test_delete_front_empty(self):
        """Test deleting from empty list."""
        lst = CcpnList()
        item = lst.delete_front()
        assert item is None
    
    def test_traverse(self):
        """Test traversing the list."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        collected = []
        lst.traverse(lambda x: collected.append(x))
        
        assert collected == [1, 2, 3]
    
    def test_find_key_default_equality(self):
        """Test finding with default equality."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        result = lst.find_key(2)
        assert result == 2
        
        result = lst.find_key(99)
        assert result is None
    
    def test_find_key_custom_comparison(self):
        """Test finding with custom comparison function."""
        lst = CcpnList()
        lst.append({'id': 1, 'name': 'Alice'})
        lst.append({'id': 2, 'name': 'Bob'})
        lst.append({'id': 3, 'name': 'Charlie'})
        
        # Find by id
        result = lst.find_key(2, lambda key, item: item['id'] == key)
        assert result['name'] == 'Bob'
        
        # Find by name
        result = lst.find_key('Alice', lambda key, item: item['name'] == key)
        assert result['id'] == 1
    
    def test_destroy(self):
        """Test destroying the list."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        lst.destroy()
        assert lst.is_empty()
        assert len(lst) == 0
    
    def test_destroy_with_cleanup(self):
        """Test destroying with cleanup function."""
        # Track cleanup calls
        cleaned = []
        
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        
        lst.destroy(lambda x: cleaned.append(x))
        
        assert lst.is_empty()
        assert cleaned == [1, 2, 3]
    
    def test_contains(self):
        """Test membership checking."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        
        assert 1 in lst
        assert 2 in lst
        assert 3 not in lst
    
    def test_getitem(self):
        """Test indexing."""
        lst = CcpnList()
        lst.append(10)
        lst.append(20)
        lst.append(30)
        
        assert lst[0] == 10
        assert lst[1] == 20
        assert lst[2] == 30
        assert lst[-1] == 30
    
    def test_complex_objects(self):
        """Test storing complex objects."""
        lst = CcpnList()
        
        obj1 = {'id': 1, 'data': [1, 2, 3]}
        obj2 = {'id': 2, 'data': [4, 5, 6]}
        
        lst.append(obj1)
        lst.append(obj2)
        
        assert len(lst) == 2
        assert lst[0] == obj1
        assert lst[1] == obj2


class TestCFunctionInterface:
    """Test the C-compatible function interface."""
    
    def test_init_list(self):
        """Test init_list function."""
        lst = init_list()
        assert empty_list(lst)
    
    def test_insert_and_append(self):
        """Test insert_list and append_list functions."""
        lst = init_list()
        
        append_list(lst, 1)
        append_list(lst, 2)
        insert_list(lst, 0)
        
        assert list(lst) == [0, 1, 2]
    
    def test_delete_key_function(self):
        """Test delete_key function."""
        lst = init_list()
        append_list(lst, 1)
        append_list(lst, 2)
        append_list(lst, 3)
        
        result = delete_key(lst, 2)
        assert result is True
        assert list(lst) == [1, 3]
        
        result = delete_key(lst, 99)
        assert result is False
    
    def test_delete_list_function(self):
        """Test delete_list function."""
        lst = init_list()
        append_list(lst, 1)
        append_list(lst, 2)
        append_list(lst, 3)
        
        item = delete_list(lst)
        assert item == 1
        assert list(lst) == [2, 3]
    
    def test_traverse_list_function(self):
        """Test traverse_list function."""
        lst = init_list()
        append_list(lst, 1)
        append_list(lst, 2)
        append_list(lst, 3)
        
        collected = []
        traverse_list(lst, lambda x: collected.append(x))
        
        assert collected == [1, 2, 3]
    
    def test_find_key_function(self):
        """Test find_key function."""
        lst = init_list()
        append_list(lst, 10)
        append_list(lst, 20)
        append_list(lst, 30)
        
        result = find_key(lst, 20)
        assert result == 20
        
        result = find_key(lst, 99)
        assert result is None
    
    def test_destroy_list_function(self):
        """Test destroy_list function."""
        lst = init_list()
        append_list(lst, 1)
        append_list(lst, 2)
        
        destroyed = []
        destroy_list(lst, lambda x: destroyed.append(x))
        
        assert empty_list(lst)
        assert destroyed == [1, 2]


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_operations_on_empty_list(self):
        """Test operations on empty list."""
        lst = CcpnList()
        
        assert lst.is_empty()
        assert lst.delete_front() is None
        assert lst.find_key(1) is None
        assert not lst.delete_key(1)
    
    def test_single_element(self):
        """Test list with single element."""
        lst = CcpnList()
        lst.append(42)
        
        assert not lst.is_empty()
        assert len(lst) == 1
        assert lst[0] == 42
        
        item = lst.delete_front()
        assert item == 42
        assert lst.is_empty()
    
    def test_duplicate_values(self):
        """Test handling duplicate values."""
        lst = CcpnList()
        lst.append(1)
        lst.append(2)
        lst.append(1)  # Duplicate
        lst.append(3)
        
        assert list(lst) == [1, 2, 1, 3]
        
        # Delete should remove first occurrence
        lst.delete_key(1)
        assert list(lst) == [2, 1, 3]
    
    def test_none_values(self):
        """Test storing None values."""
        lst = CcpnList()
        lst.append(None)
        lst.append(1)
        lst.append(None)
        
        assert len(lst) == 3
        assert lst[0] is None
        assert lst[1] == 1
        assert lst[2] is None
    
    def test_large_list(self):
        """Test with large number of elements."""
        lst = CcpnList()
        
        n = 1000
        for i in range(n):
            lst.append(i)
        
        assert len(lst) == n
        assert lst[0] == 0
        assert lst[n-1] == n-1
        
        # Test finding in large list
        result = lst.find_key(500)
        assert result == 500


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
