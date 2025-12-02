"""
Tests for diag_dbl.py - Matrix diagonalization using NumPy LAPACK
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from diag_dbl import (
    diagonalise_dbl, diagonalise_dbl_general, eigenvalues_only, DiagonalizationError
)


class TestDiagonaliseDbl:
    """Test symmetric matrix diagonalization."""
    
    def test_simple_2x2_symmetric(self):
        """Test diagonalization of simple 2x2 symmetric matrix."""
        matrix = np.array([[4.0, 2.0],
                          [2.0, 3.0]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        # Check dimensions
        assert eigenvalues.shape == (2,)
        assert eigenvectors.shape == (2, 2)
        
        # Eigenvalues should be sorted
        assert eigenvalues[0] <= eigenvalues[1]
        
        # Verify eigenvalue equation: A*v = λ*v for each eigenvector
        original_matrix = np.array([[4.0, 2.0], [2.0, 3.0]], dtype=float)
        for i in range(2):
            v = eigenvectors[:, i]
            lhs = original_matrix @ v
            rhs = eigenvalues[i] * v
            np.testing.assert_allclose(lhs, rhs, rtol=1e-10, atol=1e-10)
    
    def test_3x3_symmetric(self):
        """Test 3x3 symmetric matrix."""
        matrix = np.array([[6.0, 2.0, 1.0],
                          [2.0, 5.0, 2.0],
                          [1.0, 2.0, 4.0]], dtype=float)
        
        original = matrix.copy()
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        assert eigenvalues.shape == (3,)
        assert eigenvectors.shape == (3, 3)
        
        # Verify orthonormality of eigenvectors (for symmetric matrices)
        identity = eigenvectors.T @ eigenvectors
        np.testing.assert_allclose(identity, np.eye(3), rtol=1e-10, atol=1e-10)
        
        # Verify eigenvalue equations
        for i in range(3):
            v = eigenvectors[:, i]
            lhs = original @ v
            rhs = eigenvalues[i] * v
            np.testing.assert_allclose(lhs, rhs, rtol=1e-10, atol=1e-10)
    
    def test_diagonal_matrix(self):
        """Test that diagonal matrix returns diagonal values as eigenvalues."""
        matrix = np.diag([5.0, 3.0, 1.0])
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        # Eigenvalues should be the diagonal elements (sorted)
        expected = np.array([1.0, 3.0, 5.0])
        np.testing.assert_allclose(np.sort(eigenvalues), expected, rtol=1e-10)
    
    def test_identity_matrix(self):
        """Test identity matrix has all eigenvalues = 1."""
        matrix = np.eye(4, dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        expected = np.ones(4)
        np.testing.assert_allclose(eigenvalues, expected, rtol=1e-10)
    
    def test_matrix_modified_inplace(self):
        """Test that original matrix is modified with eigenvectors."""
        matrix = np.array([[4.0, 2.0],
                          [2.0, 3.0]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        # matrix should now contain eigenvectors
        np.testing.assert_allclose(matrix, eigenvectors, rtol=1e-10)
    
    def test_positive_definite(self):
        """Test positive definite matrix (all eigenvalues positive)."""
        # Create a positive definite matrix: A = Q^T * D * Q
        Q = np.array([[0.6, -0.8], [0.8, 0.6]])
        D = np.diag([5.0, 2.0])
        matrix = Q.T @ D @ Q
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        # All eigenvalues should be positive
        assert np.all(eigenvalues > 0)
    
    def test_large_matrix(self):
        """Test larger matrix (10x10)."""
        # Create random symmetric matrix
        np.random.seed(42)
        A = np.random.randn(10, 10)
        matrix = (A + A.T) / 2  # Make symmetric
        
        original = matrix.copy()
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        assert eigenvalues.shape == (10,)
        assert eigenvectors.shape == (10, 10)
        
        # Verify a few eigenvalue equations
        for i in [0, 4, 9]:
            v = eigenvectors[:, i]
            lhs = original @ v
            rhs = eigenvalues[i] * v
            np.testing.assert_allclose(lhs, rhs, rtol=1e-8, atol=1e-8)
    
    def test_non_square_error(self):
        """Test that non-square matrix raises error."""
        matrix = np.array([[1.0, 2.0, 3.0],
                          [4.0, 5.0, 6.0]])
        
        with pytest.raises(ValueError, match="Matrix must be square"):
            diagonalise_dbl(matrix)


class TestDiagonaliseDbGeneral:
    """Test general (possibly non-symmetric) matrix diagonalization."""
    
    def test_non_symmetric_real(self):
        """Test non-symmetric matrix with real eigenvalues."""
        matrix = np.array([[3.0, 1.0],
                          [2.0, 2.0]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl_general(matrix)
        
        assert eigenvalues.shape == (2,)
        assert eigenvectors.shape == (2, 2)
    
    def test_complex_eigenvalues(self):
        """Test matrix with complex eigenvalues."""
        # Rotation matrix has complex eigenvalues
        matrix = np.array([[0.0, -1.0],
                          [1.0, 0.0]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl_general(matrix)
        
        # Should have complex conjugate pair: ±i
        assert len(eigenvalues) == 2
        # Eigenvalues should be complex
        assert np.iscomplexobj(eigenvalues)


class TestEigenvaluesOnly:
    """Test computing eigenvalues without eigenvectors (faster)."""
    
    def test_eigenvalues_only_2x2(self):
        """Test eigenvalues-only computation."""
        matrix = np.array([[4.0, 2.0],
                          [2.0, 3.0]], dtype=float)
        
        eigenvalues = eigenvalues_only(matrix)
        
        assert eigenvalues.shape == (2,)
        
        # Compare with full diagonalization
        full_eigenvalues, _ = diagonalise_dbl(matrix)
        np.testing.assert_allclose(eigenvalues, full_eigenvalues, rtol=1e-10)
    
    def test_eigenvalues_only_3x3(self):
        """Test 3x3 eigenvalues only."""
        matrix = np.array([[6.0, 2.0, 1.0],
                          [2.0, 5.0, 2.0],
                          [1.0, 2.0, 4.0]], dtype=float)
        
        eigenvalues = eigenvalues_only(matrix)
        
        assert eigenvalues.shape == (3,)
        assert len(eigenvalues) == 3


class TestNumericalStability:
    """Test numerical stability and edge cases."""
    
    def test_nearly_singular(self):
        """Test nearly singular matrix."""
        matrix = np.array([[1.0, 1.0],
                          [1.0, 1.0 + 1e-10]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        # Should still converge
        assert eigenvalues.shape == (2,)
        # One eigenvalue should be very small
        assert np.min(np.abs(eigenvalues)) < 1e-5
    
    def test_zero_matrix(self):
        """Test zero matrix (all eigenvalues zero)."""
        matrix = np.zeros((3, 3), dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        expected = np.zeros(3)
        np.testing.assert_allclose(eigenvalues, expected, atol=1e-10)
    
    def test_very_large_eigenvalues(self):
        """Test matrix with very large eigenvalues."""
        matrix = np.diag([1e10, 1e8, 1e6])
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        expected = np.sort([1e6, 1e8, 1e10])
        np.testing.assert_allclose(np.sort(eigenvalues), expected, rtol=1e-8)
    
    def test_very_small_eigenvalues(self):
        """Test matrix with very small eigenvalues."""
        matrix = np.diag([1e-10, 1e-8, 1e-6])
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        expected = np.sort([1e-10, 1e-8, 1e-6])
        np.testing.assert_allclose(np.sort(eigenvalues), expected, rtol=1e-6)


class TestSpecialCases:
    """Test special matrix types."""
    
    def test_symmetric_with_repeated_eigenvalues(self):
        """Test matrix with repeated eigenvalues."""
        matrix = np.array([[2.0, 0.0, 0.0],
                          [0.0, 2.0, 0.0],
                          [0.0, 0.0, 3.0]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        # Should have eigenvalues [2, 2, 3]
        expected = np.array([2.0, 2.0, 3.0])
        np.testing.assert_allclose(np.sort(eigenvalues), expected, rtol=1e-10)
    
    def test_negative_eigenvalues(self):
        """Test matrix with negative eigenvalues."""
        matrix = np.diag([-3.0, -1.0, 2.0])
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        expected = np.array([-3.0, -1.0, 2.0])
        np.testing.assert_allclose(np.sort(eigenvalues), expected, rtol=1e-10)
    
    def test_tridiagonal(self):
        """Test tridiagonal symmetric matrix."""
        matrix = np.array([[2.0, 1.0, 0.0, 0.0],
                          [1.0, 2.0, 1.0, 0.0],
                          [0.0, 1.0, 2.0, 1.0],
                          [0.0, 0.0, 1.0, 2.0]], dtype=float)
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        
        assert eigenvalues.shape == (4,)
        # All eigenvalues should be real for symmetric matrix
        assert np.all(np.isreal(eigenvalues))


class TestPerformance:
    """Test performance characteristics vs C implementation."""
    
    def test_performance_marker_small(self):
        """Marker for small matrix performance (should be comparable to C)."""
        matrix = np.random.randn(5, 5)
        matrix = (matrix + matrix.T) / 2
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        assert eigenvalues.shape == (5,)
    
    def test_performance_marker_medium(self):
        """Marker for medium matrix (NumPy should start to win)."""
        matrix = np.random.randn(50, 50)
        matrix = (matrix + matrix.T) / 2
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        assert eigenvalues.shape == (50,)
    
    def test_performance_marker_large(self):
        """Marker for large matrix (NumPy 10-100x faster than C)."""
        matrix = np.random.randn(200, 200)
        matrix = (matrix + matrix.T) / 2
        
        eigenvalues, eigenvectors = diagonalise_dbl(matrix)
        assert eigenvalues.shape == (200,)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
