"""
Tests for int_array.py - Integer array data structure
"""

import pytest
from memops.c.python_impl.int_array import (
    IntArray, new_int_array, copy_int_array, equal_int_array,
    hash_int_array, MAX_NDIM
)


class TestIntArrayCreation:
    """Test IntArray creation."""
    
    def test_create_empty(self):
        """Create empty IntArray."""
        arr = IntArray([])
        assert arr.ndim == 0
        assert len(arr) == 0
    
    def test_create_1d(self):
        """Create 1D IntArray."""
        arr = IntArray([5])
        assert arr.ndim == 1
        assert arr[0] == 5
    
    def test_create_2d(self):
        """Create 2D IntArray."""
        arr = IntArray([3, 4])
        assert arr.ndim == 2
        assert arr[0] == 3
        assert arr[1] == 4
    
    def test_create_multidim(self):
        """Create multi-dimensional IntArray."""
        arr = IntArray([1, 2, 3, 4, 5])
        assert arr.ndim == 5
        assert arr.values == [1, 2, 3, 4, 5]
    
    def test_create_max_dimensions(self):
        """Create IntArray with max dimensions."""
        values = list(range(MAX_NDIM))
        arr = IntArray(values)
        assert arr.ndim == MAX_NDIM
    
    def test_create_too_many_dimensions(self):
        """Creating with too many dimensions raises error."""
        with pytest.raises(ValueError):
            IntArray(list(range(MAX_NDIM + 1)))
    
    def test_values_are_copied(self):
        """Values are copied, not referenced."""
        original = [1, 2, 3]
        arr = IntArray(original)
        original[0] = 99
        
        assert arr[0] == 1  # Not affected by change


class TestIntArrayAccess:
    """Test IntArray element access."""
    
    def test_get_valid_index(self):
        """Get element at valid index."""
        arr = IntArray([10, 20, 30])
        assert arr.get(0) == 10
        assert arr.get(1) == 20
        assert arr.get(2) == 30
    
    def test_get_out_of_bounds(self):
        """Get out of bounds returns 0."""
        arr = IntArray([10, 20])
        assert arr.get(5) == 0
        assert arr.get(-1) == 0
    
    def test_set_valid_index(self):
        """Set element at valid index."""
        arr = IntArray([1, 2, 3])
        arr.set(1, 99)
        assert arr.get(1) == 99
    
    def test_set_out_of_bounds(self):
        """Set out of bounds does nothing."""
        arr = IntArray([1, 2, 3])
        arr.set(10, 99)
        assert arr.values == [1, 2, 3]
    
    def test_getitem_operator(self):
        """Test [] get operator."""
        arr = IntArray([5, 10, 15])
        assert arr[0] == 5
        assert arr[2] == 15
    
    def test_setitem_operator(self):
        """Test [] set operator."""
        arr = IntArray([1, 2, 3])
        arr[1] = 42
        assert arr[1] == 42


class TestIntArrayEquality:
    """Test IntArray equality."""
    
    def test_equal_same_values(self):
        """Arrays with same values are equal."""
        arr1 = IntArray([1, 2, 3])
        arr2 = IntArray([1, 2, 3])
        assert arr1 == arr2
    
    def test_not_equal_different_values(self):
        """Arrays with different values are not equal."""
        arr1 = IntArray([1, 2, 3])
        arr2 = IntArray([1, 2, 4])
        assert arr1 != arr2
    
    def test_not_equal_different_dimensions(self):
        """Arrays with different dimensions are not equal."""
        arr1 = IntArray([1, 2])
        arr2 = IntArray([1, 2, 3])
        assert arr1 != arr2
    
    def test_not_equal_to_other_types(self):
        """IntArray not equal to other types."""
        arr = IntArray([1, 2, 3])
        assert arr != [1, 2, 3]
        assert arr != (1, 2, 3)
        assert arr != "123"
    
    def test_equal_int_array_function(self):
        """Test equal_int_array function."""
        arr1 = IntArray([5, 10])
        arr2 = IntArray([5, 10])
        arr3 = IntArray([5, 11])
        
        assert equal_int_array(arr1, arr2)
        assert not equal_int_array(arr1, arr3)


class TestIntArrayHashing:
    """Test IntArray hashing."""
    
    def test_hash_deterministic(self):
        """Hash is deterministic."""
        arr = IntArray([1, 2, 3])
        h1 = hash(arr)
        h2 = hash(arr)
        assert h1 == h2
    
    def test_hash_same_values(self):
        """Same values give same hash."""
        arr1 = IntArray([1, 2, 3])
        arr2 = IntArray([1, 2, 3])
        assert hash(arr1) == hash(arr2)
    
    def test_hash_different_values(self):
        """Different values give different hashes (usually)."""
        arr1 = IntArray([1, 2, 3])
        arr2 = IntArray([1, 2, 4])
        # Hashes might collide, but usually don't
        assert hash(arr1) != hash(arr2)
    
    def test_hash_int_array_function(self):
        """Test hash_int_array function."""
        arr = IntArray([10, 20, 30])
        h1 = hash_int_array(arr)
        h2 = hash(arr)
        assert h1 == h2
    
    def test_use_as_dict_key(self):
        """IntArray can be used as dict key."""
        arr1 = IntArray([1, 2, 3])
        arr2 = IntArray([1, 2, 3])
        arr3 = IntArray([4, 5, 6])
        
        data = {arr1: "first", arr3: "third"}
        
        assert data[arr1] == "first"
        assert data[arr2] == "first"  # Same values, same hash
        assert data[arr3] == "third"


