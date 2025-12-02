"""
Tests for eigenvalue.py - Eigenvalue computation using NumPy LAPACK
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from eigenvalue import (
    compute_eigenvalues, compute_eigenvectors, compute_eigenvalues_tridiag,
    sort_eigenvalues, dominant_eigenvector, matrix_condition_number, EigenvalueError
)


class TestComputeEigenvalues:
    """Test eigenvalue computation."""
    
    def test_2x2_symmetric(self):
        """Test 2x2 symmetric matrix."""
        matrix = np.array([[3.0, 1.0],
                          [1.0, 2.0]], dtype=float)
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        assert eigenvalues.shape == (2,)
        # Check eigenvalues are sorted
        assert eigenvalues[0] <= eigenvalues[1]
    
    def test_3x3_symmetric(self):
        """Test 3x3 symmetric matrix."""
        matrix = np.array([[6.0, 2.0, 1.0],
                          [2.0, 5.0, 2.0],
                          [1.0, 2.0, 4.0]], dtype=float)
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        assert eigenvalues.shape == (3,)
        assert len(eigenvalues) == 3
    
    def test_diagonal_matrix(self):
        """Test diagonal matrix eigenvalues."""
        matrix = np.diag([5.0, 3.0, 1.0, 7.0])
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        expected = np.sort([1.0, 3.0, 5.0, 7.0])
        np.testing.assert_allclose(np.sort(eigenvalues), expected, rtol=1e-10)
    
    def test_identity_matrix(self):
        """Test identity matrix has all eigenvalues = 1."""
        matrix = np.eye(5, dtype=float)
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        expected = np.ones(5)
        np.testing.assert_allclose(eigenvalues, expected, rtol=1e-10)
    
    def test_non_symmetric(self):
        """Test non-symmetric matrix."""
        matrix = np.array([[3.0, 1.0],
                          [2.0, 2.0]], dtype=float)
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=False)
        
        assert eigenvalues.shape == (2,)
    
    def test_non_square_error(self):
        """Test non-square matrix raises error."""
        matrix = np.array([[1.0, 2.0, 3.0],
                          [4.0, 5.0, 6.0]])
        
        with pytest.raises(ValueError, match="Matrix must be square"):
            compute_eigenvalues(matrix)


class TestComputeEigenvectors:
    """Test eigenvalue and eigenvector computation."""
    
    def test_2x2_with_eigenvectors(self):
        """Test 2x2 matrix with eigenvectors."""
        matrix = np.array([[4.0, 2.0],
                          [2.0, 3.0]], dtype=float)
        
        eigenvalues, eigenvectors = compute_eigenvectors(matrix, symmetric=True)
        
        assert eigenvalues.shape == (2,)
        assert eigenvectors.shape == (2, 2)
        
        # Verify eigenvalue equation: A*v = λ*v
        for i in range(2):
            v = eigenvectors[:, i]
            lhs = matrix @ v
            rhs = eigenvalues[i] * v
            np.testing.assert_allclose(lhs, rhs, rtol=1e-10, atol=1e-10)
    
    def test_3x3_orthonormal(self):
        """Test eigenvectors are orthonormal for symmetric matrix."""
        matrix = np.array([[6.0, 2.0, 1.0],
                          [2.0, 5.0, 2.0],
                          [1.0, 2.0, 4.0]], dtype=float)
        
        eigenvalues, eigenvectors = compute_eigenvectors(matrix, symmetric=True)
        
        # Eigenvectors should be orthonormal
        identity = eigenvectors.T @ eigenvectors
        np.testing.assert_allclose(identity, np.eye(3), rtol=1e-10, atol=1e-10)
    
    def test_non_symmetric_eigenvectors(self):
        """Test non-symmetric matrix eigenvectors."""
        matrix = np.array([[3.0, 1.0],
                          [2.0, 2.0]], dtype=float)
        
        eigenvalues, eigenvectors = compute_eigenvectors(matrix, symmetric=False)
        
        assert eigenvalues.shape == (2,)
        assert eigenvectors.shape == (2, 2)


class TestComputeEigenvaluesTridiag:
    """Test tridiagonal matrix eigenvalue computation."""
    
    def test_simple_tridiagonal(self):
        """Test simple tridiagonal matrix."""
        diagonal = np.array([2.0, 2.0, 2.0])
        off_diagonal = np.array([1.0, 1.0])
        
        eigenvalues = compute_eigenvalues_tridiag(diagonal, off_diagonal)
        
        assert eigenvalues.shape == (3,)
    
    def test_tridiagonal_4x4(self):
        """Test 4x4 tridiagonal."""
        diagonal = np.array([2.0, 2.0, 2.0, 2.0])
        off_diagonal = np.array([1.0, 1.0, 1.0])
        
        eigenvalues = compute_eigenvalues_tridiag(diagonal, off_diagonal)
        
        assert eigenvalues.shape == (4,)
        assert np.all(np.isreal(eigenvalues))
    
    def test_tridiagonal_size_mismatch(self):
        """Test size mismatch raises error."""
        diagonal = np.array([2.0, 2.0, 2.0])
        off_diagonal = np.array([1.0, 1.0, 1.0])  # Wrong size
        
        with pytest.raises(ValueError, match="off_diagonal must have n-1 elements"):
            compute_eigenvalues_tridiag(diagonal, off_diagonal)


class TestSortEigenvalues:
    """Test eigenvalue sorting."""
    
    def test_sort_ascending(self):
        """Test sorting eigenvalues in ascending order."""
        eigenvalues = np.array([5.0, 2.0, 8.0, 1.0])
        
        sorted_vals, _ = sort_eigenvalues(eigenvalues, ascending=True)
        
        expected = np.array([1.0, 2.0, 5.0, 8.0])
        np.testing.assert_allclose(sorted_vals, expected)
    
    def test_sort_descending(self):
        """Test sorting in descending order."""
        eigenvalues = np.array([5.0, 2.0, 8.0, 1.0])
        
        sorted_vals, _ = sort_eigenvalues(eigenvalues, ascending=False)
        
        expected = np.array([8.0, 5.0, 2.0, 1.0])
        np.testing.assert_allclose(sorted_vals, expected)
    
    def test_sort_with_eigenvectors(self):
        """Test sorting eigenvalues and eigenvectors together."""
        eigenvalues = np.array([3.0, 1.0, 2.0])
        eigenvectors = np.array([[1, 2, 3],
                                [4, 5, 6],
                                [7, 8, 9]])
        
        sorted_vals, sorted_vecs = sort_eigenvalues(eigenvalues, eigenvectors, ascending=True)
        
        expected_vals = np.array([1.0, 2.0, 3.0])
        expected_vecs = np.array([[2, 3, 1],
                                 [5, 6, 4],
                                 [8, 9, 7]])
        
        np.testing.assert_allclose(sorted_vals, expected_vals)
        np.testing.assert_allclose(sorted_vecs, expected_vecs)
    
    def test_sort_no_eigenvectors(self):
        """Test sorting without eigenvectors."""
        eigenvalues = np.array([5.0, 2.0, 8.0])
        
        sorted_vals, sorted_vecs = sort_eigenvalues(eigenvalues, None, ascending=True)
        
        expected = np.array([2.0, 5.0, 8.0])
        np.testing.assert_allclose(sorted_vals, expected)
        assert sorted_vecs is None


class TestDominantEigenvector:
    """Test dominant eigenvalue/eigenvector computation."""
    
    def test_dominant_positive(self):
        """Test dominant eigenvalue (largest absolute value)."""
        matrix = np.diag([5.0, 2.0, 1.0])
        
        dom_val, dom_vec = dominant_eigenvector(matrix, symmetric=True)
        
        assert dom_val == 5.0
        assert dom_vec.shape == (3,)
        # Dominant eigenvector should be [1, 0, 0] (or close to it)
        expected = np.array([1.0, 0.0, 0.0])
        np.testing.assert_allclose(np.abs(dom_vec), np.abs(expected), rtol=1e-10)
    
    def test_dominant_negative(self):
        """Test dominant eigenvalue when largest is negative."""
        matrix = np.diag([-10.0, 3.0, 1.0])
        
        dom_val, dom_vec = dominant_eigenvector(matrix, symmetric=True)
        
        # Should pick -10 since it has largest absolute value
        assert abs(dom_val) == 10.0
        assert dom_vec.shape == (3,)
    
    def test_dominant_2x2(self):
        """Test 2x2 matrix dominant eigenvector."""
        matrix = np.array([[4.0, 2.0],
                          [2.0, 3.0]], dtype=float)
        
        dom_val, dom_vec = dominant_eigenvector(matrix, symmetric=True)
        
        # Verify it's an eigenvector
        lhs = matrix @ dom_vec
        rhs = dom_val * dom_vec
        np.testing.assert_allclose(lhs, rhs, rtol=1e-10)


class TestMatrixConditionNumber:
    """Test condition number computation."""
    
    def test_well_conditioned(self):
        """Test well-conditioned matrix (condition number close to 1)."""
        matrix = np.eye(3, dtype=float)
        
        cond = matrix_condition_number(matrix)
        
        # Identity matrix has condition number 1
        assert abs(cond - 1.0) < 1e-10
    
    def test_ill_conditioned(self):
        """Test ill-conditioned matrix (large condition number)."""
        matrix = np.diag([100.0, 1.0, 0.01])
        
        cond = matrix_condition_number(matrix)
        
        # Condition number should be 100 / 0.01 = 10000
        assert abs(cond - 10000.0) < 1.0
    
    def test_nearly_singular(self):
        """Test nearly singular matrix (very large condition number)."""
        matrix = np.diag([100.0, 1.0, 1e-10])
        
        cond = matrix_condition_number(matrix)
        
        # Condition number should be very large
        assert cond > 1e10
    
    def test_singular_error(self):
        """Test singular matrix raises error."""
        matrix = np.array([[1.0, 2.0],
                          [2.0, 4.0]], dtype=float)  # Rank 1
        
        with pytest.raises(ValueError, match="Matrix is singular"):
            matrix_condition_number(matrix)


class TestSpecialMatrices:
    """Test with special matrix types."""
    
    def test_random_symmetric(self):
        """Test random symmetric matrix."""
        np.random.seed(42)
        A = np.random.randn(5, 5)
        matrix = (A + A.T) / 2
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        assert eigenvalues.shape == (5,)
        assert np.all(np.isreal(eigenvalues))
    
    def test_positive_definite(self):
        """Test positive definite matrix (all eigenvalues positive)."""
        # Create positive definite: A = Q^T * D * Q with D positive
        Q = np.array([[0.6, -0.8], [0.8, 0.6]])
        D = np.diag([5.0, 2.0])
        matrix = Q.T @ D @ Q
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        assert np.all(eigenvalues > 0)
    
    def test_repeated_eigenvalues(self):
        """Test matrix with repeated eigenvalues."""
        matrix = np.diag([3.0, 3.0, 3.0, 1.0])
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        # Should have three 3's and one 1
        unique, counts = np.unique(eigenvalues.round(10), return_counts=True)
        assert len(unique) == 2  # Two distinct values
    
    def test_zero_matrix(self):
        """Test zero matrix (all eigenvalues zero)."""
        matrix = np.zeros((4, 4), dtype=float)
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        np.testing.assert_allclose(eigenvalues, np.zeros(4), atol=1e-10)


class TestLargeMatrices:
    """Test with larger matrices."""
    
    def test_50x50_symmetric(self):
        """Test 50x50 symmetric matrix."""
        np.random.seed(123)
        A = np.random.randn(50, 50)
        matrix = (A + A.T) / 2
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        assert eigenvalues.shape == (50,)
    
    def test_100x100_eigenvalues_only(self):
        """Test 100x100 eigenvalues without eigenvectors (faster)."""
        np.random.seed(456)
        A = np.random.randn(100, 100)
        matrix = (A + A.T) / 2
        
        eigenvalues = compute_eigenvalues(matrix, symmetric=True)
        
        assert eigenvalues.shape == (100,)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
