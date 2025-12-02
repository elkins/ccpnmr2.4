"""
Pure Python implementation of linear algebra operations.

This module implements basic matrix operations used in the original C code
(linalg.c). These are fundamental operations for NMR data processing and
structure calculations.

The implementations use straightforward nested loops matching the C code's
algorithm. For large matrices, NumPy's BLAS-optimized routines will be
significantly faster.

Key operations:
1. Matrix-matrix multiplication: C = A × B
2. Matrix-vector multiplication: y = A × x
3. Matrix transpose: A^T

Original C signatures:
- matrix_matrix_multiply(result, A, B, n1, n2, n3)
  where A is (n1×n3), B is (n3×n2), result is (n1×n2)
- matrix_vector_multiply(result, A, x, n1, n2)
  where A is (n1×n2), x is length n2, result is length n1
- matrix_transpose(result, A, n1, n2)
  where A is (n2×n1), result is (n1×n2)

Author: CCPN Team
License: LGPL
"""


def matrix_matrix_multiply(matrix_a, matrix_b):
    """
    Multiply two matrices: C = A × B
    
    Uses the standard O(n³) algorithm with three nested loops.
    For large matrices, NumPy's BLAS implementation is much faster.
    
    Args:
        matrix_a: 2D list representing matrix A (n1 × n3)
        matrix_b: 2D list representing matrix B (n3 × n2)
        
    Returns:
        2D list representing result matrix C (n1 × n2)
        
    Raises:
        ValueError: If matrix dimensions are incompatible
        
    Example:
        >>> A = [[1, 2], [3, 4]]
        >>> B = [[5, 6], [7, 8]]
        >>> C = matrix_matrix_multiply(A, B)
        >>> # C = [[19, 22], [43, 50]]
    """
    if not matrix_a or not matrix_a[0]:
        raise ValueError("matrix_a cannot be empty")
    if not matrix_b or not matrix_b[0]:
        raise ValueError("matrix_b cannot be empty")
    
    n1 = len(matrix_a)      # rows of A
    n3 = len(matrix_a[0])   # cols of A
    n3_b = len(matrix_b)    # rows of B
    n2 = len(matrix_b[0])   # cols of B
    
    if n3 != n3_b:
        raise ValueError(f"Incompatible dimensions: A is {n1}×{n3}, B is {n3_b}×{n2}")
    
    # Initialize result matrix
    result = [[0.0 for _ in range(n2)] for _ in range(n1)]
    
    # Triple nested loop: O(n1 × n2 × n3)
    for i in range(n1):
        for j in range(n2):
            t = 0.0
            for k in range(n3):
                t += matrix_a[i][k] * matrix_b[k][j]
            result[i][j] = t
    
    return result


def matrix_vector_multiply(matrix, vector):
    """
    Multiply matrix by vector: y = A × x
    
    Args:
        matrix: 2D list representing matrix A (n1 × n2)
        vector: 1D list representing vector x (length n2)
        
    Returns:
        1D list representing result vector y (length n1)
        
    Raises:
        ValueError: If dimensions are incompatible
        
    Example:
        >>> A = [[1, 2], [3, 4], [5, 6]]
        >>> x = [7, 8]
        >>> y = matrix_vector_multiply(A, x)
        >>> # y = [23, 53, 83]
    """
    if not matrix or not matrix[0]:
        raise ValueError("matrix cannot be empty")
    if not vector:
        raise ValueError("vector cannot be empty")
    
    n1 = len(matrix)      # rows
    n2 = len(matrix[0])   # cols
    
    if len(vector) != n2:
        raise ValueError(f"Incompatible dimensions: matrix is {n1}×{n2}, vector has length {len(vector)}")
    
    # Initialize result vector
    result = [0.0] * n1
    
    # Double nested loop: O(n1 × n2)
    for i in range(n1):
        t = 0.0
        for j in range(n2):
            t += matrix[i][j] * vector[j]
        result[i] = t
    
    return result


