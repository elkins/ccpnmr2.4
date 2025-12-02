"""
Tests for int_array.py module

Test coverage:
- IntArray creation
- Copy operations
- Get/set operations
- Equality and hashing
- Dict-like interface
- Conversion to tuple/list
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.c.python_impl.int_array import (
    IntArray,
    new_int_array, copy_int_array, delete_int_array,
    equal_int_array, hash_int_array,
    MAX_NDIM
)


# ============================================================================
# Creation Tests
# ============================================================================

def test_create_int_array():
    """Test creating integer array."""
    arr = IntArray([1, 2, 3])
    assert arr.ndim == 3
    assert arr.values == [1, 2, 3]


def test_create_empty():
    """Test creating empty array."""
    arr = IntArray([])
    assert arr.ndim == 0
    assert arr.values == []


def test_create_too_large():
    """Test error for too many dimensions."""
    try:
        arr = IntArray([0] * (MAX_NDIM + 1))
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_new_int_array_function():
    """Test C-style creation function."""
    arr = new_int_array([4, 5, 6])
    assert arr.ndim == 3
    assert arr.values == [4, 5, 6]


# ============================================================================
# Copy Tests
# ============================================================================

def test_copy():
    """Test copying array."""
    arr1 = IntArray([1, 2, 3])
    arr2 = arr1.copy()
    
    assert arr1.values == arr2.values
    assert arr1 is not arr2  # Different objects
    assert arr1.values is not arr2.values  # Different lists


def test_copy_and_modify():
    """Test that copy is independent."""
    arr1 = IntArray([1, 2, 3])
    arr2 = arr1.copy()
    
    arr2[0] = 99
    
    assert arr1[0] == 1  # Original unchanged
    assert arr2[0] == 99  # Copy changed


def test_copy_int_array_function():
    """Test C-style copy function."""
    arr1 = IntArray([7, 8, 9])
    arr2 = copy_int_array(arr1)
    
    assert arr1.values == arr2.values
    assert arr1 is not arr2


def test_delete_int_array_function():
    """Test C-style delete function (no-op in Python)."""
    arr = IntArray([1, 2, 3])
    delete_int_array(arr)  # Should not crash


# ============================================================================
# Get/Set Tests
# ============================================================================

def test_get():
    """Test getting values."""
    arr = IntArray([10, 20, 30])
    
    assert arr.get(0) == 10
    assert arr.get(1) == 20
    assert arr.get(2) == 30


def test_get_out_of_bounds():
    """Test getting out of bounds returns 0."""
    arr = IntArray([1, 2, 3])
    
    assert arr.get(-1) == 0
    assert arr.get(10) == 0


def test_set():
    """Test setting values."""
    arr = IntArray([1, 2, 3])
    
    arr.set(0, 99)
    assert arr.get(0) == 99
    
    arr.set(1, 88)
    assert arr.get(1) == 88


def test_set_out_of_bounds():
    """Test setting out of bounds is ignored."""
    arr = IntArray([1, 2, 3])
    original = arr.values.copy()
    
    arr.set(-1, 99)
    arr.set(10, 88)
    
    assert arr.values == original  # Unchanged


def test_getitem_operator():
    """Test [] operator for getting."""
    arr = IntArray([10, 20, 30])
    
    assert arr[0] == 10
    assert arr[1] == 20
    assert arr[2] == 30


def test_setitem_operator():
    """Test [] operator for setting."""
    arr = IntArray([1, 2, 3])
    
    arr[0] = 99
    assert arr[0] == 99


# ============================================================================
# Equality Tests
# ============================================================================

def test_equality_same():
    """Test equality for identical arrays."""
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([1, 2, 3])
    
    assert arr1 == arr2


def test_equality_different_values():
    """Test inequality for different values."""
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([4, 5, 6])
    
    assert arr1 != arr2


def test_equality_different_dimensions():
    """Test inequality for different dimensions."""
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([1, 2])
    
    assert arr1 != arr2


def test_equality_not_int_array():
    """Test inequality with non-IntArray."""
    arr = IntArray([1, 2, 3])
    
    assert arr != [1, 2, 3]
    assert arr != (1, 2, 3)
    assert arr != "test"


def test_equal_int_array_function():
    """Test C-style equality function."""
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([1, 2, 3])
    arr3 = IntArray([4, 5, 6])
    
    assert equal_int_array(arr1, arr2)
    assert not equal_int_array(arr1, arr3)


# ============================================================================
# Hashing Tests
# ============================================================================

def test_hash():
    """Test hashing."""
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([1, 2, 3])
    arr3 = IntArray([4, 5, 6])
    
    # Same values -> same hash
    assert hash(arr1) == hash(arr2)
    
    # Different values -> (probably) different hash
    # Note: Hash collisions possible but unlikely for these values
    assert hash(arr1) != hash(arr3)


def test_hash_as_dict_key():
    """Test using IntArray as dictionary key."""
    arr1 = IntArray([1, 2, 3])
    arr2 = IntArray([1, 2, 3])
    arr3 = IntArray([4, 5, 6])
    
    data = {arr1: "first"}
    
    # Should find using arr2 (equal to arr1)
    assert data[arr2] == "first"
    
    # Add another key
    data[arr3] = "second"
    assert len(data) == 2


def test_hash_int_array_function():
    """Test C-style hash function."""
    arr = IntArray([1, 2, 3])
    
    h1 = hash_int_array(arr)
    h2 = hash(arr)
    
    assert h1 == h2


# ============================================================================
# Length and String Tests
# ============================================================================

def test_len():
    """Test length operator."""
    arr = IntArray([1, 2, 3, 4, 5])
    assert len(arr) == 5
    
    arr2 = IntArray([])
    assert len(arr2) == 0


def test_repr():
    """Test repr string."""
    arr = IntArray([1, 2, 3])
    r = repr(arr)
    
    assert "IntArray" in r
    assert "1" in r and "2" in r and "3" in r


def test_str():
    """Test string representation."""
    arr = IntArray([1, 2, 3])
    s = str(arr)
    
    # Should look like tuple
    assert s == "(1, 2, 3)"


# ============================================================================
# Conversion Tests
# ============================================================================

def test_to_tuple():
    """Test conversion to tuple."""
    arr = IntArray([1, 2, 3])
    t = arr.to_tuple()
    
    assert t == (1, 2, 3)
    assert isinstance(t, tuple)


def test_to_list():
    """Test conversion to list."""
    arr = IntArray([1, 2, 3])
    lst = arr.to_list()
    
    assert lst == [1, 2, 3]
    assert isinstance(lst, list)
    
    # Should be a copy
    lst[0] = 99
    assert arr[0] == 1  # Original unchanged


# ============================================================================
# Edge Cases
# ============================================================================

def test_single_value():
    """Test array with single value."""
    arr = IntArray([42])
    
    assert len(arr) == 1
    assert arr[0] == 42


def test_negative_values():
    """Test array with negative values."""
    arr = IntArray([-1, -2, -3])
    
    assert arr[0] == -1
    assert arr[1] == -2
    assert arr[2] == -3


def test_zero_values():
    """Test array of zeros."""
    arr = IntArray([0, 0, 0])
    
    assert all(v == 0 for v in arr.values)


def test_large_values():
    """Test array with large values."""
    arr = IntArray([1000000, 2000000, 3000000])
    
    assert arr[0] == 1000000
    assert arr[1] == 2000000


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_create_int_array,
        test_create_empty,
        test_create_too_large,
        test_new_int_array_function,
        test_copy,
        test_copy_and_modify,
        test_copy_int_array_function,
        test_delete_int_array_function,
        test_get,
        test_get_out_of_bounds,
        test_set,
        test_set_out_of_bounds,
        test_getitem_operator,
        test_setitem_operator,
        test_equality_same,
        test_equality_different_values,
        test_equality_different_dimensions,
        test_equality_not_int_array,
        test_equal_int_array_function,
        test_hash,
        test_hash_as_dict_key,
        test_hash_int_array_function,
        test_len,
        test_repr,
        test_str,
        test_to_tuple,
        test_to_list,
        test_single_value,
        test_negative_values,
        test_zero_values,
        test_large_values
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
    print(f"Int Array Tests: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
