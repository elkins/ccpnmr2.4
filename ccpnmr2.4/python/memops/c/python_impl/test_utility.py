"""
Tests for utility.py - General utility functions
"""

import pytest
import sys
import tempfile
import os
from memops.c.python_impl.utility import (
    is_big_endian, is_little_endian, endianess, determine_swapped,
    swap_bytes, equal_strings, empty_string, file_exists,
    log_2, floor_power_of_2, ceil_power_of_2, greatest_common_factor,
    get_integers, get_floats, get_max_integers, get_max_floats,
    get_some_integers, get_some_floats, print_integer_array,
    float_words, int_words, UtilityOps
)


class TestEndianness:
    """Test endianness detection."""
    
    def test_big_or_little_endian(self):
        """System must be either big or little endian."""
        assert is_big_endian() or is_little_endian()
        assert not (is_big_endian() and is_little_endian())
    
    def test_endianess_string(self):
        """Endianess string matches boolean checks."""
        result = endianess()
        assert result in ['BIG_ENDIAN', 'LITTLE_ENDIAN']
        
        if is_big_endian():
            assert result == 'BIG_ENDIAN'
        else:
            assert result == 'LITTLE_ENDIAN'
    
    def test_determine_swapped(self):
        """Swap determination matches endianness."""
        # Most modern systems are little-endian
        if is_little_endian():
            assert not determine_swapped()
        else:
            assert determine_swapped()
    
    def test_swap_bytes_4byte_words(self):
        """Test byte swapping for 4-byte words."""
        original = b'\x01\x02\x03\x04'
        swapped = swap_bytes(original)
        assert swapped == b'\x04\x03\x02\x01'
    
    def test_swap_bytes_multiple_words(self):
        """Test byte swapping for multiple 4-byte words."""
        original = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        swapped = swap_bytes(original)
        assert swapped == b'\x04\x03\x02\x01\x08\x07\x06\x05'
    
    def test_swap_bytes_error_on_bad_length(self):
        """Swap bytes should fail if not multiple of 4."""
        with pytest.raises(ValueError):
            swap_bytes(b'\x01\x02\x03')


class TestStringOperations:
    """Test string utility functions."""
    
    def test_equal_strings_both_same(self):
        """Equal strings return True."""
        assert equal_strings("test", "test")
        assert equal_strings("", "")
    
    def test_equal_strings_different(self):
        """Different strings return False."""
        assert not equal_strings("test", "TEST")
        assert not equal_strings("abc", "def")
    
    def test_equal_strings_both_none(self):
        """Both None counts as equal."""
        assert equal_strings(None, None)
    
    def test_equal_strings_one_none(self):
        """One None returns False."""
        assert not equal_strings("test", None)
        assert not equal_strings(None, "test")
    
    def test_empty_string_whitespace(self):
        """Whitespace-only strings count as empty."""
        assert empty_string("")
        assert empty_string("   ")
        assert empty_string("\t\n")
    
    def test_empty_string_content(self):
        """Strings with content are not empty."""
        assert not empty_string("a")
        assert not empty_string("  text  ")


