"""
Pure Python implementation of geometry operations.

Vector operations for NMR analysis:
- vector_length: Calculate vector magnitude
- inner_product: Dot product of two vectors  
- cross_product: Cross product (3D only)
- normalise_vector: Scale vector to unit length
- vectors_angle: Angle between two vectors
- rotation_matrix: Create rotation matrix

Mathematical Background:
    All operations use standard vector algebra:
    - Inner product: v1·v2 = Σ(v1[i] * v2[i])
    - Cross product: v1×v2 = [v1[1]*v2[2]-v1[2]*v2[1], ...]
    - Angle: θ = arccos((v1·v2)/(|v1||v2|))
    - Rotation: Rodrigues' formula R = I + sin(θ)K + (1-cos(θ))K²

Performance:
    - Pure Python for small vectors (< 10 elements)
    - For large arrays, use geometry_numba.py or NumPy directly
    - No NumPy dependency for maximum portability

Example Usage:
    >>> from memops.c.python_impl.geometry import *
    >>> 
    >>> # Calculate vector length
    >>> v = [3.0, 4.0, 0.0]
    >>> length = vector_length(v)  # Returns 5.0
    >>> 
    >>> # Dot product
    >>> v1 = [1.0, 0.0, 0.0]
    >>> v2 = [0.0, 1.0, 0.0]
    >>> dot = inner_product(v1, v2)  # Returns 0.0 (orthogonal)
    >>> 
    >>> # Cross product
    >>> v3 = cross_product(v1, v2)  # Returns [0, 0, 1] (right-hand rule)
    >>> 
    >>> # Normalize vector
    >>> v_unit = normalise_vector([3.0, 4.0, 0.0])  # [0.6, 0.8, 0.0]
    >>> 
    >>> # Angle between vectors
    >>> import math
    >>> angle = vectors_angle(v1, v2)  # π/2 radians (90 degrees)
    >>> degrees = angle * 180 / math.pi  # 90.0
    >>> 
    >>> # Create rotation matrix (rotate 90° about z-axis)
    >>> axis = [0.0, 0.0, 1.0]
    >>> angle = math.pi / 2
    >>> R = rotation_matrix(axis, angle)
    >>> # Apply to vector: result = [sum(R[i][j]*v[j] for j in range(3)) for i in range(3)]

See Also:
    - geometry_numba.py: Numba-accelerated versions for large datasets
    - struct_util.py: Kabsch algorithm using these operations
    - linalg.py: Matrix operations and decompositions

Original C: ccpnmr2.4/c/memops/c/geometry.c (430 lines)
Python implementation: 200 lines
"""

import math
from typing import List, Tuple


def vector_length(v: List[float]) -> float:
    """
    Calculate the length (magnitude) of a vector.
    
    Args:
        v: Input vector
    
    Returns:
        Length of the vector
    """
    return math.sqrt(inner_product(v, v))


def inner_product(v1: List[float], v2: List[float]) -> float:
    """
    Calculate the inner (dot) product of two vectors.
    
    Args:
        v1: First vector
        v2: Second vector
    
    Returns:
        Dot product v1 · v2
    """
    if len(v1) != len(v2):
        raise ValueError(f"Vectors must have same length: {len(v1)} vs {len(v2)}")
    
    return sum(a * b for a, b in zip(v1, v2))


def cross_product(v2: List[float], v3: List[float]) -> List[float]:
    """
    Calculate the cross product of two 3D vectors.
    
    Args:
        v2: First 3D vector
        v3: Second 3D vector
    
    Returns:
        Cross product v2 × v3
    """
    if len(v2) != 3 or len(v3) != 3:
        raise ValueError("Cross product requires 3D vectors")
    
    return [
        v2[1]*v3[2] - v2[2]*v3[1],
        v2[2]*v3[0] - v2[0]*v3[2],
        v2[0]*v3[1] - v2[1]*v3[0]
    ]


def normalise_vector(v: List[float]) -> List[float]:
    """
    Normalize a vector to unit length.
    
    Args:
        v: Input vector
    
    Returns:
        Normalized vector (unit length)
    """
    length = vector_length(v)
    if length > 0:
        scale = 1.0 / length
        return [x * scale for x in v]
    return v[:]


def vectors_angle(v1: List[float], v2: List[float]) -> float:
    """
    Calculate the angle (in radians) between two vectors.
    
    Args:
        v1: First vector
        v2: Second vector
    
    Returns:
        Angle in radians (0 to π)
    """
    d1 = vector_length(v1)
    d2 = vector_length(v2)
    
    if d1 > 0 and d2 > 0:
        d = inner_product(v1, v2) / (d1 * d2)
        # Clamp to [-1, 1] to avoid numerical errors in acos
        d = max(-1.0, min(1.0, d))
        return math.acos(d)
    else:
        return 0.0  # Arbitrary for zero vectors


def rotation_matrix(axis: List[float], angle: float) -> List[List[float]]:
    """
    Create a 3D rotation matrix for rotation about an axis.
    
    Args:
        axis: 3D axis of rotation (will be normalized)
        angle: Rotation angle in radians
    
    Returns:
        3x3 rotation matrix
    """
    if len(axis) != 3:
        raise ValueError("Rotation axis must be 3D")
    
    # Normalize axis
    axis = normalise_vector(axis)
    
    c = math.cos(angle)
    s = math.sin(angle)
    
    # Initialize matrix with diagonal c
    matrix = [[0.0, 0.0, 0.0] for _ in range(3)]
    for i in range(3):
        matrix[i][i] = c
        for j in range(3):
            matrix[i][j] += (1 - c) * axis[i] * axis[j]
    
    # Add skew-symmetric part
    axis_s = [x * s for x in axis]
    matrix[0][1] -= axis_s[2]
    matrix[1][0] += axis_s[2]
    matrix[1][2] -= axis_s[0]
    matrix[2][1] += axis_s[0]
    matrix[2][0] -= axis_s[1]
    matrix[0][2] += axis_s[1]
    
    return matrix


SMALL_ANGLE = 1.0e-6

def rotation_matrix_vector_to_vector(v1: List[float], v2: List[float]) -> List[List[float]]:
    """
    Create a rotation matrix that rotates v1 to align with v2.
    
    Args:
        v1: Starting 3D vector
        v2: Target 3D vector
    
    Returns:
        3x3 rotation matrix
    """
    if len(v1) != 3 or len(v2) != 3:
        raise ValueError("Vectors must be 3D")
    
    d1 = vector_length(v1)
    d2 = vector_length(v2)
    angle = vectors_angle(v1, v2)
    
    if d1 > 0 and d2 > 0 and angle > 0:
        if angle < math.pi - SMALL_ANGLE:
            # Normal case: cross product gives rotation axis
            axis = cross_product(v1, v2)
            axis = normalise_vector(axis)
        else:
            # Anti-parallel vectors: choose perpendicular axis
            if v1[0] != 0 or v1[1] != 0:
                axis = [v1[1], -v1[0], 0.0]
            else:
                axis = [1.0, 0.0, 0.0]
    else:
        # Parallel or zero vectors: identity rotation
        angle = 0.0
        axis = [1.0, 0.0, 0.0]
    
    return rotation_matrix(axis, angle)


# C-style API for compatibility
def new_vector(size: int) -> List[float]:
    """Create a new zero vector."""
    return [0.0] * size


def copy_vector(v: List[float]) -> List[float]:
    """Create a copy of a vector."""
    return v[:]


def scale_vector(v: List[float], scale: float) -> List[float]:
    """Scale a vector by a scalar."""
    return [x * scale for x in v]
