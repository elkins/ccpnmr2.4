"""
Numba JIT-compiled implementation of random number generation.

This module provides high-performance random number generation using
Numba's JIT compilation. The implementation uses the same Linear
Congruential Generator (LCG) algorithm as the C code for compatibility.

Key performance optimizations:
1. @jit(nopython=True) for native code generation
2. NumPy arrays for efficient vectorized operations
3. Pre-allocation to minimize memory operations

The Numba version should approach C performance while maintaining
the simplicity of Python code.

Author: CCPN Team
License: LGPL
"""

import math
import numpy as np

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback decorator that does nothing
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# LCG parameters (same as C and pure Python)
RAN_ARRAY_SIZE = 123

M1 = 259200
A1 = 7141
C1 = 54773

M2 = 134456
A2 = 8121
C2 = 28411

M3 = 243000
A3 = 4561
C3 = 51349

R1 = 1.0 / M1
R2 = 1.0 / M2

TWOPI = 2.0 * math.pi


@jit(nopython=True)
def _init_seed_numba(seed, ran_array):
    """
    Initialize LCG states and shuffle buffer (Numba JIT version).
    
    Args:
        seed: Unsigned integer seed
        ran_array: Pre-allocated array for shuffle buffer
        
    Returns:
        Tuple of (x1, x2, x3) initial states
    """
    # Initialize LCG states
    x1 = (C1 + seed) % M1
    x1 = (A1 * x1 + C1) % M1
    x2 = x1 % M2
    x1 = (A1 * x1 + C1) % M1
    x3 = x1 % M3
    
    # Fill shuffle buffer
    for i in range(RAN_ARRAY_SIZE):
        x1 = (A1 * x1 + C1) % M1
        x2 = (A2 * x2 + C2) % M2
        ran_array[i] = (x1 + x2 * R2) * R1
    
    return x1, x2, x3


@jit(nopython=True)
def _uniform01_numba(x1, x2, x3, ran_array):
    """
    Generate single uniform random number (Numba JIT version).
    
    Args:
        x1, x2, x3: LCG states
        ran_array: Shuffle buffer
        
    Returns:
        Tuple of (random_value, new_x1, new_x2, new_x3)
    """
    # Advance all three LCGs
    x1 = (A1 * x1 + C1) % M1
    x2 = (A2 * x2 + C2) % M2
    x3 = (A3 * x3 + C3) % M3
    
    # Use x3 to select from shuffle buffer
    ind = (RAN_ARRAY_SIZE * x3) // M3
    r = ran_array[ind]
    
    # Refill buffer position
    ran_array[ind] = (x1 + x2 * R2) * R1
    
    return r, x1, x2, x3


@jit(nopython=True)
def _uniform01_array_numba(n, x1, x2, x3, ran_array, result):
    """
    Generate array of uniform random numbers (Numba JIT version).
    
    Args:
        n: Number of values to generate
        x1, x2, x3: LCG states
        ran_array: Shuffle buffer
        result: Pre-allocated output array
        
    Returns:
        Tuple of (new_x1, new_x2, new_x3)
    """
    for i in range(n):
        # Advance all three LCGs
        x1 = (A1 * x1 + C1) % M1
        x2 = (A2 * x2 + C2) % M2
        x3 = (A3 * x3 + C3) % M3
        
        # Use x3 to select from shuffle buffer
        ind = (RAN_ARRAY_SIZE * x3) // M3
        result[i] = ran_array[ind]
        
        # Refill buffer position
        ran_array[ind] = (x1 + x2 * R2) * R1
    
    return x1, x2, x3


