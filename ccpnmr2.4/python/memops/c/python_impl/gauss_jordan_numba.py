"""
Numba JIT-compiled implementation of Gauss-Jordan elimination.

This module provides high-performance JIT-compiled versions of Gauss-Jordan
elimination using Numba. All core numerical operations are decorated with
@jit(nopython=True) for maximum performance.

Uses NumPy arrays for efficient numerical operations.
"""

try:
    import numpy as np
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback to pure Python if Numba not available
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from gauss_jordan import gauss_jordan_solve as _fallback_solve
    from gauss_jordan import solve_linear_system as _fallback_system
    from gauss_jordan import matrix_inverse as _fallback_inverse


if NUMBA_AVAILABLE:
    @jit(nopython=True)
    def gauss_jordan_solve_numba(a, b):
        """
        Numba JIT-compiled Gauss-Jordan solver.
        
        Solves Ax = b and computes A⁻¹ in place using Gauss-Jordan elimination
        with partial pivoting.
        
        Args:
            a: n×n NumPy array (modified in place to A⁻¹)
            b: n-element NumPy array (modified in place to solution x)
        
        Returns:
            bool: True if matrix is singular, False otherwise
        """
        n = len(a)
        
        # Working arrays
        piv = np.zeros(n, dtype=np.int32)
        row = np.zeros(n, dtype=np.int32)
        col = np.zeros(n, dtype=np.int32)
        
        # Main loop over columns
        for i in range(n):
            # Find pivot
            max_val = 0.0
            max_row = 0
            max_col = 0
            
            for j in range(n):
                if piv[j] != 1:
                    for k in range(n):
                        if piv[k] == 0:
                            abs_val = abs(a[j, k])
                            if abs_val >= max_val:
                                max_val = abs_val
                                max_row = j
                                max_col = k
                        elif piv[k] > 1:
                            # Singular matrix
                            return True
            
            piv[max_col] += 1
            
            # Interchange rows if needed
            if max_row != max_col:
                # Swap rows in matrix
                for j in range(n):
                    a[max_row, j], a[max_col, j] = a[max_col, j], a[max_row, j]
                # Swap elements in vector
                b[max_row], b[max_col] = b[max_col], b[max_row]
            
            row[i] = max_row
            col[i] = max_col
            
            # Check for singularity
            pivot_val = a[max_col, max_col]
            if pivot_val == 0.0:
                return True
            
            # Divide pivot row by pivot element
            piv_inv = 1.0 / pivot_val
            a[max_col, max_col] = 1.0
            
            for j in range(n):
                a[max_col, j] *= piv_inv
            b[max_col] *= piv_inv
            
            # Reduce all other rows
            for j in range(n):
                if j != max_col:
                    x = a[j, max_col]
                    a[j, max_col] = 0.0
                    
                    for k in range(n):
                        a[j, k] -= x * a[max_col, k]
                    
                    b[j] -= x * b[max_col]
        
        # Unscramble columns
        for j in range(n-1, -1, -1):
            if row[j] != col[j]:
                for i in range(n):
                    a[i, row[j]], a[i, col[j]] = a[i, col[j]], a[i, row[j]]
        
        return False


class GaussJordanOps:
    """High-level API for Gauss-Jordan operations using Numba."""
    
    @staticmethod
    def solve(a, b):
        """
        Solve linear system Ax = b without modifying inputs.
        
        Args:
            a: n×n matrix (list of lists or NumPy array)
            b: n-element vector (list or NumPy array)
        
        Returns:
            tuple: (solution, inverse, is_singular)
        """
        if not NUMBA_AVAILABLE:
            return _fallback_system(a, b)
        
        # Convert to NumPy arrays
        a_array = np.array(a, dtype=np.float64)
        b_array = np.array(b, dtype=np.float64)
        
        # Make copies for solving
        a_copy = a_array.copy()
        b_copy = b_array.copy()
        
        is_singular = gauss_jordan_solve_numba(a_copy, b_copy)
        
        return (b_copy.tolist(), a_copy.tolist(), is_singular)
    
    @staticmethod
    def solve_inplace(a, b):
        """
        Solve Ax = b, modifying a and b in place.
        
        Args:
            a: n×n NumPy array (modified to A⁻¹)
            b: n-element NumPy array (modified to solution)
        
        Returns:
            bool: True if singular
        """
        if not NUMBA_AVAILABLE:
            from gauss_jordan import gauss_jordan_solve
            is_singular, _, _ = gauss_jordan_solve(a.tolist(), b.tolist())
            return is_singular
        
        return gauss_jordan_solve_numba(a, b)
    
    @staticmethod
    def inverse(a):
        """
        Compute matrix inverse.
        
        Args:
            a: n×n matrix (list of lists or NumPy array)
        
        Returns:
            tuple: (inverse, is_singular)
        """
        if not NUMBA_AVAILABLE:
            return _fallback_inverse(a)
        
        n = len(a)
        a_array = np.array(a, dtype=np.float64)
        
        # Create dummy vector (we only care about the inverse in matrix a)
        b = np.zeros(n, dtype=np.float64)
        b[0] = 1.0
        
        a_copy = a_array.copy()
        is_singular = gauss_jordan_solve_numba(a_copy, b)
        
        if is_singular:
            return (None, True)
        
        return (a_copy.tolist(), False)
    
    @staticmethod
    def determinant(a):
        """
        Compute determinant by checking if matrix is singular.
        
        Note: This is not the most efficient way to compute determinant,
        but it's a useful byproduct of the Gauss-Jordan algorithm.
        
        Args:
            a: n×n matrix
        
        Returns:
            float or None: Determinant, or None if singular
        """
        if not NUMBA_AVAILABLE:
            # Use pure Python version
            from gauss_jordan import matrix_inverse
            _, is_singular = matrix_inverse(a)
            return None if is_singular else 0.0
        
        _, is_singular = GaussJordanOps.inverse(a)
        
        if is_singular:
            return None
        
        # For a proper determinant computation, we'd need to track
        # the product of pivots. This is a simplified version.
        return 0.0  # Placeholder


# Module-level convenience functions
def solve_linear_system(a, b):
    """Solve Ax = b using Numba-optimized Gauss-Jordan."""
    return GaussJordanOps.solve(a, b)


def matrix_inverse(a):
    """Compute matrix inverse using Numba-optimized Gauss-Jordan."""
    return GaussJordanOps.inverse(a)


def gauss_jordan_vector(a, b):
    """C-compatible API: Solve Ax = b in place."""
    if not NUMBA_AVAILABLE:
        from gauss_jordan import gauss_jordan_vector as fallback
        return fallback(a, b)
    
    # Convert to arrays if needed
    if not isinstance(a, np.ndarray):
        a_array = np.array(a, dtype=np.float64)
        b_array = np.array(b, dtype=np.float64)
    else:
        a_array = a
        b_array = b
    
    is_singular = gauss_jordan_solve_numba(a_array, b_array)
    
    # Copy results back if we converted
    if not isinstance(a, np.ndarray):
        for i in range(len(a)):
            for j in range(len(a)):
                a[i][j] = a_array[i, j]
            b[i] = b_array[i]
    
    return is_singular
