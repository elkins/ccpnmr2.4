"""
Pure Python implementation of Gauss-Jordan elimination for solving linear equations.

This module provides functions to solve linear systems Ax = b using Gauss-Jordan
elimination with partial pivoting. The algorithm simultaneously computes the 
solution x and the inverse matrix A⁻¹.

Based on the algorithm from Numerical Recipes.

Original C code: ccpnmr2.4/c/memops/global/gauss_jordan.c
"""


def gauss_jordan_solve(a, b):
    """
    Solve linear equation Ax = b using Gauss-Jordan elimination.
    
    This function solves the linear system and simultaneously computes the
    inverse of matrix A. Both the matrix 'a' and vector 'b' are modified
    in place.
    
    Args:
        a: n×n matrix as list of lists (will be replaced with A⁻¹)
        b: n-element vector as list (will be replaced with solution x)
    
    Returns:
        tuple: (is_singular, a_inverse, x) where:
            - is_singular: True if matrix is singular, False otherwise
            - a_inverse: Inverse of original matrix A (or modified A if singular)
            - x: Solution vector (or modified b if singular)
    
    Example:
        >>> a = [[2.0, 1.0], [1.0, 2.0]]
        >>> b = [3.0, 3.0]
        >>> singular, a_inv, x = gauss_jordan_solve(a, b)
        >>> # x should be [1.0, 1.0]
        >>> # a_inv should be [[2/3, -1/3], [-1/3, 2/3]]
    """
    n = len(a)
    if len(b) != n:
        raise ValueError(f"Matrix dimension {n}x{n} doesn't match vector length {len(b)}")
    
    # Working arrays for pivoting
    piv = [0] * n  # Pivot tracking
    row = [0] * n  # Row interchanges
    col = [0] * n  # Column interchanges
    
    # Main loop over columns to be reduced
    for i in range(n):
        # Find the pivot element
        max_val = 0.0
        max_row = 0
        max_col = 0
        
        for j in range(n):
            if piv[j] != 1:
                for k in range(n):
                    if piv[k] == 0:
                        if abs(a[j][k]) >= max_val:
                            max_val = abs(a[j][k])
                            max_row = j
                            max_col = k
                    elif piv[k] > 1:
                        # Singular matrix - element pivoted twice
                        return (True, a, b)
        
        piv[max_col] += 1
        
        # Interchange rows if needed
        if max_row != max_col:
            a[max_row], a[max_col] = a[max_col], a[max_row]
            b[max_row], b[max_col] = b[max_col], b[max_row]
        
        row[i] = max_row
        col[i] = max_col
        
        # Check for singularity
        if a[max_col][max_col] == 0.0:
            return (True, a, b)
        
        # Divide pivot row by pivot element
        piv_inv = 1.0 / a[max_col][max_col]
        a[max_col][max_col] = 1.0
        
        for j in range(n):
            a[max_col][j] *= piv_inv
        b[max_col] *= piv_inv
        
        # Reduce rows (except pivot row)
        for j in range(n):
            if j != max_col:
                x = a[j][max_col]
                a[j][max_col] = 0.0
                
                for k in range(n):
                    a[j][k] -= x * a[max_col][k]
                
                b[j] -= x * b[max_col]
    
    # Unscramble solution - interchange columns in reverse order
    for j in range(n-1, -1, -1):
        if row[j] != col[j]:
            for i in range(n):
                a[i][row[j]], a[i][col[j]] = a[i][col[j]], a[i][row[j]]
    
    return (False, a, b)


def solve_linear_system(a, b):
    """
    High-level function to solve Ax = b without modifying inputs.
    
    Args:
        a: n×n matrix as list of lists
        b: n-element vector as list
    
    Returns:
        tuple: (solution, inverse, is_singular) where:
            - solution: Solution vector x
            - inverse: Inverse matrix A⁻¹
            - is_singular: True if matrix is singular
    
    Example:
        >>> a = [[2.0, 1.0], [1.0, 2.0]]
        >>> b = [3.0, 3.0]
        >>> x, a_inv, singular = solve_linear_system(a, b)
    """
    # Deep copy to avoid modifying inputs
    a_copy = [row[:] for row in a]
    b_copy = b[:]
    
    is_singular, a_inv, x = gauss_jordan_solve(a_copy, b_copy)
    
    return (x, a_inv, is_singular)


def matrix_inverse(a):
    """
    Compute the inverse of a square matrix.
    
    Args:
        a: n×n matrix as list of lists
    
    Returns:
        tuple: (inverse, is_singular) where:
            - inverse: Inverse matrix A⁻¹ (or None if singular)
            - is_singular: True if matrix is singular
    
    Example:
        >>> a = [[2.0, 1.0], [1.0, 2.0]]
        >>> a_inv, singular = matrix_inverse(a)
    """
    n = len(a)
    
    # Create identity matrix as b
    b = [0.0] * n
    
    # Deep copy matrix
    a_copy = [row[:] for row in a]
    
    # Solve for each column of the identity matrix
    # Since Gauss-Jordan gives us the inverse directly, 
    # we just need a dummy b vector
    b[0] = 1.0  # Doesn't really matter, we want the inverse from 'a'
    
    is_singular, a_inv, _ = gauss_jordan_solve(a_copy, b)
    
    if is_singular:
        return (None, True)
    
    return (a_inv, False)


# C-style API for compatibility
def gauss_jordan_vector(a, b):
    """
    C-compatible API: Solve Ax = b and compute A⁻¹ in place.
    
    Args:
        a: Matrix (modified in place to inverse)
        b: Vector (modified in place to solution)
    
    Returns:
        bool: True if singular, False otherwise
    """
    n = len(a)
    piv = [0] * n
    row = [0] * n
    col = [0] * n
    
    is_singular, _, _ = gauss_jordan_solve(a, b)
    return is_singular
