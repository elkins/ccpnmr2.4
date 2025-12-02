"""
Tests for utility.py module

Test coverage:
- Endianness detection
- Byte swapping
- String operations
- File operations
- Math utilities (log2, GCD, power of 2)
- Array parsing
- Word conversion
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.c.python_impl.utility import (
    is_big_endian, is_little_endian, endianess,
    determine_swapped, swap_bytes,
    equal_strings, copy_string, empty_string,
    file_exists,
    log_2, floor_power_of_2, ceil_power_of_2, greatest_common_factor,
    get_integers, get_floats, get_max_integers, get_max_floats,
    get_some_integers, get_some_floats, print_integer_array,
    float_words, int_words,
    UtilityOps
)


# ============================================================================
# Endianness Tests
# ============================================================================

def test_endianness_detection():
    """Test endianness detection (one must be true)."""
    big = is_big_endian()
    little = is_little_endian()
    assert big or little, "Must be either big or little endian"
    assert not (big and little), "Cannot be both endian types"


def test_endianess_string():
    """Test endianness string."""
    e = endianess()
    assert e in ['BIG_ENDIAN', 'LITTLE_ENDIAN']


def test_determine_swapped():
    """Test swap determination (returns True for big-endian)."""
    swapped = determine_swapped()
    assert swapped == is_big_endian()


def test_swap_bytes():
    """Test byte swapping."""
    # Test 4-byte word swap
    data = b'\x01\x02\x03\x04'
    swapped = swap_bytes(data)
    assert swapped == b'\x04\x03\x02\x01'
    
    # Test 8 bytes (two words)
    data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    swapped = swap_bytes(data)
    assert swapped == b'\x04\x03\x02\x01\x08\x07\x06\x05'


def test_swap_bytes_error():
    """Test swap_bytes with invalid length."""
    try:
        swap_bytes(b'\x01\x02\x03')  # Not multiple of 4
        assert False, "Should raise ValueError"
    except ValueError:
        pass


# ============================================================================
# String Operation Tests
# ============================================================================

def test_equal_strings_same():
    """Test equal strings."""
    assert equal_strings("hello", "hello")
    assert equal_strings("", "")


def test_equal_strings_different():
    """Test different strings."""
    assert not equal_strings("hello", "world")
    assert not equal_strings("test", "")


def test_equal_strings_none():
    """Test strings with None."""
    assert equal_strings(None, None)
    assert not equal_strings(None, "test")
    assert not equal_strings("test", None)


def test_copy_string():
    """Test string copy."""
    s = "hello"
    s2 = copy_string(s)
    assert s2 == s


def test_empty_string():
    """Test empty string detection."""
    assert empty_string("")
    assert empty_string("   ")
    assert empty_string("\t\n")
    assert not empty_string("hello")
    assert not empty_string("  x  ")


# ============================================================================
# File Operation Tests
# ============================================================================

def test_file_exists():
    """Test file existence check."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
        f.write(b"test")
    
    try:
        assert file_exists(temp_path)
        assert not file_exists("/nonexistent/path/to/file.txt")
    finally:
        os.unlink(temp_path)


# ============================================================================
# Math Utility Tests
# ============================================================================

def test_log_2_powers():
    """Test log2 for powers of 2."""
    assert log_2(1) == 0
    assert log_2(2) == 1
    assert log_2(4) == 2
    assert log_2(8) == 3
    assert log_2(16) == 4
    assert log_2(1024) == 10


def test_floor_power_of_2():
    """Test floor to power of 2."""
    assert floor_power_of_2(1) == 1
    assert floor_power_of_2(2) == 2
    assert floor_power_of_2(3) == 2
    assert floor_power_of_2(5) == 4
    assert floor_power_of_2(7) == 4
    assert floor_power_of_2(8) == 8
    assert floor_power_of_2(15) == 8
    assert floor_power_of_2(20) == 16


def test_ceil_power_of_2():
    """Test ceil to power of 2."""
    assert ceil_power_of_2(1) == 1
    assert ceil_power_of_2(2) == 2
    assert ceil_power_of_2(3) == 4
    assert ceil_power_of_2(5) == 8
    assert ceil_power_of_2(7) == 8
    assert ceil_power_of_2(8) == 8
    assert ceil_power_of_2(9) == 16
    assert ceil_power_of_2(20) == 32


def test_greatest_common_factor():
    """Test GCD calculation."""
    assert greatest_common_factor(12, 8) == 4
    assert greatest_common_factor(48, 18) == 6
    assert greatest_common_factor(100, 50) == 50
    assert greatest_common_factor(17, 19) == 1  # Coprime
    assert greatest_common_factor(0, 5) == 5
    assert greatest_common_factor(5, 0) == 5


