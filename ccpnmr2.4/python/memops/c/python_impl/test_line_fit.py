"""
Test suite for line fitting implementations.

Tests both pure Python and Numba versions for correctness and consistency.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

import line_fit
import line_fit_numba


class TestLineFitPython(unittest.TestCase):
    """Test pure Python line fit implementation."""
    
    def test_perfect_line(self):
        """Test fitting a perfect line y = 2 + 3x."""
        x = [0.0, 1.0, 2.0, 3.0, 4.0]
        y = [2.0, 5.0, 8.0, 11.0, 14.0]
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['a'], 2.0, places=10)
        self.assertAlmostEqual(result['b'], 3.0, places=10)
    
    def test_noisy_data(self):
        """Test fitting line with noise."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.1, 4.0, 5.9, 8.1, 10.0]  # Approximately y = 2x
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        # Should be close to a=0, b=2
        self.assertAlmostEqual(result['a'], 0.0, delta=0.5)
        self.assertAlmostEqual(result['b'], 2.0, delta=0.1)
    
    def test_horizontal_line(self):
        """Test fitting a horizontal line (slope = 0)."""
        x = [1.0, 2.0, 3.0, 4.0]
        y = [5.0, 5.0, 5.0, 5.0]
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['a'], 5.0, places=5)
        self.assertAlmostEqual(result['b'], 0.0, places=10)
    
    def test_vertical_spread(self):
        """Test data with vertical spread (non-zero slope)."""
        x = [0.0, 1.0, 2.0]
        y = [0.0, 1.0, 2.0]
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['a'], 0.0, places=10)
        self.assertAlmostEqual(result['b'], 1.0, places=10)
    
    def test_weighted_fit(self):
        """Test weighted fit with different sigmas."""
        x = [1.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 6.0, 8.0]
        sigma = [0.5, 0.5, 2.0, 2.0]  # First two points more precise
        
        result = line_fit.line_fit(x, y, sigma=sigma)
        
        self.assertIsNone(result['error'])
        # With weighting, should still be close to y = 2x
        self.assertAlmostEqual(result['b'], 2.0, delta=0.2)
    
    def test_error_same_x_values(self):
        """Test error when all x values are the same."""
        x = [1.0, 1.0, 1.0]
        y = [2.0, 3.0, 4.0]
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNotNone(result['error'])
        self.assertIn('x values all the same', result['error'])
    
    def test_error_too_few_points(self):
        """Test error with only one data point."""
        x = [1.0]
        y = [2.0]
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNotNone(result['error'])
        self.assertIn('number of parameters < 2', result['error'])
    
    def test_fitted_values(self):
        """Test that fitted values are computed correctly."""
        x = [0.0, 1.0, 2.0, 3.0]
        y = [1.0, 3.0, 5.0, 7.0]  # y = 1 + 2x
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        expected_yfit = [1.0, 3.0, 5.0, 7.0]
        
        for i in range(len(x)):
            self.assertAlmostEqual(result['yfit'][i], expected_yfit[i], places=10)
    
    def test_simple_wrapper(self):
        """Test simple_line_fit wrapper."""
        x = [0.0, 1.0, 2.0]
        y = [3.0, 5.0, 7.0]  # y = 3 + 2x
        
        a, b = line_fit.simple_line_fit(x, y)
        
        self.assertAlmostEqual(a, 3.0, places=10)
        self.assertAlmostEqual(b, 2.0, places=10)
    
    def test_negative_slope(self):
        """Test fitting line with negative slope."""
        x = [0.0, 1.0, 2.0, 3.0]
        y = [10.0, 8.0, 6.0, 4.0]  # y = 10 - 2x
        
        result = line_fit.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['a'], 10.0, places=10)
        self.assertAlmostEqual(result['b'], -2.0, places=10)


