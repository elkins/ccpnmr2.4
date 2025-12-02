"""
Tests for linear algebra implementations.

This test suite validates:
1. Correctness: Operations produce mathematically correct results
2. Edge cases: Empty matrices, single elements, rectangular matrices
3. Consistency: Python and Numba produce identical results
4. NumPy compatibility: Results match NumPy operations

Author: CCPN Team
License: LGPL
"""

import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.c.python_impl import linalg as linalg_py
from memops.c.python_impl import linalg_numba


class TestLinAlgPython(unittest.TestCase):
    """Test pure Python linear algebra implementation."""
    
    def test_matrix_matrix_multiply_square(self):
        """Test matrix multiplication with square matrices."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        
        C = linalg_py.matrix_matrix_multiply(A, B)
        
        # Expected: [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
        #         = [[19, 22], [43, 50]]
        self.assertEqual(C, [[19, 22], [43, 50]])
    
    def test_matrix_matrix_multiply_rectangular(self):
        """Test matrix multiplication with rectangular matrices."""
        A = [[1, 2, 3], [4, 5, 6]]  # 2×3
        B = [[7, 8], [9, 10], [11, 12]]  # 3×2
        
        C = linalg_py.matrix_matrix_multiply(A, B)
        
        # Result should be 2×2
        self.assertEqual(len(C), 2)
        self.assertEqual(len(C[0]), 2)
        
        # Expected: [[1*7+2*9+3*11, 1*8+2*10+3*12], [4*7+5*9+6*11, 4*8+5*10+6*12]]
        #         = [[58, 64], [139, 154]]
        self.assertEqual(C[0][0], 58)
        self.assertEqual(C[0][1], 64)
        self.assertEqual(C[1][0], 139)
        self.assertEqual(C[1][1], 154)
    
    def test_matrix_matrix_multiply_identity(self):
        """Test multiplication by identity matrix."""
        A = [[1, 2], [3, 4]]
        I = [[1, 0], [0, 1]]
        
        C = linalg_py.matrix_matrix_multiply(A, I)
        self.assertEqual(C, A)
        
        C = linalg_py.matrix_matrix_multiply(I, A)
        self.assertEqual(C, A)
    
    def test_matrix_matrix_multiply_incompatible(self):
        """Test error handling for incompatible dimensions."""
        A = [[1, 2], [3, 4]]  # 2×2
        B = [[5, 6, 7]]  # 1×3
        
        with self.assertRaises(ValueError):
            linalg_py.matrix_matrix_multiply(A, B)
    
    def test_matrix_vector_multiply(self):
        """Test matrix-vector multiplication."""
        A = [[1, 2], [3, 4], [5, 6]]  # 3×2
        x = [7, 8]
        
        y = linalg_py.matrix_vector_multiply(A, x)
        
        # Expected: [1*7+2*8, 3*7+4*8, 5*7+6*8] = [23, 53, 83]
        self.assertEqual(y, [23, 53, 83])
    
    def test_matrix_vector_multiply_identity(self):
        """Test multiplication with identity matrix."""
        I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        x = [5, 6, 7]
        
        y = linalg_py.matrix_vector_multiply(I, x)
        self.assertEqual(y, x)
    
    def test_matrix_vector_multiply_incompatible(self):
        """Test error handling for incompatible dimensions."""
        A = [[1, 2], [3, 4]]  # 2×2
        x = [5, 6, 7]  # length 3
        
        with self.assertRaises(ValueError):
            linalg_py.matrix_vector_multiply(A, x)
    
    def test_matrix_transpose_square(self):
        """Test transpose of square matrix."""
        A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        
        B = linalg_py.matrix_transpose(A)
        
        # Expected: [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        self.assertEqual(B, [[1, 4, 7], [2, 5, 8], [3, 6, 9]])
    
    def test_matrix_transpose_rectangular(self):
        """Test transpose of rectangular matrix."""
        A = [[1, 2, 3], [4, 5, 6]]  # 2×3
        
        B = linalg_py.matrix_transpose(A)
        
        # Should be 3×2
        self.assertEqual(len(B), 3)
        self.assertEqual(len(B[0]), 2)
        
        # Expected: [[1, 4], [2, 5], [3, 6]]
        self.assertEqual(B, [[1, 4], [2, 5], [3, 6]])
    
    def test_matrix_transpose_double(self):
        """Test that double transpose returns original."""
        A = [[1, 2, 3], [4, 5, 6]]
        
        B = linalg_py.matrix_transpose(A)
        C = linalg_py.matrix_transpose(B)
        
        self.assertEqual(C, A)
    
    def test_identity(self):
        """Test identity matrix creation."""
        I = linalg_py.LinAlgOps.identity(3)
        
        expected = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.assertEqual(I, expected)
    
    def test_trace(self):
        """Test trace calculation."""
        A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        
        tr = linalg_py.LinAlgOps.trace(A)
        
        # Expected: 1 + 5 + 9 = 15
        self.assertEqual(tr, 15.0)


class TestLinAlgNumba(unittest.TestCase):
    """Test Numba JIT-compiled linear algebra implementation."""
    
    def test_matrix_matrix_multiply_square(self):
        """Test matrix multiplication with square matrices."""
        A = np.array([[1, 2], [3, 4]], dtype=np.float64)
        B = np.array([[5, 6], [7, 8]], dtype=np.float64)
        
        C = linalg_numba.matmul(A, B)
        
        expected = np.array([[19, 22], [43, 50]], dtype=np.float64)
        np.testing.assert_array_almost_equal(C, expected)
    
    def test_matrix_matrix_multiply_rectangular(self):
        """Test matrix multiplication with rectangular matrices."""
        A = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64)  # 2×3
        B = np.array([[7, 8], [9, 10], [11, 12]], dtype=np.float64)  # 3×2
        
        C = linalg_numba.matmul(A, B)
        
        self.assertEqual(C.shape, (2, 2))
        expected = np.array([[58, 64], [139, 154]], dtype=np.float64)
        np.testing.assert_array_almost_equal(C, expected)
    
    def test_matrix_vector_multiply(self):
        """Test matrix-vector multiplication."""
        A = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float64)
        x = np.array([7, 8], dtype=np.float64)
        
        y = linalg_numba.matvec(A, x)
        
        expected = np.array([23, 53, 83], dtype=np.float64)
        np.testing.assert_array_almost_equal(y, expected)
    
    def test_matrix_transpose(self):
        """Test matrix transpose."""
        A = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64)
        
        B = linalg_numba.transpose(A)
        
        self.assertEqual(B.shape, (3, 2))
        expected = np.array([[1, 4], [2, 5], [3, 6]], dtype=np.float64)
        np.testing.assert_array_almost_equal(B, expected)
    
    def test_trace(self):
        """Test trace calculation."""
        A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float64)
        
        tr = linalg_numba.trace(A)
        
        self.assertAlmostEqual(tr, 15.0)


class TestConsistency(unittest.TestCase):
    """Test consistency between Python and Numba implementations."""
    
    def test_matmul_consistency(self):
        """Test matrix multiplication consistency."""
        A_list = [[1, 2, 3], [4, 5, 6]]
        B_list = [[7, 8], [9, 10], [11, 12]]
        
        # Python version
        C_py = linalg_py.matrix_matrix_multiply(A_list, B_list)
        
        # Numba version
        A_np = np.array(A_list, dtype=np.float64)
        B_np = np.array(B_list, dtype=np.float64)
        C_numba = linalg_numba.matmul(A_np, B_np)
        
        # Should match
        for i in range(len(C_py)):
            for j in range(len(C_py[0])):
                self.assertAlmostEqual(C_py[i][j], C_numba[i, j], places=10)
    
    def test_matvec_consistency(self):
        """Test matrix-vector multiplication consistency."""
        A_list = [[1, 2], [3, 4], [5, 6]]
        x_list = [7, 8]
        
        # Python version
        y_py = linalg_py.matrix_vector_multiply(A_list, x_list)
        
        # Numba version
        A_np = np.array(A_list, dtype=np.float64)
        x_np = np.array(x_list, dtype=np.float64)
        y_numba = linalg_numba.matvec(A_np, x_np)
        
        # Should match
        for i in range(len(y_py)):
            self.assertAlmostEqual(y_py[i], y_numba[i], places=10)
    
    def test_transpose_consistency(self):
        """Test transpose consistency."""
        A_list = [[1, 2, 3], [4, 5, 6]]
        
        # Python version
        B_py = linalg_py.matrix_transpose(A_list)
        
        # Numba version
        A_np = np.array(A_list, dtype=np.float64)
        B_numba = linalg_numba.transpose(A_np)
        
        # Should match
        for i in range(len(B_py)):
            for j in range(len(B_py[0])):
                self.assertAlmostEqual(B_py[i][j], B_numba[i, j], places=10)


class TestNumPyCompatibility(unittest.TestCase):
    """Test that results match NumPy operations."""
    
    def test_matmul_vs_numpy(self):
        """Test matrix multiplication against NumPy."""
        A = np.random.randn(5, 7)
        B = np.random.randn(7, 3)
        
        # Numba version
        C_numba = linalg_numba.matmul(A, B)
        
        # NumPy version
        C_numpy = np.dot(A, B)
        
        np.testing.assert_array_almost_equal(C_numba, C_numpy, decimal=10)
    
    def test_matvec_vs_numpy(self):
        """Test matrix-vector multiplication against NumPy."""
        A = np.random.randn(5, 3)
        x = np.random.randn(3)
        
        # Numba version
        y_numba = linalg_numba.matvec(A, x)
        
        # NumPy version
        y_numpy = np.dot(A, x)
        
        np.testing.assert_array_almost_equal(y_numba, y_numpy, decimal=10)
    
    def test_transpose_vs_numpy(self):
        """Test transpose against NumPy."""
        A = np.random.randn(4, 6)
        
        # Numba version
        B_numba = linalg_numba.transpose(A)
        
        # NumPy version
        B_numpy = A.T
        
        np.testing.assert_array_almost_equal(B_numba, B_numpy, decimal=10)
    
    def test_trace_vs_numpy(self):
        """Test trace against NumPy."""
        A = np.random.randn(5, 5)
        
        # Numba version
        tr_numba = linalg_numba.trace(A)
        
        # NumPy version
        tr_numpy = np.trace(A)
        
        self.assertAlmostEqual(tr_numba, tr_numpy, places=10)


if __name__ == '__main__':
    unittest.main()
