"""
Utility functions - Python implementation of utility.c

This module provides various utility functions including:
- Endianness detection and byte swapping
- String operations
- File operations
- Math utilities (log2, GCD, power of 2)
- Array parsing from strings
- Word conversion between int and float

Original: ccpnmr2.4/c/memops/global/utility.c
Python: Pure Python implementation with standard library
"""

import sys
import os
import struct
import math
from typing import List, Tuple, Optional


# ============================================================================
# Endianness Functions
# ============================================================================

def is_big_endian() -> bool:
    """Check if system uses big-endian byte order.
    
    Returns:
        True if big-endian, False if little-endian
    """
    return sys.byteorder == 'big'


def is_little_endian() -> bool:
    """Check if system uses little-endian byte order.
    
    Returns:
        True if little-endian, False if big-endian
    """
    return sys.byteorder == 'little'


def endianess() -> str:
    """Get system endianness as string constant.
    
    Returns:
        'BIG_ENDIAN' or 'LITTLE_ENDIAN'
    """
    return 'BIG_ENDIAN' if is_big_endian() else 'LITTLE_ENDIAN'


def determine_swapped() -> bool:
    """Determine if byte swapping is needed.
    
    Most modern systems are little-endian, so this returns True if big-endian.
    
    Returns:
        True if bytes need swapping (big-endian system)
    """
    return is_big_endian()


def swap_bytes(data: bytes) -> bytes:
    """Swap bytes in 4-byte words (assumes 4 bytes per word).
    
    Args:
        data: Bytes to swap (must be multiple of 4)
        
    Returns:
        Bytes with swapped endianness
        
    Raises:
        ValueError: If data length not multiple of 4
    """
    if len(data) % 4 != 0:
        raise ValueError(f"Data length {len(data)} not multiple of 4")
    
    # Swap bytes in each 4-byte word
    result = bytearray()
    for i in range(0, len(data), 4):
        word = data[i:i+4]
        result.extend(word[::-1])  # Reverse bytes in word
    
    return bytes(result)


def endian_fwrite(data: bytes, fp) -> None:
    """Write data to file with endianness handling.
    
    Swaps bytes if needed before writing.
    
    Args:
        data: Bytes to write
        fp: File pointer (opened in binary mode)
    """
    if determine_swapped():
        data = swap_bytes(data)
    fp.write(data)


# ============================================================================
# String Operations
# ============================================================================

def equal_strings(string1: Optional[str], string2: Optional[str]) -> bool:
    """Check if two strings are equal (handles None).
    
    Args:
        string1: First string (can be None)
        string2: Second string (can be None)
        
    Returns:
        True if strings are equal (including both None)
    """
    if string1 is None and string2 is None:
        return True
    if string1 is None or string2 is None:
        return False
    return string1 == string2


def copy_string(string: str) -> str:
    """Copy a string (Python strings are immutable, so just return).
    
    Args:
        string: String to copy
        
    Returns:
        Copy of string (in Python, same reference is fine)
    """
    return string


def empty_string(string: str) -> bool:
    """Check if string is empty or only whitespace.
    
    Args:
        string: String to check
        
    Returns:
        True if empty or all whitespace
    """
    return len(string.strip()) == 0


# ============================================================================
# File Operations
# ============================================================================

def file_exists(filepath: str) -> bool:
    """Check if file exists.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file exists and is readable
    """
    return os.path.isfile(filepath) and os.access(filepath, os.R_OK)


# ============================================================================
# Math Utilities
# ============================================================================

def log_2(n: int) -> int:
    """Calculate log base 2 of n (assumes n is power of 2).
    
    Args:
        n: Integer (should be power of 2)
        
    Returns:
        log2(n) as integer
    """
    if n <= 0:
        raise ValueError(f"log_2 requires positive integer, got {n}")
    
    m = -1
    while n > 0:
        n >>= 1
        m += 1
    return m


def floor_power_of_2(n: int) -> int:
    """Find largest power of 2 <= n.
    
    Args:
        n: Integer
        
    Returns:
        Largest power of 2 that is <= n
    """
    if n < 1:
        return 0
    
    m = -1
    q = n
    while q > 0:
        q >>= 1
        m += 1
    
    return 1 << m