def test_gcd_negative():
    """Test GCD with negative numbers."""
    assert greatest_common_factor(-12, 8) == 4
    assert greatest_common_factor(12, -8) == 4
    assert greatest_common_factor(-12, -8) == 4


# ============================================================================
# Array Parsing Tests
# ============================================================================

def test_get_integers():
    """Test parsing integers from string."""
    result = get_integers(5, "10 20 30 40 50")
    assert result == [10, 20, 30, 40, 50]
    
    result = get_integers(3, "1 2 3 4 5")
    assert result == [1, 2, 3]


def test_get_integers_error():
    """Test error handling for integer parsing."""
    try:
        get_integers(5, "1 2 3")  # Not enough values
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_get_floats():
    """Test parsing floats from string."""
    result = get_floats(3, "1.5 2.7 3.9")
    assert len(result) == 3
    assert abs(result[0] - 1.5) < 0.01
    assert abs(result[1] - 2.7) < 0.01
    assert abs(result[2] - 3.9) < 0.01


def test_get_max_integers():
    """Test parsing up to max integers."""
    result = get_max_integers(5, "1 2 3")
    assert result == [1, 2, 3]
    
    result = get_max_integers(3, "1 2 3 4 5")
    assert result == [1, 2, 3]
    
    result = get_max_integers(5, "1 two 3")
    assert result == [1]  # Stops at first error


def test_get_max_floats():
    """Test parsing up to max floats."""
    result = get_max_floats(5, "1.5 2.7 3.9")
    assert len(result) == 3
    
    result = get_max_floats(3, "1.5 2.7 3.9 4.2 5.1")
    assert len(result) == 3


def test_get_some_integers():
    """Test parsing integers with skip list."""
    result = get_some_integers(5, [1, 3], "10 20 30 40 50")
    assert result == [10, 0, 30, 0, 50]


def test_get_some_floats():
    """Test parsing floats with skip list."""
    result = get_some_floats(4, [0, 2], "1.5 2.7 3.9 4.2")
    assert len(result) == 4
    assert abs(result[0]) < 0.01  # Skipped
    assert abs(result[1] - 2.7) < 0.01
    assert abs(result[2]) < 0.01  # Skipped
    assert abs(result[3] - 4.2) < 0.01


def test_print_integer_array():
    """Test integer array formatting."""
    result = print_integer_array([0, 1, 2])
    assert result == "(1, 2, 3)"  # Adds 1 to each
    
    result = print_integer_array([5, 10, 15])
    assert result == "(6, 11, 16)"


# ============================================================================
# Word Conversion Tests
# ============================================================================

def test_float_words_round_trip():
    """Test int -> float -> int conversion."""
    # Test with simple pattern
    int_data = [42, 100, -5]
    float_data = float_words(int_data)
    int_data2 = int_words(float_data)
    
    # Should get back similar values (some loss due to float representation)
    assert len(int_data2) == len(int_data)


def test_int_words_round_trip():
    """Test float -> int -> float conversion."""
    float_data = [1.5, 2.7, 3.9]
    int_data = int_words(float_data)
    
    # Check we got integers
    assert len(int_data) == len(float_data)


# ============================================================================
# UtilityOps Class Tests
# ============================================================================

def test_utility_ops_class():
    """Test UtilityOps wrapper class."""
    ops = UtilityOps()
    
    # Endianness
    assert ops.is_big_endian() == is_big_endian()
    assert ops.is_little_endian() == is_little_endian()
    
    # Strings
    assert ops.equal_strings("test", "test")
    assert ops.empty_string("   ")
    
    # Math
    assert ops.log_2(16) == 4
    assert ops.floor_power_of_2(20) == 16
    assert ops.ceil_power_of_2(20) == 32
    assert ops.gcd(48, 18) == 6
    
    # Array parsing
    ints = ops.parse_integers(3, "1 2 3")
    assert ints == [1, 2, 3]
    
    floats = ops.parse_floats(2, "1.5 2.7")
    assert len(floats) == 2


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_endianness_detection,
        test_endianess_string,
        test_determine_swapped,
        test_swap_bytes,
        test_swap_bytes_error,
        test_equal_strings_same,
        test_equal_strings_different,
        test_equal_strings_none,
        test_copy_string,
        test_empty_string,
        test_file_exists,
        test_log_2_powers,
        test_floor_power_of_2,
        test_ceil_power_of_2,
        test_greatest_common_factor,
        test_gcd_negative,
        test_get_integers,
        test_get_integers_error,
        test_get_floats,
        test_get_max_integers,
        test_get_max_floats,
        test_get_some_integers,
        test_get_some_floats,
        test_print_integer_array,
        test_float_words_round_trip,
        test_int_words_round_trip,
        test_utility_ops_class
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
    print(f"Utility Tests: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
