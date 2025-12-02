"""
Integration tests for CCPN NMR C-to-Python converted modules.

These tests verify that converted modules work together correctly in
realistic workflows, ensuring that the modular conversions integrate
properly into the larger system.
"""

import pytest
import math
from memops.c.python_impl.geometry import *
from memops.c.python_impl.gauss_jordan import gauss_jordan_solve
from memops.c.python_impl.line_fit import line_fit
from memops.c.python_impl.linalg import matrix_matrix_multiply, matrix_vector_multiply
from memops.c.python_impl.random import set_seed, normal


class TestGeometryWorkflows:
    """Test geometry module integrations."""
    
    def test_transformation_pipeline(self):
        """Test chaining geometry transformations."""
        # Create points
        points = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        
        # Rotate each point using rotation matrix
        axis = [0.0, 0.0, 1.0]  # Z-axis
        angle = math.pi / 2  # 90 degrees
        
        rot_matrix = rotation_matrix(axis, angle)
        from memops.c.python_impl.linalg import matrix_vector_multiply
        rotated = [matrix_vector_multiply(rot_matrix, p) for p in points]
        
        # Calculate distances between rotated points
        def distance(v1, v2):
            diff = [v1[i] - v2[i] for i in range(len(v1))]
            return vector_length(diff)
        
        d01 = distance(rotated[0], rotated[1])
        d02 = distance(rotated[0], rotated[2])
        d12 = distance(rotated[1], rotated[2])
        
        # All distances should be sqrt(2) (corners of unit cube)
        assert abs(d01 - math.sqrt(2)) < 1e-6
        assert abs(d02 - math.sqrt(2)) < 1e-6
        assert abs(d12 - math.sqrt(2)) < 1e-6
    
    def test_plane_fitting_workflow(self):
        """Test fitting a plane to points."""
        # Create coplanar points
        points = [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0]
        ]
        
        # Compute plane normal from two edge vectors
        v1 = [points[1][i] - points[0][i] for i in range(3)]
        v2 = [points[2][i] - points[0][i] for i in range(3)]
        normal = normalise_vector(cross_product(v1, v2))
        
        # Normal should point along Z axis
        assert abs(normal[0]) < 1e-6
        assert abs(normal[1]) < 1e-6
        assert abs(abs(normal[2]) - 1.0) < 1e-6


class TestLinearAlgebraIntegration:
    """Test linear algebra operations together."""
    
    def test_matrix_chain_multiplication(self):
        """Test A × B × C matrix chain."""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        C = [[9, 10], [11, 12]]
        
        # (A × B) × C
        AB = matrix_matrix_multiply(A, B)
        ABC = matrix_matrix_multiply(AB, C)
        
        # Should get valid result
        assert len(ABC) == 2
        assert len(ABC[0]) == 2
    
    def test_gauss_jordan_with_linalg(self):
        """Test Gauss-Jordan with matrix operations."""
        # System: 2x + 3y = 8, 4x + 5y = 14
        A = [[2.0, 3.0], [4.0, 5.0]]
        b = [8.0, 14.0]
        
        # Solve using Gauss-Jordan (returns tuple)
        is_singular, a_inverse, solution = gauss_jordan_solve(A, b)
        
        # Verify not singular
        assert not is_singular
        
        # Verify solution has correct length
        assert len(solution) == 2
        
        # Verify solution: A × x = b (use original matrix values)
        A_orig = [[2.0, 3.0], [4.0, 5.0]]
        result = matrix_vector_multiply(A_orig, solution)
        assert abs(result[0] - 8.0) < 1e-10
        assert abs(result[1] - 14.0) < 1e-10


class TestFittingWorkflows:
    """Test fitting module integrations."""
    
    def test_linear_fit_workflow(self):
        """Test linear fit with noise."""
        # Generate linear data with noise
        set_seed(42)
        x = [float(i) for i in range(10)]
        y_linear = [2.0 + 3.0 * xi + normal(0, 0.1) for xi in x]
        
        # Fit linear (returns dict)
        result = line_fit(x, y_linear)
        assert result['error'] is None
        assert abs(result['a'] - 2.0) < 0.5  # Intercept
        assert abs(result['b'] - 3.0) < 0.5  # Slope


class TestDataStructureIntegration:
    """Test data structure interactions."""
    
    def test_hash_table_with_int_array(self):
        """Test using IntArray as hash table keys."""
        from memops.c.python_impl.hash_table import HashTable
        from memops.c.python_impl.int_array import IntArray
        
        # Create hash table for multi-dimensional indices
        table = HashTable(
            equal_func=lambda a1, a2: a1 == a2,
            hash_func=lambda a: hash(a)
        )
        
        # Store data for multi-dimensional grid
        for i in range(3):
            for j in range(3):
                key = IntArray([i, j])
                table[key] = i * 10 + j
        
        # Retrieve data
        key = IntArray([1, 2])
        assert table[key] == 12
    
    def test_utility_functions_with_fitting(self):
        """Test utility functions in fitting context."""
        from memops.c.python_impl.utility import (
            ceil_power_of_2, floor_power_of_2
        )
        
        # Determine FFT size for NMR data
        data_size = 1500
        fft_size = ceil_power_of_2(data_size)
        
        assert fft_size == 2048
        assert fft_size >= data_size
        assert floor_power_of_2(fft_size) == fft_size  # Is power of 2


class TestStatisticalWorkflows:
    """Test statistical analysis workflows."""
    
    def test_monte_carlo_error_estimation(self):
        """Test Monte Carlo error estimation for fits."""
        set_seed(42)
        
        # True parameters
        true_params = {'a': 2.0, 'b': 3.0}
        
        # Generate data
        x = [float(i) for i in range(10)]
        y_true = [true_params['a'] + true_params['b'] * xi for xi in x]
        
        # Run Monte Carlo trials
        n_trials = 50
        fitted_slopes = []
        
        for trial in range(n_trials):
            # Add noise
            y_noisy = [yi + normal(0, 0.5) for yi in y_true]
            
            # Fit (returns dict)
            result = line_fit(x, y_noisy)
            if result['error'] is None:
                fitted_slopes.append(result['b'])
        
        # Check distribution of fitted slopes
        mean_slope = sum(fitted_slopes) / len(fitted_slopes)
        assert abs(mean_slope - true_params['b']) < 0.2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