class TestIntArrayCopy:
    """Test IntArray copying."""
    
    def test_copy_method(self):
        """Test copy() method."""
        original = IntArray([1, 2, 3])
        copy = original.copy()
        
        assert copy == original
        assert copy is not original
        assert copy.values is not original.values
    
    def test_copy_independence(self):
        """Copy is independent of original."""
        original = IntArray([10, 20, 30])
        copy = original.copy()
        
        copy[1] = 99
        
        assert original[1] == 20
        assert copy[1] == 99
    
    def test_copy_int_array_function(self):
        """Test copy_int_array function."""
        original = IntArray([5, 10, 15])
        copy = copy_int_array(original)
        
        assert copy == original
        copy[0] = 100
        assert original[0] == 5


class TestIntArrayConversion:
    """Test IntArray conversions."""
    
    def test_to_tuple(self):
        """Convert to tuple."""
        arr = IntArray([1, 2, 3])
        tup = arr.to_tuple()
        assert tup == (1, 2, 3)
        assert isinstance(tup, tuple)
    
    def test_to_list(self):
        """Convert to list."""
        arr = IntArray([4, 5, 6])
        lst = arr.to_list()
        assert lst == [4, 5, 6]
        assert isinstance(lst, list)
    
    def test_to_list_independence(self):
        """to_list returns independent copy."""
        arr = IntArray([1, 2, 3])
        lst = arr.to_list()
        lst[0] = 99
        assert arr[0] == 1


class TestIntArrayStringRepresentation:
    """Test IntArray string representations."""
    
    def test_repr(self):
        """Test repr()."""
        arr = IntArray([1, 2, 3])
        r = repr(arr)
        assert "IntArray" in r
        assert "[1, 2, 3]" in r
    
    def test_str(self):
        """Test str()."""
        arr = IntArray([10, 20, 30])
        s = str(arr)
        assert s == "(10, 20, 30)"
    
    def test_str_single_element(self):
        """Test str() with single element."""
        arr = IntArray([42])
        assert str(arr) == "(42)"
    
    def test_str_empty(self):
        """Test str() with empty array."""
        arr = IntArray([])
        assert str(arr) == "()"


class TestFactoryFunctions:
    """Test C-style factory functions."""
    
    def test_new_int_array(self):
        """Test new_int_array function."""
        arr = new_int_array([1, 2, 3])
        assert isinstance(arr, IntArray)
        assert arr.ndim == 3
        assert arr.values == [1, 2, 3]


class TestIntArrayInHashTable:
    """Test IntArray usage in hash tables."""
    
    def test_as_hash_key(self):
        """Use IntArray as hash table key."""
        from memops.c.python_impl.hash_table import HashTable
        
        table = HashTable(
            equal_func=lambda a1, a2: a1 == a2,
            hash_func=lambda a: hash(a)
        )
        
        key1 = IntArray([1, 2, 3])
        key2 = IntArray([4, 5, 6])
        
        table[key1] = "data1"
        table[key2] = "data2"
        
        assert table[key1] == "data1"
        assert table[key2] == "data2"
    
    def test_hash_key_equivalence(self):
        """Equivalent IntArrays work as same key."""
        from memops.c.python_impl.hash_table import HashTable
        
        table = HashTable(
            equal_func=lambda a1, a2: a1 == a2,
            hash_func=lambda a: hash(a)
        )
        
        key1 = IntArray([10, 20])
        key2 = IntArray([10, 20])  # Same values
        
        table[key1] = "value"
        
        # key2 should find the same entry
        assert table[key2] == "value"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_values(self):
        """IntArray with zero values."""
        arr = IntArray([0, 0, 0])
        assert arr.ndim == 3
        assert all(v == 0 for v in arr.values)
    
    def test_negative_values(self):
        """IntArray with negative values."""
        arr = IntArray([-1, -2, -3])
        assert arr[-1] == 0  # Out of bounds
        assert arr[0] == -1
        assert arr[1] == -2
    
    def test_large_values(self):
        """IntArray with large values."""
        large = 1000000
        arr = IntArray([large, large + 1, large + 2])
        assert arr[0] == large
    
    def test_single_dimension(self):
        """Single dimension IntArray."""
        arr = IntArray([42])
        assert len(arr) == 1
        assert arr[0] == 42


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