def ceil_power_of_2(n: int) -> int:
    """Find smallest power of 2 >= n.
    
    Args:
        n: Integer
        
    Returns:
        Smallest power of 2 that is >= n
    """
    if n < 1:
        return 0
    
    m = -1
    q = n
    while q > 0:
        q >>= 1
        m += 1
    
    p = 1 << m
    return 2 * p if p < n else p


def greatest_common_factor(m: int, n: int) -> int:
    """Calculate GCD using Euclidean algorithm.
    
    Args:
        m: First integer
        n: Second integer
        
    Returns:
        Greatest common divisor
    """
    # Handle zero cases
    if m == 0:
        return n
    if n == 0:
        return m
    
    # Work with absolute values
    m = abs(m)
    n = abs(n)
    
    # Ensure m <= n
    if m > n:
        m, n = n, m
    
    # Euclidean algorithm
    p = n % m
    while p != 0:
        n = m
        m = p
        p = n % m
    
    return m


# ============================================================================
# Array I/O (parse from strings)
# ============================================================================

def get_integers(n: int, string: str) -> List[int]:
    """Parse exactly n integers from whitespace-separated string.
    
    Args:
        n: Number of integers expected
        string: String containing integers
        
    Returns:
        List of n integers
        
    Raises:
        ValueError: If cannot parse exactly n integers
    """
    tokens = string.split()
    if len(tokens) < n:
        raise ValueError(f"Expected {n} integers, found {len(tokens)}")
    
    try:
        return [int(tokens[i]) for i in range(n)]
    except ValueError as e:
        raise ValueError(f"Failed to parse integers: {e}")


def get_floats(n: int, string: str) -> List[float]:
    """Parse exactly n floats from whitespace-separated string.
    
    Args:
        n: Number of floats expected
        string: String containing floats
        
    Returns:
        List of n floats
        
    Raises:
        ValueError: If cannot parse exactly n floats
    """
    tokens = string.split()
    if len(tokens) < n:
        raise ValueError(f"Expected {n} floats, found {len(tokens)}")
    
    try:
        return [float(tokens[i]) for i in range(n)]
    except ValueError as e:
        raise ValueError(f"Failed to parse floats: {e}")


def get_max_integers(nmax: int, string: str) -> List[int]:
    """Parse up to nmax integers from string (returns however many found).
    
    Args:
        nmax: Maximum number of integers to parse
        string: String containing integers
        
    Returns:
        List of parsed integers (up to nmax)
    """
    tokens = string.split()
    result = []
    
    for i in range(min(nmax, len(tokens))):
        try:
            result.append(int(tokens[i]))
        except ValueError:
            break
    
    return result


def get_max_floats(nmax: int, string: str) -> List[float]:
    """Parse up to nmax floats from string (returns however many found).
    
    Args:
        nmax: Maximum number of floats to parse
        string: String containing floats
        
    Returns:
        List of parsed floats (up to nmax)
    """
    tokens = string.split()
    result = []
    
    for i in range(min(nmax, len(tokens))):
        try:
            result.append(float(tokens[i]))
        except ValueError:
            break
    
    return result


def get_some_integers(n: int, skip: List[int], string: str) -> List[int]:
    """Parse n integers from string, setting 0 for skipped indices.
    
    Args:
        n: Number of values expected
        skip: List of indices to skip (0-based)
        string: String containing integers
        
    Returns:
        List of n integers (0 for skipped indices)
        
    Raises:
        ValueError: If cannot parse enough tokens
    """
    tokens = string.split()
    if len(tokens) < n:
        raise ValueError(f"Expected {n} tokens, found {len(tokens)}")
    
    result = []
    skip_set = set(skip)
    
    for i in range(n):
        if i in skip_set:
            result.append(0)
        else:
            try:
                result.append(int(tokens[i]))
            except ValueError as e:
                raise ValueError(f"Failed to parse integer at index {i}: {e}")
    
    return result


def get_some_floats(n: int, skip: List[int], string: str) -> List[float]:
    """Parse n floats from string, setting 0.0 for skipped indices.
    
    Args:
        n: Number of values expected
        skip: List of indices to skip (0-based)
        string: String containing floats
        
    Returns:
        List of n floats (0.0 for skipped indices)
        
    Raises:
        ValueError: If cannot parse enough tokens
    """
    tokens = string.split()
    if len(tokens) < n:
        raise ValueError(f"Expected {n} tokens, found {len(tokens)}")
    
    result = []
    skip_set = set(skip)
    
    for i in range(n):
        if i in skip_set:
            result.append(0.0)
        else:
            try:
                result.append(float(tokens[i]))
            except ValueError as e:
                raise ValueError(f"Failed to parse float at index {i}: {e}")
    
    return result


