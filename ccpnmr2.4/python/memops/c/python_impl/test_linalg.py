"""
Tests for linalg.py - Linear algebra operations
"""

import pytest
from memops.c.python_impl.linalg import (
    matrix_matrix_multiply, matrix_vector_multiply, matrix_transpose,
    LinAlgOps
)


class TestMatrixMatrixMultiply:
    """Test matrix-matrix multiplication."""
    
    def test_2x2_multiply(self):
        """Multiply 2x2 matrices."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = matrix_matrix_multiply(A, B)
        
        # [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
        assert C == [[19, 22], [43, 50]]
    
    def test_3x3_multiply(self):
        """Multiply 3x3 matrices."""
        A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Identity
        B = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        C = matrix_matrix_multiply(A, B)
        
        assert C == B  # A is identity
    
    def test_non_square_multiply(self):
        """Multiply non-square matrices."""
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3
        B = [[1, 2], [3, 4], [5, 6]]  # 3x2
        C = matrix_matrix_multiply(A, B)  # Should be 2x2
        
        # [[1*1+2*3+3*5, 1*2+2*4+3*6], [4*1+5*3+6*5, 4*2+5*4+6*6]]
        assert C == [[22, 28], [49, 64]]
    
    def test_vector_as_column_matrix(self):
        """Multiply matrix by column vector (nx1)."""
        A = [[1, 2], [3, 4]]  # 2x2
        B = [[5], [6]]  # 2x1
        C = matrix_matrix_multiply(A, B)  # Should be 2x1
        
        assert C == [[17], [39]]
    
    def test_incompatible_dimensions(self):
        """Error on incompatible dimensions."""
        A = [[1, 2], [3, 4]]  # 2x2
        B = [[1, 2, 3]]  # 1x3
        
        with pytest.raises(ValueError, match="Incompatible dimensions"):
            matrix_matrix_multiply(A, B)
    
    def test_empty_matrix_error(self):
        """Error on empty matrix."""
        with pytest.raises(ValueError):
            matrix_matrix_multiply([], [[1]])
        
        with pytest.raises(ValueError):
            matrix_matrix_multiply([[1]], [])
    
    def test_1x1_multiply(self):
        """Multiply 1x1 matrices."""
        A = [[5]]
        B = [[7]]
        C = matrix_matrix_multiply(A, B)
        assert C == [[35]]
    
    def test_rectangular_multiply(self):
        """Test various rectangular multiplications."""
        # 1x3 * 3x1 = 1x1
        A = [[1, 2, 3]]
        B = [[4], [5], [6]]
        C = matrix_matrix_multiply(A, B)
        assert C == [[32]]  # 1*4 + 2*5 + 3*6


class TestMatrixVectorMultiply:
    """Test matrix-vector multiplication."""
    
    def test_2x2_vector(self):
        """Multiply 2x2 matrix by vector."""
        A = [[1, 2], [3, 4]]
        x = [5, 6]
        y = matrix_vector_multiply(A, x)
        
        # [1*5+2*6, 3*5+4*6] = [17, 39]
        assert y == [17, 39]
    
    def test_3x3_vector(self):
        """Multiply 3x3 matrix by vector."""
        A = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Identity
        x = [7, 8, 9]
        y = matrix_vector_multiply(A, x)
        
        assert y == x  # Identity matrix
    
    def test_rectangular_matrix(self):
        """Multiply rectangular matrix by vector."""
        A = [[1, 2], [3, 4], [5, 6]]  # 3x2
        x = [7, 8]  # length 2
        y = matrix_vector_multiply(A, x)  # Should be length 3
        
        # [1*7+2*8, 3*7+4*8, 5*7+6*8] = [23, 53, 83]
        assert y == [23, 53, 83]
    
    def test_single_row(self):
        """Multiply single-row matrix by vector."""
        A = [[1, 2, 3]]  # 1x3
        x = [4, 5, 6]  # length 3
        y = matrix_vector_multiply(A, x)  # Should be length 1
        
        assert y == [32]  # 1*4 + 2*5 + 3*6
    
    def test_incompatible_dimensions(self):
        """Error on incompatible dimensions."""
        A = [[1, 2], [3, 4]]  # 2x2
        x = [1, 2, 3]  # Wrong length
        
        with pytest.raises(ValueError, match="Incompatible dimensions"):
            matrix_vector_multiply(A, x)
    
    def test_empty_error(self):
        """Error on empty inputs."""
        with pytest.raises(ValueError):
            matrix_vector_multiply([], [1, 2])
        
        with pytest.raises(ValueError):
            matrix_vector_multiply([[1, 2]], [])
    
    def test_zero_vector(self):
        """Multiply by zero vector."""
        A = [[1, 2], [3, 4]]
        x = [0, 0]
        y = matrix_vector_multiply(A, x)
        
        assert y == [0, 0]


class TestMatrixTranspose:
    """Test matrix transpose."""
    
    def test_2x2_transpose(self):
        """Transpose 2x2 matrix."""
        A = [[1, 2], [3, 4]]
        B = matrix_transpose(A)
        
        assert B == [[1, 3], [2, 4]]
    
    def test_3x3_transpose(self):
        """Transpose 3x3 matrix."""
        A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        B = matrix_transpose(A)
        
        assert B == [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    
    def test_rectangular_transpose(self):
        """Transpose rectangular matrix."""
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3
        B = matrix_transpose(A)  # Should be 3x2
        
        assert B == [[1, 4], [2, 5], [3, 6]]
    
    def test_single_row_transpose(self):
        """Transpose single row to column."""
        A = [[1, 2, 3]]  # 1x3
        B = matrix_transpose(A)  # Should be 3x1
        
        assert B == [[1], [2], [3]]
    
    def test_single_column_transpose(self):
        """Transpose single column to row."""
        A = [[1], [2], [3]]  # 3x1
        B = matrix_transpose(A)  # Should be 1x3
        
        assert B == [[1, 2, 3]]
    
    def test_double_transpose(self):
        """Transpose twice returns original."""
        A = [[1, 2, 3], [4, 5, 6]]
        B = matrix_transpose(matrix_transpose(A))
        
        assert B == A
    
    def test_empty_matrix_error(self):
        """Error on empty matrix."""
        with pytest.raises(ValueError):
            matrix_transpose([])


class TestLinAlgOpsClass:
    """Test LinAlgOps wrapper class."""
    
    def test_matmul(self):
        """Test LinAlgOps.matmul."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = LinAlgOps.matmul(A, B)
        
        assert C == [[19, 22], [43, 50]]
    
    def test_matvec(self):
        """Test LinAlgOps.matvec."""
        A = [[1, 2], [3, 4]]
        x = [5, 6]
        y = LinAlgOps.matvec(A, x)
        
        assert y == [17, 39]
    
    def test_transpose(self):
        """Test LinAlgOps.transpose."""
        A = [[1, 2], [3, 4]]
        B = LinAlgOps.transpose(A)
        
        assert B == [[1, 3], [2, 4]]
    
    def test_identity(self):
        """Test LinAlgOps.identity."""
        I = LinAlgOps.identity(3)
        
        assert I == [[1.0, 0.0, 0.0], 
                     [0.0, 1.0, 0.0], 
                     [0.0, 0.0, 1.0]]
    
    def test_zeros(self):
        """Test LinAlgOps.zeros."""
        Z = LinAlgOps.zeros(2, 3)
        
        assert Z == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    
    def test_zeros_square(self):
        """Test LinAlgOps.zeros with single argument."""
        Z = LinAlgOps.zeros(3)
        
        assert Z == [[0.0, 0.0, 0.0], 
                     [0.0, 0.0, 0.0], 
                     [0.0, 0.0, 0.0]]
    
    def test_trace(self):
        """Test LinAlgOps.trace."""
        A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        t = LinAlgOps.trace(A)
        
        assert t == 15  # 1 + 5 + 9
    
    def test_trace_rectangular(self):
        """Test trace of rectangular matrix."""
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3
        t = LinAlgOps.trace(A)
        
        assert t == 6  # 1 + 5 (only 2 diagonal elements)
    
    def test_matrix_add(self):
        """Test LinAlgOps.matrix_add."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = LinAlgOps.matrix_add(A, B)
        
        assert C == [[6, 8], [10, 12]]
    
    def test_scalar_multiply(self):
        """Test LinAlgOps.scalar_multiply."""
        A = [[1, 2], [3, 4]]
        B = LinAlgOps.scalar_multiply(3, A)
        
        assert B == [[3, 6], [9, 12]]


class TestNumericalProperties:
    """Test numerical properties and accuracy."""
    
    def test_associativity(self):
        """Test (AB)C = A(BC)."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = [[9, 10], [11, 12]]
        
        AB = matrix_matrix_multiply(A, B)
        BC = matrix_matrix_multiply(B, C)
        
        ABC1 = matrix_matrix_multiply(AB, C)
        ABC2 = matrix_matrix_multiply(A, BC)
        
        assert ABC1 == ABC2
    
    def test_distributivity(self):
        """Test A(B+C) = AB + AC."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = [[1, 1], [1, 1]]
        
        B_plus_C = LinAlgOps.matrix_add(B, C)
        left = matrix_matrix_multiply(A, B_plus_C)
        
        AB = matrix_matrix_multiply(A, B)
        AC = matrix_matrix_multiply(A, C)
        right = LinAlgOps.matrix_add(AB, AC)
        
        assert left == right
    
    def test_transpose_product(self):
        """Test (AB)^T = B^T A^T."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        
        AB = matrix_matrix_multiply(A, B)
        left = matrix_transpose(AB)
        
        At = matrix_transpose(A)
        Bt = matrix_transpose(B)
        right = matrix_matrix_multiply(Bt, At)
        
        assert left == right
    
    def test_identity_multiplication(self):
        """Test AI = IA = A."""
        A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        I = LinAlgOps.identity(3)
        
        AI = matrix_matrix_multiply(A, I)
        IA = matrix_matrix_multiply(I, A)
        
        assert AI == A
        assert IA == A


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_large_matrix(self):
        """Test with larger matrices."""
        n = 50
        A = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        x = list(range(n))
        
        # Identity matrix times vector
        y = matrix_vector_multiply(A, x)
        assert y == x
    
    def test_floating_point_values(self):
        """Test with floating point values."""
        A = [[1.5, 2.5], [3.5, 4.5]]
        B = [[0.5, 1.5], [2.5, 3.5]]
        C = matrix_matrix_multiply(A, B)
        
        # Check approximate equality
        assert abs(C[0][0] - 7.0) < 1e-10
        assert abs(C[0][1] - 11.0) < 1e-10
        assert abs(C[1][0] - 13.0) < 1e-10
        assert abs(C[1][1] - 21.0) < 1e-10
    
    def test_negative_values(self):
        """Test with negative values."""
        A = [[-1, 2], [3, -4]]
        B = [[5, -6], [-7, 8]]
        C = matrix_matrix_multiply(A, B)
        
        assert C == [[-19, 22], [43, -50]]
    
    def test_zero_matrix(self):
        """Test with zero matrix."""
        A = [[0, 0], [0, 0]]
        B = [[1, 2], [3, 4]]
        C = matrix_matrix_multiply(A, B)
        
        assert C == [[0, 0], [0, 0]]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