@jit(nopython=True)
def _uniform_array_numba(n, a, b, x1, x2, x3, ran_array, result):
    """
    Generate array of uniform random numbers in [a, b).
    
    Args:
        n: Number of values
        a, b: Range bounds
        x1, x2, x3: LCG states
        ran_array: Shuffle buffer
        result: Pre-allocated output array
        
    Returns:
        Tuple of (new_x1, new_x2, new_x3)
    """
    scale = b - a
    
    for i in range(n):
        x1 = (A1 * x1 + C1) % M1
        x2 = (A2 * x2 + C2) % M2
        x3 = (A3 * x3 + C3) % M3
        
        ind = (RAN_ARRAY_SIZE * x3) // M3
        result[i] = a + scale * ran_array[ind]
        ran_array[ind] = (x1 + x2 * R2) * R1
    
    return x1, x2, x3


@jit(nopython=True)
def _normal01_numba(x1, x2, x3, ran_array, flag, next_value):
    """
    Generate single standard normal random number (Numba JIT version).
    
    Uses Box-Muller transform.
    
    Args:
        x1, x2, x3: LCG states
        ran_array: Shuffle buffer
        flag: Boolean indicating if cached value available
        next_value: Cached normal value from previous call
        
    Returns:
        Tuple of (random_value, new_x1, new_x2, new_x3, new_flag, new_next_value)
    """
    if flag:
        # Generate new pair using Box-Muller
        
        # Get u1, ensuring it's not zero
        u1, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
        while u1 == 0.0:
            u1, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
        
        # Get u2
        u2, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
        
        # Box-Muller transform
        r = math.sqrt(-2.0 * math.log(u1))
        theta = TWOPI * u2
        
        y = r * math.cos(theta)
        next_value = r * math.sin(theta)
        flag = False
        
        return y, x1, x2, x3, flag, next_value
    else:
        # Return cached value
        flag = True
        return next_value, x1, x2, x3, flag, next_value


@jit(nopython=True)
def _normal01_array_numba(n, x1, x2, x3, ran_array, flag, next_value, result):
    """
    Generate array of standard normal random numbers (Numba JIT version).
    
    Args:
        n: Number of values
        x1, x2, x3: LCG states
        ran_array: Shuffle buffer
        flag: Boolean for cached value
        next_value: Cached value
        result: Pre-allocated output array
        
    Returns:
        Tuple of (new_x1, new_x2, new_x3, new_flag, new_next_value)
    """
    for i in range(n):
        if flag:
            # Generate new pair
            u1, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
            while u1 == 0.0:
                u1, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
            
            u2, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
            
            r = math.sqrt(-2.0 * math.log(u1))
            theta = TWOPI * u2
            
            result[i] = r * math.cos(theta)
            next_value = r * math.sin(theta)
            flag = False
        else:
            # Use cached value
            result[i] = next_value
            flag = True
    
    return x1, x2, x3, flag, next_value


@jit(nopython=True)
def _normal_array_numba(n, mean, std_dev, x1, x2, x3, ran_array, flag, next_value, result):
    """
    Generate array of normal random numbers with specified parameters.
    
    Args:
        n: Number of values
        mean: Distribution mean
        std_dev: Distribution standard deviation
        x1, x2, x3: LCG states
        ran_array: Shuffle buffer
        flag: Boolean for cached value
        next_value: Cached value
        result: Pre-allocated output array
        
    Returns:
        Tuple of (new_x1, new_x2, new_x3, new_flag, new_next_value)
    """
    for i in range(n):
        if flag:
            u1, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
            while u1 == 0.0:
                u1, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
            
            u2, x1, x2, x3 = _uniform01_numba(x1, x2, x3, ran_array)
            
            r = math.sqrt(-2.0 * math.log(u1))
            theta = TWOPI * u2
            
            result[i] = mean + std_dev * r * math.cos(theta)
            next_value = r * math.sin(theta)
            flag = False
        else:
            result[i] = mean + std_dev * next_value
            flag = True
    
    return x1, x2, x3, flag, next_value