def print_integer_array(array: List[int]) -> str:
    """Format integer array as string (adds 1 to each element like C version).
    
    Args:
        array: List of integers
        
    Returns:
        String like "(1, 2, 3)"
    """
    adjusted = [x + 1 for x in array]
    return "(" + ", ".join(str(x) for x in adjusted) + ")"


# ============================================================================
# Word Conversion (int <-> float binary representation)
# ============================================================================

def float_words(int_data: List[int]) -> List[float]:
    """Convert integer data to floats by reinterpreting binary representation.
    
    Takes integer values and reinterprets their binary representation as floats.
    
    Args:
        int_data: List of integers
        
    Returns:
        List of floats with same binary representation
    """
    result = []
    for i in int_data:
        # Pack as int, unpack as float (binary reinterpretation)
        bytes_data = struct.pack('i', i)
        f = struct.unpack('f', bytes_data)[0]
        result.append(f)
    return result


def int_words(float_data: List[float]) -> List[int]:
    """Convert float data to integers by rounding and reinterpreting.
    
    Takes floats and reinterprets their binary representation as integers.
    
    Args:
        float_data: List of floats
        
    Returns:
        List of integers (rounded from floats)
    """
    result = []
    for f in float_data:
        # Pack as float, unpack as int (binary reinterpretation)
        bytes_data = struct.pack('f', f)
        i = struct.unpack('i', bytes_data)[0]
        result.append(i)
    return result


# ============================================================================
# Utility Class Wrapper
# ============================================================================

class UtilityOps:
    """Convenience wrapper for utility operations."""
    
    # Endianness
    @staticmethod
    def is_big_endian() -> bool:
        return is_big_endian()
    
    @staticmethod
    def is_little_endian() -> bool:
        return is_little_endian()
    
    @staticmethod
    def endianess() -> str:
        return endianess()
    
    @staticmethod
    def swap_bytes(data: bytes) -> bytes:
        return swap_bytes(data)
    
    # String operations
    @staticmethod
    def equal_strings(s1: Optional[str], s2: Optional[str]) -> bool:
        return equal_strings(s1, s2)
    
    @staticmethod
    def empty_string(s: str) -> bool:
        return empty_string(s)
    
    # File operations
    @staticmethod
    def file_exists(path: str) -> bool:
        return file_exists(path)
    
    # Math utilities
    @staticmethod
    def log_2(n: int) -> int:
        return log_2(n)
    
    @staticmethod
    def floor_power_of_2(n: int) -> int:
        return floor_power_of_2(n)
    
    @staticmethod
    def ceil_power_of_2(n: int) -> int:
        return ceil_power_of_2(n)
    
    @staticmethod
    def gcd(m: int, n: int) -> int:
        return greatest_common_factor(m, n)
    
    # Array parsing
    @staticmethod
    def parse_integers(n: int, string: str) -> List[int]:
        return get_integers(n, string)
    
    @staticmethod
    def parse_floats(n: int, string: str) -> List[float]:
        return get_floats(n, string)


# Example usage
if __name__ == "__main__":
    # Endianness
    print(f"System endianness: {endianess()}")
    print(f"Is little-endian: {is_little_endian()}")
    
    # Math utilities
    print(f"\nlog_2(16) = {log_2(16)}")
    print(f"floor_power_of_2(20) = {floor_power_of_2(20)}")
    print(f"ceil_power_of_2(20) = {ceil_power_of_2(20)}")
    print(f"gcd(48, 18) = {greatest_common_factor(48, 18)}")
    
    # Array parsing
    ints = get_integers(5, "10 20 30 40 50")
    print(f"\nParsed integers: {ints}")
    print(f"Formatted: {print_integer_array(ints)}")
    
    floats = get_floats(3, "1.5 2.7 3.9")
    print(f"Parsed floats: {floats}")
    
    # String operations
    print(f"\nequal_strings('test', 'test'): {equal_strings('test', 'test')}")
    print(f"empty_string('   '): {empty_string('   ')}")
    print(f"file_exists('utility.py'): {file_exists('utility.py')}")
