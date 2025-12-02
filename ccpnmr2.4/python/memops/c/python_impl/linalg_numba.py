"""
Numba JIT-compiled implementation of linear algebra operations.

This module provides high-performance matrix operations using Numba's
JIT compilation. The implementations work on NumPy arrays for efficiency.

For small to medium matrices, Numba can approach or match C performance.
For large matrices (>100×100), NumPy's BLAS-optimized routines typically
dominate due to cache optimization and SIMD instructions.

Author: CCPN Team
License: LGPL
"""

import numpy as np

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback decorator
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@jit(nopython=True)
def matrix_matrix_multiply_numba(matrix_a, matrix_b, result):
    """
    Multiply two matrices: C = A × B (Numba JIT version).
    
    Uses in-place modification of result matrix for efficiency.
    
    Args:
        matrix_a: 2D NumPy array (n1 × n3)
        matrix_b: 2D NumPy array (n3 × n2)
        result: Pre-allocated 2D NumPy array for output (n1 × n2)
    """
    n1, n3 = matrix_a.shape
    n2 = matrix_b.shape[1]
    
    for i in range(n1):
        for j in range(n2):
            t = 0.0
            for k in range(n3):
                t += matrix_a[i, k] * matrix_b[k, j]
            result[i, j] = t


@jit(nopython=True)
def matrix_vector_multiply_numba(matrix, vector, result):
    """
    Multiply matrix by vector: y = A × x (Numba JIT version).
    
    Args:
        matrix: 2D NumPy array (n1 × n2)
        vector: 1D NumPy array (length n2)
        result: Pre-allocated 1D NumPy array for output (length n1)
    """
    n1, n2 = matrix.shape
    
    for i in range(n1):
        t = 0.0
        for j in range(n2):
            t += matrix[i, j] * vector[j]
        result[i] = t


@jit(nopython=True)
def matrix_transpose_numba(matrix, result):
    """
    Transpose a matrix: B = A^T (Numba JIT version).
    
    Args:
        matrix: 2D NumPy array (n2 × n1)
        result: Pre-allocated 2D NumPy array for output (n1 × n2)
    """
    n2, n1 = matrix.shape
    
    for i in range(n1):
        for j in range(n2):
            result[i, j] = matrix[j, i]


@jit(nopython=True)
def matrix_add_numba(matrix_a, matrix_b, result):
    """
    Add two matrices: C = A + B (Numba JIT version).
    
    Args:
        matrix_a: 2D NumPy array
        matrix_b: 2D NumPy array (same shape as A)
        result: Pre-allocated 2D NumPy array for output
    """
    n1, n2 = matrix_a.shape
    
    for i in range(n1):
        for j in range(n2):
            result[i, j] = matrix_a[i, j] + matrix_b[i, j]


@jit(nopython=True)
def scalar_multiply_numba(scalar, matrix, result):
    """
    Multiply matrix by scalar: B = c × A (Numba JIT version).
    
    Args:
        scalar: Scalar multiplier
        matrix: 2D NumPy array
        result: Pre-allocated 2D NumPy array for output
    """
    n1, n2 = matrix.shape
    
    for i in range(n1):
        for j in range(n2):
            result[i, j] = scalar * matrix[i, j]


@jit(nopython=True)
def trace_numba(matrix):
    """
    Calculate trace (sum of diagonal elements) (Numba JIT version).
    
    Args:
        matrix: Square NumPy array
        
    Returns:
        Sum of diagonal elements
    """
    n = min(matrix.shape[0], matrix.shape[1])
    total = 0.0
    
    for i in range(n):
        total += matrix[i, i]
    
    return total


