"""
Test suite for Gauss-Jordan elimination implementations.

Tests both pure Python and Numba versions for correctness and consistency.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

import gauss_jordan
import gauss_jordan_numba


class TestGaussJordanPython(unittest.TestCase):
    """Test pure Python Gauss-Jordan implementation."""
    
    def assertMatrixAlmostEqual(self, m1, m2, places=5):
        """Helper to compare matrices element-wise."""
        self.assertEqual(len(m1), len(m2))
        for i in range(len(m1)):
            self.assertEqual(len(m1[i]), len(m2[i]))
            for j in range(len(m1[i])):
                self.assertAlmostEqual(m1[i][j], m2[i][j], places=places)
    
    def assertVectorAlmostEqual(self, v1, v2, places=5):
        """Helper to compare vectors element-wise."""
        self.assertEqual(len(v1), len(v2))
        for i in range(len(v1)):
            self.assertAlmostEqual(v1[i], v2[i], places=places)
    
    def test_simple_2x2_system(self):
        """Test solving a simple 2x2 system."""
        # 2x + y = 3
        # x + 2y = 3
        # Solution: x=1, y=1
        a = [[2.0, 1.0], [1.0, 2.0]]
        b = [3.0, 3.0]
        
        x, a_inv, is_singular = gauss_jordan.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.0, 1.0])
    
    def test_3x3_system(self):
        """Test solving a 3x3 system."""
        # x + 2y + z = 6
        # 2x + y + z = 6
        # x + y + 2z = 6
        # Solution: x=1.5, y=1.5, z=1.5
        a = [[1.0, 2.0, 1.0],
             [2.0, 1.0, 1.0],
             [1.0, 1.0, 2.0]]
        b = [6.0, 6.0, 6.0]
        
        x, a_inv, is_singular = gauss_jordan.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.5, 1.5, 1.5], places=4)
    
    def test_identity_matrix(self):
        """Test with identity matrix."""
        a = [[1.0, 0.0], [0.0, 1.0]]
        b = [5.0, 3.0]
        
        x, a_inv, is_singular = gauss_jordan.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [5.0, 3.0])
        self.assertMatrixAlmostEqual(a_inv, [[1.0, 0.0], [0.0, 1.0]])
    
    def test_matrix_inverse_2x2(self):
        """Test matrix inversion for 2x2."""
        a = [[2.0, 1.0], [1.0, 2.0]]
        
        a_inv, is_singular = gauss_jordan.matrix_inverse(a)
        
        self.assertFalse(is_singular)
        # Inverse should be [[2/3, -1/3], [-1/3, 2/3]]
        expected = [[2.0/3.0, -1.0/3.0], [-1.0/3.0, 2.0/3.0]]
        self.assertMatrixAlmostEqual(a_inv, expected)
    
    def test_matrix_inverse_3x3(self):
        """Test matrix inversion for 3x3."""
        a = [[1.0, 2.0, 3.0],
             [0.0, 1.0, 4.0],
             [5.0, 6.0, 0.0]]
        
        a_inv, is_singular = gauss_jordan.matrix_inverse(a)
        
        self.assertFalse(is_singular)
        self.assertIsNotNone(a_inv)
        
        # Verify A * A^-1 = I
        n = 3
        identity = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    identity[i][j] += a[i][k] * a_inv[k][j]
        
        # Check it's close to identity
        for i in range(n):
            for j in range(n):
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(identity[i][j], expected, places=4)
    
    def test_singular_matrix(self):
        """Test detection of singular matrix."""
        # This matrix is singular (second row = first row)
        a = [[1.0, 2.0], [1.0, 2.0]]
        b = [3.0, 3.0]
        
        x, a_inv, is_singular = gauss_jordan.solve_linear_system(a, b)
        
        self.assertTrue(is_singular)
    
    def test_near_singular_matrix(self):
        """Test with nearly singular matrix (zero pivot)."""
        a = [[0.0, 1.0], [1.0, 1.0]]
        b = [2.0, 3.0]
        
        x, a_inv, is_singular = gauss_jordan.solve_linear_system(a, b)
        
        # Should still solve due to pivoting
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.0, 2.0])
    
    def test_diagonal_matrix(self):
        """Test with diagonal matrix."""
        a = [[2.0, 0.0, 0.0],
             [0.0, 3.0, 0.0],
             [0.0, 0.0, 4.0]]
        b = [2.0, 6.0, 8.0]
        
        x, a_inv, is_singular = gauss_jordan.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.0, 2.0, 2.0])


class TestGaussJordanNumba(unittest.TestCase):
    """Test Numba JIT-compiled Gauss-Jordan implementation."""
    
    def assertVectorAlmostEqual(self, v1, v2, places=5):
        """Helper to compare vectors."""
        self.assertEqual(len(v1), len(v2))
        for i in range(len(v1)):
            self.assertAlmostEqual(v1[i], v2[i], places=places)
    
    def assertMatrixAlmostEqual(self, m1, m2, places=5):
        """Helper to compare matrices."""
        self.assertEqual(len(m1), len(m2))
        for i in range(len(m1)):
            self.assertEqual(len(m1[i]), len(m2[i]))
            for j in range(len(m1[i])):
                self.assertAlmostEqual(m1[i][j], m2[i][j], places=places)
    
    def test_simple_2x2_system(self):
        """Test solving a simple 2x2 system with Numba."""
        a = [[2.0, 1.0], [1.0, 2.0]]
        b = [3.0, 3.0]
        
        x, a_inv, is_singular = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.0, 1.0])
    
    def test_3x3_system(self):
        """Test solving a 3x3 system with Numba."""
        a = [[1.0, 2.0, 1.0],
             [2.0, 1.0, 1.0],
             [1.0, 1.0, 2.0]]
        b = [6.0, 6.0, 6.0]
        
        x, a_inv, is_singular = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.5, 1.5, 1.5], places=4)
    
    def test_matrix_inverse(self):
        """Test matrix inversion with Numba."""
        a = [[2.0, 1.0], [1.0, 2.0]]
        
        a_inv, is_singular = gauss_jordan_numba.matrix_inverse(a)
        
        self.assertFalse(is_singular)
        expected = [[2.0/3.0, -1.0/3.0], [-1.0/3.0, 2.0/3.0]]
        self.assertMatrixAlmostEqual(a_inv, expected)
    
    def test_singular_matrix(self):
        """Test detection of singular matrix with Numba."""
        a = [[1.0, 2.0], [1.0, 2.0]]
        b = [3.0, 3.0]
        
        x, a_inv, is_singular = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertTrue(is_singular)
    
    def test_diagonal_matrix(self):
        """Test with diagonal matrix using Numba."""
        a = [[2.0, 0.0, 0.0],
             [0.0, 3.0, 0.0],
             [0.0, 0.0, 4.0]]
        b = [2.0, 6.0, 8.0]
        
        x, a_inv, is_singular = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertFalse(is_singular)
        self.assertVectorAlmostEqual(x, [1.0, 2.0, 2.0])


class TestConsistency(unittest.TestCase):
    """Test consistency between Python and Numba implementations."""
    
    def assertVectorAlmostEqual(self, v1, v2, places=5):
        """Helper to compare vectors."""
        self.assertEqual(len(v1), len(v2))
        for i in range(len(v1)):
            self.assertAlmostEqual(v1[i], v2[i], places=places)
    
    def assertMatrixAlmostEqual(self, m1, m2, places=5):
        """Helper to compare matrices."""
        self.assertEqual(len(m1), len(m2))
        for i in range(len(m1)):
            self.assertEqual(len(m1[i]), len(m2[i]))
            for j in range(len(m1[i])):
                self.assertAlmostEqual(m1[i][j], m2[i][j], places=places)
    
    def test_consistency_2x2(self):
        """Check Python and Numba give same results for 2x2."""
        a = [[2.0, 1.0], [1.0, 2.0]]
        b = [3.0, 3.0]
        
        x_py, _, singular_py = gauss_jordan.solve_linear_system(a, b)
        x_nb, _, singular_nb = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertEqual(singular_py, singular_nb)
        self.assertVectorAlmostEqual(x_py, x_nb)
    
    def test_consistency_3x3(self):
        """Check Python and Numba give same results for 3x3."""
        a = [[1.0, 2.0, 1.0],
             [2.0, 1.0, 1.0],
             [1.0, 1.0, 2.0]]
        b = [6.0, 6.0, 6.0]
        
        x_py, _, singular_py = gauss_jordan.solve_linear_system(a, b)
        x_nb, _, singular_nb = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertEqual(singular_py, singular_nb)
        self.assertVectorAlmostEqual(x_py, x_nb, places=4)
    
    def test_consistency_inverse(self):
        """Check Python and Numba give same inverse."""
        a = [[2.0, 1.0], [1.0, 2.0]]
        
        inv_py, singular_py = gauss_jordan.matrix_inverse(a)
        inv_nb, singular_nb = gauss_jordan_numba.matrix_inverse(a)
        
        self.assertEqual(singular_py, singular_nb)
        self.assertMatrixAlmostEqual(inv_py, inv_nb)
    
    def test_consistency_singular(self):
        """Check both detect singular matrices consistently."""
        a = [[1.0, 2.0], [1.0, 2.0]]
        b = [3.0, 3.0]
        
        _, _, singular_py = gauss_jordan.solve_linear_system(a, b)
        _, _, singular_nb = gauss_jordan_numba.solve_linear_system(a, b)
        
        self.assertEqual(singular_py, singular_nb)
        self.assertTrue(singular_py)


if __name__ == '__main__':
    unittest.main()