class TestLineFitNumba(unittest.TestCase):
    """Test Numba line fit implementation."""
    
    def test_perfect_line(self):
        """Test fitting a perfect line with Numba."""
        x = [0.0, 1.0, 2.0, 3.0, 4.0]
        y = [2.0, 5.0, 8.0, 11.0, 14.0]
        
        result = line_fit_numba.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['a'], 2.0, places=10)
        self.assertAlmostEqual(result['b'], 3.0, places=10)
    
    def test_noisy_data(self):
        """Test fitting line with noise using Numba."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.1, 4.0, 5.9, 8.1, 10.0]
        
        result = line_fit_numba.line_fit(x, y)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['a'], 0.0, delta=0.5)
        self.assertAlmostEqual(result['b'], 2.0, delta=0.1)
    
    def test_weighted_fit(self):
        """Test weighted fit with Numba."""
        x = [1.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 6.0, 8.0]
        sigma = [0.5, 0.5, 2.0, 2.0]
        
        result = line_fit_numba.line_fit(x, y, sigma=sigma)
        
        self.assertIsNone(result['error'])
        self.assertAlmostEqual(result['b'], 2.0, delta=0.2)
    
    def test_error_same_x_values(self):
        """Test error detection with Numba."""
        x = [1.0, 1.0, 1.0]
        y = [2.0, 3.0, 4.0]
        
        result = line_fit_numba.line_fit(x, y)
        
        self.assertIsNotNone(result['error'])
    
    def test_simple_wrapper(self):
        """Test Numba simple wrapper."""
        x = [0.0, 1.0, 2.0]
        y = [3.0, 5.0, 7.0]
        
        a, b = line_fit_numba.simple_line_fit(x, y)
        
        self.assertAlmostEqual(a, 3.0, places=10)
        self.assertAlmostEqual(b, 2.0, places=10)


class TestConsistency(unittest.TestCase):
    """Test consistency between Python and Numba implementations."""
    
    def test_consistency_perfect_line(self):
        """Check Python and Numba give same results for perfect line."""
        x = [0.0, 1.0, 2.0, 3.0, 4.0]
        y = [2.0, 5.0, 8.0, 11.0, 14.0]
        
        result_py = line_fit.line_fit(x, y)
        result_nb = line_fit_numba.line_fit(x, y)
        
        self.assertAlmostEqual(result_py['a'], result_nb['a'], places=10)
        self.assertAlmostEqual(result_py['b'], result_nb['b'], places=10)
        self.assertAlmostEqual(result_py['std_a'], result_nb['std_a'], places=10)
        self.assertAlmostEqual(result_py['std_b'], result_nb['std_b'], places=10)
    
    def test_consistency_noisy_data(self):
        """Check consistency with noisy data."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.1, 4.0, 5.9, 8.1, 10.0]
        
        result_py = line_fit.line_fit(x, y)
        result_nb = line_fit_numba.line_fit(x, y)
        
        self.assertAlmostEqual(result_py['a'], result_nb['a'], places=8)
        self.assertAlmostEqual(result_py['b'], result_nb['b'], places=8)
        self.assertAlmostEqual(result_py['goodness'], result_nb['goodness'], places=8)
    
    def test_consistency_weighted(self):
        """Check consistency for weighted fit."""
        x = [1.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 6.0, 8.0]
        sigma = [0.5, 0.5, 2.0, 2.0]
        
        result_py = line_fit.line_fit(x, y, sigma=sigma)
        result_nb = line_fit_numba.line_fit(x, y, sigma=sigma)
        
        self.assertAlmostEqual(result_py['a'], result_nb['a'], places=8)
        self.assertAlmostEqual(result_py['b'], result_nb['b'], places=8)
        self.assertAlmostEqual(result_py['std_a'], result_nb['std_a'], places=8)
        self.assertAlmostEqual(result_py['std_b'], result_nb['std_b'], places=8)
    
    def test_consistency_fitted_values(self):
        """Check fitted values match between implementations."""
        x = [0.0, 1.0, 2.0, 3.0]
        y = [1.0, 3.0, 5.0, 7.0]
        
        result_py = line_fit.line_fit(x, y)
        result_nb = line_fit_numba.line_fit(x, y)
        
        for i in range(len(x)):
            self.assertAlmostEqual(result_py['yfit'][i], result_nb['yfit'][i], places=10)
    
    def test_consistency_errors(self):
        """Check both detect same error conditions."""
        x = [1.0, 1.0, 1.0]
        y = [2.0, 3.0, 4.0]
        
        result_py = line_fit.line_fit(x, y)
        result_nb = line_fit_numba.line_fit(x, y)
        
        self.assertIsNotNone(result_py['error'])
        self.assertIsNotNone(result_nb['error'])


if __name__ == '__main__':
    unittest.main()