class LinAlgOpsNumba:
    """
    Numba-accelerated linear algebra operations.
    
    This class provides a high-level API for JIT-compiled matrix operations.
    All operations work on NumPy arrays and pre-allocate result arrays for
    efficiency.
    """
    
    @staticmethod
    def matmul(matrix_a, matrix_b):
        """
        Matrix-matrix multiplication: C = A × B
        
        Args:
            matrix_a: NumPy array (n1 × n3)
            matrix_b: NumPy array (n3 × n2)
            
        Returns:
            NumPy array (n1 × n2)
        """
        matrix_a = np.asarray(matrix_a, dtype=np.float64)
        matrix_b = np.asarray(matrix_b, dtype=np.float64)
        
        if matrix_a.shape[1] != matrix_b.shape[0]:
            raise ValueError(f"Incompatible dimensions: {matrix_a.shape} and {matrix_b.shape}")
        
        result = np.empty((matrix_a.shape[0], matrix_b.shape[1]), dtype=np.float64)
        matrix_matrix_multiply_numba(matrix_a, matrix_b, result)
        return result
    
    @staticmethod
    def matvec(matrix, vector):
        """
        Matrix-vector multiplication: y = A × x
        
        Args:
            matrix: NumPy array (n1 × n2)
            vector: NumPy array (length n2)
            
        Returns:
            NumPy array (length n1)
        """
        matrix = np.asarray(matrix, dtype=np.float64)
        vector = np.asarray(vector, dtype=np.float64)
        
        if matrix.shape[1] != vector.shape[0]:
            raise ValueError(f"Incompatible dimensions: matrix {matrix.shape}, vector length {vector.shape[0]}")
        
        result = np.empty(matrix.shape[0], dtype=np.float64)
        matrix_vector_multiply_numba(matrix, vector, result)
        return result
    
    @staticmethod
    def transpose(matrix):
        """
        Matrix transpose: B = A^T
        
        Args:
            matrix: NumPy array (n2 × n1)
            
        Returns:
            NumPy array (n1 × n2)
        """
        matrix = np.asarray(matrix, dtype=np.float64)
        result = np.empty((matrix.shape[1], matrix.shape[0]), dtype=np.float64)
        matrix_transpose_numba(matrix, result)
        return result
    
    @staticmethod
    def identity(n):
        """
        Create n×n identity matrix.
        
        Args:
            n: Size of matrix
            
        Returns:
            NumPy identity matrix
        """
        return np.eye(n, dtype=np.float64)
    
    @staticmethod
    def zeros(n1, n2=None):
        """
        Create zero matrix.
        
        Args:
            n1: Number of rows
            n2: Number of columns (if None, creates n1×n1 matrix)
            
        Returns:
            NumPy zero matrix
        """
        if n2 is None:
            n2 = n1
        return np.zeros((n1, n2), dtype=np.float64)
    
    @staticmethod
    def trace(matrix):
        """
        Calculate trace (sum of diagonal elements).
        
        Args:
            matrix: Square NumPy array
            
        Returns:
            Sum of diagonal elements
        """
        matrix = np.asarray(matrix, dtype=np.float64)
        return trace_numba(matrix)
    
    @staticmethod
    def matrix_add(matrix_a, matrix_b):
        """
        Add two matrices: C = A + B
        
        Args:
            matrix_a: NumPy array
            matrix_b: NumPy array (same shape)
            
        Returns:
            NumPy array
        """
        matrix_a = np.asarray(matrix_a, dtype=np.float64)
        matrix_b = np.asarray(matrix_b, dtype=np.float64)
        
        if matrix_a.shape != matrix_b.shape:
            raise ValueError(f"Matrices must have same shape: {matrix_a.shape} vs {matrix_b.shape}")
        
        result = np.empty_like(matrix_a)
        matrix_add_numba(matrix_a, matrix_b, result)
        return result
    
    @staticmethod
    def scalar_multiply(scalar, matrix):
        """
        Multiply matrix by scalar: B = c × A
        
        Args:
            scalar: Scalar multiplier
            matrix: NumPy array
            
        Returns:
            NumPy array
        """
        matrix = np.asarray(matrix, dtype=np.float64)
        result = np.empty_like(matrix)
        scalar_multiply_numba(float(scalar), matrix, result)
        return result


# Module-level convenience functions

def matmul(matrix_a, matrix_b):
    """Matrix-matrix multiplication using Numba."""
    return LinAlgOpsNumba.matmul(matrix_a, matrix_b)


def matvec(matrix, vector):
    """Matrix-vector multiplication using Numba."""
    return LinAlgOpsNumba.matvec(matrix, vector)


def transpose(matrix):
    """Matrix transpose using Numba."""
    return LinAlgOpsNumba.transpose(matrix)


def identity(n):
    """Create identity matrix."""
    return LinAlgOpsNumba.identity(n)


def zeros(n1, n2=None):
    """Create zero matrix."""
    return LinAlgOpsNumba.zeros(n1, n2)


def trace(matrix):
    """Calculate matrix trace."""
    return LinAlgOpsNumba.trace(matrix)


def matrix_add(matrix_a, matrix_b):
    """Add two matrices."""
    return LinAlgOpsNumba.matrix_add(matrix_a, matrix_b)


def scalar_multiply(scalar, matrix):
    """Multiply matrix by scalar."""
    return LinAlgOpsNumba.scalar_multiply(scalar, matrix)