class TestFileOperations:
    """Test file utility functions."""
    
    def test_file_exists_real_file(self):
        """Real files should exist."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            assert file_exists(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_file_exists_nonexistent(self):
        """Non-existent files should not exist."""
        assert not file_exists("/nonexistent/path/to/file.txt")
    
    def test_file_exists_directory(self):
        """Directories should not count as files."""
        assert not file_exists("/tmp")


class TestMathUtilities:
    """Test mathematical utility functions."""
    
    def test_log_2_powers_of_2(self):
        """Log2 of powers of 2."""
        assert log_2(1) == 0
        assert log_2(2) == 1
        assert log_2(4) == 2
        assert log_2(8) == 3
        assert log_2(16) == 4
        assert log_2(1024) == 10
    
    def test_log_2_error_on_zero(self):
        """Log2 of zero should raise error."""
        with pytest.raises(ValueError):
            log_2(0)
    
    def test_log_2_error_on_negative(self):
        """Log2 of negative should raise error."""
        with pytest.raises(ValueError):
            log_2(-5)
    
    def test_floor_power_of_2(self):
        """Floor to power of 2."""
        assert floor_power_of_2(1) == 1
        assert floor_power_of_2(3) == 2
        assert floor_power_of_2(5) == 4
        assert floor_power_of_2(15) == 8
        assert floor_power_of_2(16) == 16
        assert floor_power_of_2(20) == 16
        assert floor_power_of_2(100) == 64
    
    def test_floor_power_of_2_edge_cases(self):
        """Floor power of 2 edge cases."""
        assert floor_power_of_2(0) == 0
        assert floor_power_of_2(-5) == 0
    
    def test_ceil_power_of_2(self):
        """Ceiling to power of 2."""
        assert ceil_power_of_2(1) == 1
        assert ceil_power_of_2(3) == 4
        assert ceil_power_of_2(5) == 8
        assert ceil_power_of_2(15) == 16
        assert ceil_power_of_2(16) == 16
        assert ceil_power_of_2(20) == 32
        assert ceil_power_of_2(100) == 128
    
    def test_ceil_power_of_2_edge_cases(self):
        """Ceiling power of 2 edge cases."""
        assert ceil_power_of_2(0) == 0
        assert ceil_power_of_2(-5) == 0
    
    def test_greatest_common_factor(self):
        """GCD calculations."""
        assert greatest_common_factor(48, 18) == 6
        assert greatest_common_factor(100, 50) == 50
        assert greatest_common_factor(17, 19) == 1  # Coprime
        assert greatest_common_factor(0, 5) == 5
        assert greatest_common_factor(5, 0) == 5
    
    def test_gcd_negative_numbers(self):
        """GCD with negative numbers."""
        assert greatest_common_factor(-48, 18) == 6
        assert greatest_common_factor(48, -18) == 6
        assert greatest_common_factor(-48, -18) == 6


class TestArrayParsing:
    """Test array parsing from strings."""
    
    def test_get_integers_basic(self):
        """Parse integers from string."""
        result = get_integers(5, "10 20 30 40 50")
        assert result == [10, 20, 30, 40, 50]
    
    def test_get_integers_negative(self):
        """Parse negative integers."""
        result = get_integers(3, "-5 0 5")
        assert result == [-5, 0, 5]
    
    def test_get_integers_error_not_enough(self):
        """Error if not enough integers."""
        with pytest.raises(ValueError):
            get_integers(5, "10 20 30")
    
    def test_get_integers_extra_ignored(self):
        """Extra integers are ignored."""
        result = get_integers(3, "10 20 30 40 50")
        assert result == [10, 20, 30]
    
    def test_get_floats_basic(self):
        """Parse floats from string."""
        result = get_floats(4, "1.5 2.7 3.9 4.1")
        assert result == [1.5, 2.7, 3.9, 4.1]
    
    def test_get_floats_scientific(self):
        """Parse scientific notation."""
        result = get_floats(3, "1.5e2 -3.7e-1 0.0")
        assert abs(result[0] - 150.0) < 1e-10
        assert abs(result[1] - (-0.37)) < 1e-10
        assert result[2] == 0.0
    
    def test_get_max_integers_full(self):
        """Parse up to max integers (all available)."""
        result = get_max_integers(10, "1 2 3 4 5")
        assert result == [1, 2, 3, 4, 5]
    
    def test_get_max_integers_limited(self):
        """Parse up to max integers (limited)."""
        result = get_max_integers(3, "1 2 3 4 5")
        assert result == [1, 2, 3]
    
    def test_get_max_floats(self):
        """Parse up to max floats."""
        result = get_max_floats(3, "1.1 2.2 3.3 4.4")
        assert result == [1.1, 2.2, 3.3]
    
    def test_get_some_integers_with_skip(self):
        """Parse integers with skipped indices."""
        result = get_some_integers(5, [1, 3], "10 20 30 40 50")
        assert result == [10, 0, 30, 0, 50]
    
    def test_get_some_floats_with_skip(self):
        """Parse floats with skipped indices."""
        result = get_some_floats(4, [0, 2], "1.1 2.2 3.3 4.4")
        assert result == [0.0, 2.2, 0.0, 4.4]
    
    def test_print_integer_array(self):
        """Format integer array as string."""
        result = print_integer_array([0, 1, 2])
        assert result == "(1, 2, 3)"  # Adds 1 to each element


class TestWordConversion:
    """Test int/float word conversion."""
    
    def test_float_words_roundtrip(self):
        """Convert int -> float -> int roundtrip."""
        original = [100, 200, 300]
        floats = float_words(original)
        recovered = int_words(floats)
        # Binary reinterpretation, should be exact
        assert recovered == original
    
    def test_int_words_roundtrip(self):
        """Convert float -> int -> float roundtrip."""
        import struct
        
        # Create some float values
        original = [1.5, 2.7, 3.9]
        ints = int_words(original)
        recovered = float_words(ints)
        
        # Should recover original floats
        for i in range(len(original)):
            assert abs(recovered[i] - original[i]) < 1e-6


class TestUtilityOpsClass:
    """Test UtilityOps wrapper class."""
    
    def test_is_little_endian(self):
        """Test UtilityOps.is_little_endian."""
        assert UtilityOps.is_little_endian() == is_little_endian()
    
    def test_log_2(self):
        """Test UtilityOps.log_2."""
        assert UtilityOps.log_2(16) == 4
    
    def test_gcd(self):
        """Test UtilityOps.gcd."""
        assert UtilityOps.gcd(48, 18) == 6
    
    def test_parse_integers(self):
        """Test UtilityOps.parse_integers."""
        result = UtilityOps.parse_integers(3, "10 20 30")
        assert result == [10, 20, 30]
    
    def test_parse_floats(self):
        """Test UtilityOps.parse_floats."""
        result = UtilityOps.parse_floats(3, "1.5 2.5 3.5")
        assert result == [1.5, 2.5, 3.5]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_string_parsing(self):
        """Parse from empty string should fail."""
        with pytest.raises(ValueError):
            get_integers(3, "")
    
    def test_gcd_both_zero(self):
        """GCD of (0, 0) should return 0."""
        assert greatest_common_factor(0, 0) == 0
    
    def test_power_of_2_large_values(self):
        """Power of 2 functions with large values."""
        large = 1000000
        floor_p2 = floor_power_of_2(large)
        ceil_p2 = ceil_power_of_2(large)
        
        assert floor_p2 <= large < floor_p2 * 2
        assert ceil_p2 // 2 < large <= ceil_p2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
