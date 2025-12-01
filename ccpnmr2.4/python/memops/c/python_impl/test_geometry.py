"""
Test suite for geometry implementations (Python and Numba).

Tests vector operations for correctness and consistency.
"""

import unittest
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Import implementations
from geometry import (
    vector_length, inner_product, cross_product, normalise_vector,
    vectors_angle, rotation_matrix, rotation_matrix_vector_to_vector
)
from geometry import vector_length as vector_length_python
from geometry import inner_product as inner_product_python

try:
    from geometry_numba import (
        vector_length as vector_length_numba,
        inner_product as inner_product_numba,
        cross_product as cross_product_numba,
        normalise_vector as normalise_vector_numba,
        vectors_angle as vectors_angle_numba
    )
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False


class TestGeometryPython(unittest.TestCase):
    """Test pure Python geometry operations."""
    
    def test_vector_length(self):
        """Test vector length calculation."""
        self.assertAlmostEqual(vector_length([3, 4]), 5.0)
        self.assertAlmostEqual(vector_length([1, 0, 0]), 1.0)
        self.assertAlmostEqual(vector_length([1, 1, 1]), math.sqrt(3))
        self.assertAlmostEqual(vector_length([0, 0, 0]), 0.0)
    
    def test_inner_product(self):
        """Test dot product."""
        self.assertAlmostEqual(inner_product([1, 2, 3], [4, 5, 6]), 32.0)
        self.assertAlmostEqual(inner_product([1, 0], [0, 1]), 0.0)
        self.assertAlmostEqual(inner_product([2, 3], [2, 3]), 13.0)
    
    def test_cross_product(self):
        """Test cross product."""
        result = cross_product([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.0)
        self.assertAlmostEqual(result[2], 1.0)
        
        # i × j = k
        result = cross_product([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(vector_length(result), 1.0)
    
    def test_normalise_vector(self):
        """Test vector normalization."""
        result = normalise_vector([3, 4])
        self.assertAlmostEqual(vector_length(result), 1.0)
        self.assertAlmostEqual(result[0], 0.6)
        self.assertAlmostEqual(result[1], 0.8)
        
        result = normalise_vector([1, 1, 1])
        self.assertAlmostEqual(vector_length(result), 1.0)
    
    def test_vectors_angle(self):
        """Test angle calculation."""
        # Perpendicular vectors
        angle = vectors_angle([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(angle, math.pi / 2)
        
        # Parallel vectors
        angle = vectors_angle([1, 0, 0], [2, 0, 0])
        self.assertAlmostEqual(angle, 0.0)
        
        # 45 degrees
        angle = vectors_angle([1, 0], [1, 1])
        self.assertAlmostEqual(angle, math.pi / 4, places=5)
    
    def test_rotation_matrix(self):
        """Test rotation matrix creation."""
        # Rotation about z-axis by 90 degrees
        matrix = rotation_matrix([0, 0, 1], math.pi / 2)
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), 3)
        
        # Check it's approximately orthogonal
        # M * M^T should be identity
        result = [[sum(matrix[i][k] * matrix[j][k] for k in range(3))
                   for j in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(result[i][j], expected, places=5)


@unittest.skipIf(not HAS_NUMBA, "Numba not available")
class TestGeometryNumba(unittest.TestCase):
    """Test Numba geometry operations."""
    
    def test_vector_length(self):
        """Test vector length with Numba."""
        self.assertAlmostEqual(vector_length_numba([3, 4]), 5.0)
        self.assertAlmostEqual(vector_length_numba([1, 0, 0]), 1.0)
    
    def test_inner_product(self):
        """Test dot product with Numba."""
        self.assertAlmostEqual(inner_product_numba([1, 2, 3], [4, 5, 6]), 32.0)
        self.assertAlmostEqual(inner_product_numba([1, 0], [0, 1]), 0.0)
    
    def test_cross_product(self):
        """Test cross product with Numba."""
        result = cross_product_numba([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(result[2], 1.0)
    
    def test_normalise_vector(self):
        """Test normalization with Numba."""
        result = normalise_vector_numba([3, 4])
        length = math.sqrt(result[0]**2 + result[1]**2)
        self.assertAlmostEqual(length, 1.0)
    
    def test_vectors_angle(self):
        """Test angle with Numba."""
        angle = vectors_angle_numba([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(angle, math.pi / 2)


@unittest.skipIf(not HAS_NUMBA, "Numba not available")
class TestConsistency(unittest.TestCase):
    """Test consistency between Python and Numba implementations."""
    
    def test_vector_length_consistency(self):
        """Ensure Python and Numba give same results."""
        test_vectors = [
            [1, 2, 3],
            [3, 4],
            [1, 0, 0, 0, 1],
            [0.1, 0.2, 0.3]
        ]
        for v in test_vectors:
            python_result = vector_length_python(v)
            numba_result = vector_length_numba(v)
            self.assertAlmostEqual(python_result, numba_result, places=6)
    
    def test_inner_product_consistency(self):
        """Ensure Python and Numba give same results."""
        test_pairs = [
            ([1, 2, 3], [4, 5, 6]),
            ([1, 0], [0, 1]),
            ([0.5, 0.5], [0.5, 0.5])
        ]
        for v1, v2 in test_pairs:
            python_result = inner_product_python(v1, v2)
            numba_result = inner_product_numba(v1, v2)
            self.assertAlmostEqual(python_result, numba_result, places=6)
    
    def test_cross_product_consistency(self):
        """Ensure Python and Numba give same cross product."""
        test_pairs = [
            ([1, 0, 0], [0, 1, 0]),
            ([1, 2, 3], [4, 5, 6]),
            ([0.5, 0.5, 0.5], [1, 0, 0])
        ]
        from geometry import cross_product as cross_product_python
        for v1, v2 in test_pairs:
            python_result = cross_product_python(v1, v2)
            numba_result = cross_product_numba(v1, v2)
            for i in range(3):
                self.assertAlmostEqual(python_result[i], numba_result[i], places=6)


if __name__ == '__main__':
    unittest.main()
