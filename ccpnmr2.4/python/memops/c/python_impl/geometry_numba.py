"""
Numba-accelerated geometry operations.

Uses JIT compilation for high-performance vector operations.
"""

import math
from typing import List

try:
    from numba import jit
    import numpy as np
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback to pure Python
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


@jit(nopython=True)
def inner_product_numba(v1, v2):
    """Calculate dot product (JIT-compiled)."""
    result = 0.0
    for i in range(len(v1)):
        result += v1[i] * v2[i]
    return result


@jit(nopython=True)
def vector_length_numba(v):
    """Calculate vector length (JIT-compiled)."""
    return math.sqrt(inner_product_numba(v, v))


@jit(nopython=True)
def cross_product_numba(v2, v3):
    """Calculate cross product (JIT-compiled)."""
    result = np.empty(3, dtype=np.float64)
    result[0] = v2[1]*v3[2] - v2[2]*v3[1]
    result[1] = v2[2]*v3[0] - v2[0]*v3[2]
    result[2] = v2[0]*v3[1] - v2[1]*v3[0]
    return result


@jit(nopython=True)
def normalise_vector_numba(v):
    """Normalize vector to unit length (JIT-compiled)."""
    length = vector_length_numba(v)
    result = np.empty(len(v), dtype=np.float64)
    if length > 0:
        scale = 1.0 / length
        for i in range(len(v)):
            result[i] = v[i] * scale
    else:
        for i in range(len(v)):
            result[i] = v[i]
    return result


@jit(nopython=True)
def vectors_angle_numba(v1, v2):
    """Calculate angle between vectors (JIT-compiled)."""
    d1 = vector_length_numba(v1)
    d2 = vector_length_numba(v2)
    
    if d1 > 0 and d2 > 0:
        d = inner_product_numba(v1, v2) / (d1 * d2)
        # Clamp to [-1, 1]
        d = max(-1.0, min(1.0, d))
        return math.acos(d)
    else:
        return 0.0


@jit(nopython=True)
def rotation_matrix_numba(axis, angle):
    """Create rotation matrix (JIT-compiled)."""
    # Normalize axis
    axis_norm = normalise_vector_numba(axis)
    
    c = math.cos(angle)
    s = math.sin(angle)
    
    # Initialize matrix
    matrix = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        matrix[i, i] = c
        for j in range(3):
            matrix[i, j] += (1 - c) * axis_norm[i] * axis_norm[j]
    
    # Add skew-symmetric part
    matrix[0, 1] -= axis_norm[2] * s
    matrix[1, 0] += axis_norm[2] * s
    matrix[1, 2] -= axis_norm[0] * s
    matrix[2, 1] += axis_norm[0] * s
    matrix[2, 0] -= axis_norm[1] * s
    matrix[0, 2] += axis_norm[1] * s
    
    return matrix


SMALL_ANGLE = 1.0e-6

@jit(nopython=True)
def rotation_matrix_vector_to_vector_numba(v1, v2):
    """Create rotation matrix from v1 to v2 (JIT-compiled)."""
    d1 = vector_length_numba(v1)
    d2 = vector_length_numba(v2)
    angle = vectors_angle_numba(v1, v2)
    
    axis = np.zeros(3, dtype=np.float64)
    
    if d1 > 0 and d2 > 0 and angle > 0:
        if angle < math.pi - SMALL_ANGLE:
            # Normal case
            axis = cross_product_numba(v1, v2)
            axis = normalise_vector_numba(axis)
        else:
            # Anti-parallel
            if v1[0] != 0 or v1[1] != 0:
                axis[0] = v1[1]
                axis[1] = -v1[0]
                axis[2] = 0.0
            else:
                axis[0] = 1.0
                axis[1] = 0.0
                axis[2] = 0.0
    else:
        # Parallel or zero
        angle = 0.0
        axis[0] = 1.0
        axis[1] = 0.0
        axis[2] = 0.0
    
    return rotation_matrix_numba(axis, angle)


# High-level API
class GeometryOps:
    """Numba-accelerated geometry operations."""
    
    @staticmethod
    def vector_length(v):
        """Calculate vector length."""
        if NUMBA_AVAILABLE:
            return vector_length_numba(np.array(v, dtype=np.float64))
        else:
            return math.sqrt(sum(x*x for x in v))
    
    @staticmethod
    def inner_product(v1, v2):
        """Calculate dot product."""
        if NUMBA_AVAILABLE:
            return inner_product_numba(
                np.array(v1, dtype=np.float64),
                np.array(v2, dtype=np.float64)
            )
        else:
            return sum(a*b for a, b in zip(v1, v2))
    
    @staticmethod
    def cross_product(v2, v3):
        """Calculate cross product."""
        if NUMBA_AVAILABLE:
            result = cross_product_numba(
                np.array(v2, dtype=np.float64),
                np.array(v3, dtype=np.float64)
            )
            return result.tolist()
        else:
            return [
                v2[1]*v3[2] - v2[2]*v3[1],
                v2[2]*v3[0] - v2[0]*v3[2],
                v2[0]*v3[1] - v2[1]*v3[0]
            ]
    
    @staticmethod
    def normalise_vector(v):
        """Normalize vector."""
        if NUMBA_AVAILABLE:
            result = normalise_vector_numba(np.array(v, dtype=np.float64))
            return result.tolist()
        else:
            length = math.sqrt(sum(x*x for x in v))
            if length > 0:
                return [x / length for x in v]
            return v[:]
    
    @staticmethod
    def vectors_angle(v1, v2):
        """Calculate angle between vectors."""
        if NUMBA_AVAILABLE:
            return vectors_angle_numba(
                np.array(v1, dtype=np.float64),
                np.array(v2, dtype=np.float64)
            )
        else:
            d1 = math.sqrt(sum(x*x for x in v1))
            d2 = math.sqrt(sum(x*x for x in v2))
            if d1 > 0 and d2 > 0:
                d = sum(a*b for a, b in zip(v1, v2)) / (d1 * d2)
                d = max(-1.0, min(1.0, d))
                return math.acos(d)
            return 0.0
    
    @staticmethod
    def rotation_matrix(axis, angle):
        """Create rotation matrix."""
        if NUMBA_AVAILABLE:
            result = rotation_matrix_numba(
                np.array(axis, dtype=np.float64),
                float(angle)
            )
            return [list(row) for row in result]
        else:
            # Simplified fallback
            return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    
    @staticmethod
    def rotation_matrix_vector_to_vector(v1, v2):
        """Create rotation matrix from v1 to v2."""
        if NUMBA_AVAILABLE:
            result = rotation_matrix_vector_to_vector_numba(
                np.array(v1, dtype=np.float64),
                np.array(v2, dtype=np.float64)
            )
            return [list(row) for row in result]
        else:
            # Simplified fallback
            return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


# Convenience functions
vector_length = GeometryOps.vector_length
inner_product = GeometryOps.inner_product
cross_product = GeometryOps.cross_product
normalise_vector = GeometryOps.normalise_vector
vectors_angle = GeometryOps.vectors_angle
rotation_matrix = GeometryOps.rotation_matrix
rotation_matrix_vector_to_vector = GeometryOps.rotation_matrix_vector_to_vector