class RandomGeneratorNumba:
    """
    Numba-accelerated random number generator.
    
    Maintains state for the RNG and provides high-level API
    for generating random numbers using JIT-compiled functions.
    """
    
    def __init__(self, seed=123456):
        """Initialize with seed."""
        self.ran_array = np.zeros(RAN_ARRAY_SIZE, dtype=np.float64)
        self.normal_flag = True
        self.normal_next = 0.0
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        
        self.set_seed(seed)
    
    def set_seed(self, seed):
        """Set the seed and reinitialize state."""
        self.x1, self.x2, self.x3 = _init_seed_numba(seed, self.ran_array)
        self.normal_flag = True
        self.normal_next = 0.0
    
    def uniform01(self):
        """Generate single uniform random number in [0, 1)."""
        r, self.x1, self.x2, self.x3 = _uniform01_numba(
            self.x1, self.x2, self.x3, self.ran_array
        )
        return r
    
    def uniform(self, a, b):
        """Generate uniform random number in [a, b)."""
        return a + (b - a) * self.uniform01()
    
    def normal01(self):
        """Generate standard normal random number."""
        r, self.x1, self.x2, self.x3, self.normal_flag, self.normal_next = _normal01_numba(
            self.x1, self.x2, self.x3, self.ran_array,
            self.normal_flag, self.normal_next
        )
        return r
    
    def normal(self, mean, std_dev):
        """Generate normal random number with specified mean and std dev."""
        return mean + std_dev * self.normal01()
    
    def uniform01_array(self, n):
        """Generate array of uniform random numbers in [0, 1)."""
        result = np.empty(n, dtype=np.float64)
        self.x1, self.x2, self.x3 = _uniform01_array_numba(
            n, self.x1, self.x2, self.x3, self.ran_array, result
        )
        return result
    
    def uniform_array(self, n, a, b):
        """Generate array of uniform random numbers in [a, b)."""
        result = np.empty(n, dtype=np.float64)
        self.x1, self.x2, self.x3 = _uniform_array_numba(
            n, a, b, self.x1, self.x2, self.x3, self.ran_array, result
        )
        return result
    
    def normal01_array(self, n):
        """Generate array of standard normal random numbers."""
        result = np.empty(n, dtype=np.float64)
        self.x1, self.x2, self.x3, self.normal_flag, self.normal_next = _normal01_array_numba(
            n, self.x1, self.x2, self.x3, self.ran_array,
            self.normal_flag, self.normal_next, result
        )
        return result
    
    def normal_array(self, n, mean, std_dev):
        """Generate array of normal random numbers."""
        result = np.empty(n, dtype=np.float64)
        self.x1, self.x2, self.x3, self.normal_flag, self.normal_next = _normal_array_numba(
            n, mean, std_dev, self.x1, self.x2, self.x3, self.ran_array,
            self.normal_flag, self.normal_next, result
        )
        return result


# Global generator instance
_global_generator_numba = RandomGeneratorNumba()


# Module-level convenience functions

def set_seed(seed):
    """Set seed for global generator."""
    _global_generator_numba.set_seed(seed)


def uniform01():
    """Generate uniform random number in [0, 1)."""
    return _global_generator_numba.uniform01()


def uniform(a, b):
    """Generate uniform random number in [a, b)."""
    return _global_generator_numba.uniform(a, b)


def normal01():
    """Generate standard normal random number."""
    return _global_generator_numba.normal01()


def normal(mean, std_dev):
    """Generate normal random number."""
    return _global_generator_numba.normal(mean, std_dev)


def uniform01_array(n):
    """Generate array of uniform random numbers."""
    return _global_generator_numba.uniform01_array(n)


def uniform_array(n, a, b):
    """Generate array of uniform random numbers in [a, b)."""
    return _global_generator_numba.uniform_array(n, a, b)


def normal01_array(n):
    """Generate array of standard normal random numbers."""
    return _global_generator_numba.normal01_array(n)


def normal_array(n, mean, std_dev):
    """Generate array of normal random numbers."""
    return _global_generator_numba.normal_array(n, mean, std_dev)