def matrix_transpose(matrix):
    """
    Transpose a matrix: B = A^T
    
    Args:
        matrix: 2D list representing matrix A (n2 × n1)
        
    Returns:
        2D list representing transposed matrix B (n1 × n2)
        
    Example:
        >>> A = [[1, 2, 3], [4, 5, 6]]
        >>> B = matrix_transpose(A)
        >>> # B = [[1, 4], [2, 5], [3, 6]]
    """
    if not matrix:
        raise ValueError("matrix cannot be empty")
    if not matrix[0]:
        # Handle edge case of empty rows
        return [[]]
    
    n2 = len(matrix)      # original rows
    n1 = len(matrix[0])   # original cols
    
    # Initialize transposed matrix
    result = [[0.0 for _ in range(n2)] for _ in range(n1)]
    
    # Double nested loop: O(n1 × n2)
    for i in range(n1):
        for j in range(n2):
            result[i][j] = matrix[j][i]
    
    return result


class LinAlgOps:
    """
    Wrapper class providing linear algebra operations.
    
    This class provides a convenient interface for matrix operations,
    similar to how the C code might be used. All methods are static.
    """
    
    @staticmethod
    def matmul(matrix_a, matrix_b):
        """Matrix-matrix multiplication: C = A × B"""
        return matrix_matrix_multiply(matrix_a, matrix_b)
    
    @staticmethod
    def matvec(matrix, vector):
        """Matrix-vector multiplication: y = A × x"""
        return matrix_vector_multiply(matrix, vector)
    
    @staticmethod
    def transpose(matrix):
        """Matrix transpose: B = A^T"""
        return matrix_transpose(matrix)
    
    @staticmethod
    def identity(n):
        """
        Create n×n identity matrix.
        
        Args:
            n: Size of identity matrix
            
        Returns:
            n×n identity matrix
        """
        result = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            result[i][i] = 1.0
        return result
    
    @staticmethod
    def zeros(n1, n2=None):
        """
        Create zero matrix.
        
        Args:
            n1: Number of rows
            n2: Number of columns (if None, creates n1×n1 matrix)
            
        Returns:
            Zero matrix
        """
        if n2 is None:
            n2 = n1
        return [[0.0 for _ in range(n2)] for _ in range(n1)]
    
    @staticmethod
    def trace(matrix):
        """
        Calculate trace (sum of diagonal elements).
        
        Args:
            matrix: Square matrix
            
        Returns:
            Sum of diagonal elements
        """
        if not matrix:
            return 0.0
        
        n = min(len(matrix), len(matrix[0]) if matrix[0] else 0)
        return sum(matrix[i][i] for i in range(n))
    
    @staticmethod
    def matrix_add(matrix_a, matrix_b):
        """
        Add two matrices: C = A + B
        
        Args:
            matrix_a: First matrix
            matrix_b: Second matrix
            
        Returns:
            Sum matrix
        """
        if not matrix_a or not matrix_b:
            raise ValueError("Matrices cannot be empty")
        
        n1 = len(matrix_a)
        n2 = len(matrix_a[0])
        
        if len(matrix_b) != n1 or len(matrix_b[0]) != n2:
            raise ValueError("Matrices must have same dimensions")
        
        result = [[0.0 for _ in range(n2)] for _ in range(n1)]
        for i in range(n1):
            for j in range(n2):
                result[i][j] = matrix_a[i][j] + matrix_b[i][j]
        
        return result
    
    @staticmethod
    def scalar_multiply(scalar, matrix):
        """
        Multiply matrix by scalar: B = c × A
        
        Args:
            scalar: Scalar multiplier
            matrix: Input matrix
            
        Returns:
            Scaled matrix
        """
        if not matrix:
            raise ValueError("Matrix cannot be empty")
        
        n1 = len(matrix)
        n2 = len(matrix[0]) if matrix[0] else 0
        
        result = [[0.0 for _ in range(n2)] for _ in range(n1)]
        for i in range(n1):
            for j in range(n2):
                result[i][j] = scalar * matrix[i][j]
        
        return result
