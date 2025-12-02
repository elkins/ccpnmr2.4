"""
Tests for fit1d.py - 1D function minimization
"""

import pytest
import numpy as np
import math
from memops.c.python_impl.fit1d import (
    bracket_minimum, golden_search, brent_search,
    minimize_scalar, find_minimum, Fit1dError
)


class TestBracketMinimum:
    """Test bracket_minimum function."""
    
    def test_simple_parabola(self):
        """Test bracketing a simple parabola."""
        def parabola(x, param):
            return (x - 3.0)**2
        
        ax, bx, cx = bracket_minimum(0.0, 1.0, parabola)
        
        # Check ordering
        assert ax < bx < cx or cx < bx < ax
        
        # Check that middle point has lowest value
        fa = parabola(ax, None)
        fb = parabola(bx, None)
        fc = parabola(cx, None)
        assert fb < fa and fb < fc
    
    def test_quartic(self):
        """Test bracketing a quartic function."""
        def quartic(x, param):
            return (x - 2.5)**4 + 1.0
        
        ax, bx, cx = bracket_minimum(0.0, 1.0, quartic)
        
        fa = quartic(ax, None)
        fb = quartic(bx, None)
        fc = quartic(cx, None)
        assert fb < fa and fb < fc
    
    def test_with_params(self):
        """Test bracketing with additional parameters."""
        def shifted_parabola(x, param):
            shift = param if param else 0
            return (x - shift)**2
        
        ax, bx, cx = bracket_minimum(0.0, 1.0, shifted_parabola, 5.0)
        
        # Minimum should be near x=5
        assert 3.0 < bx < 7.0


class TestGoldenSearch:
    """Test golden_search function."""
    
    def test_simple_minimum(self):
        """Test finding minimum of parabola."""
        def parabola(x, param):
            return (x - 3.0)**2
        
        xmin, fmin = golden_search(2.0, 3.0, 4.0, parabola)
        
        assert abs(xmin - 3.0) < 0.05  # Within default tolerance
        assert abs(fmin - 0.0) < 0.01
    
    def test_tight_tolerance(self):
        """Test with tighter tolerance."""
        def parabola(x, param):
            return (x - 3.0)**2
        
        xmin, fmin = golden_search(2.0, 3.0, 4.0, parabola, tol=0.001)
        
        assert abs(xmin - 3.0) < 0.005  # Much tighter
        assert abs(fmin - 0.0) < 0.0001
    
    def test_quartic(self):
        """Test with quartic function."""
        def quartic(x, param):
            return (x - 2.5)**4
        
        xmin, fmin = golden_search(1.0, 2.5, 4.0, quartic)
        
        assert abs(xmin - 2.5) < 0.05
        assert fmin < 0.01
    
    def test_with_offset(self):
        """Test function with vertical offset."""
        def offset_parabola(x, param):
            return (x - 1.5)**2 + 10.0
        
        xmin, fmin = golden_search(0.0, 1.5, 3.0, offset_parabola)
        
        assert abs(xmin - 1.5) < 0.05
        assert abs(fmin - 10.0) < 0.01


class TestBrentSearch:
    """Test brent_search function."""
    
    def test_simple_minimum(self):
        """Test Brent's method on parabola."""
        def parabola(x, param):
            return (x - 3.0)**2
        
        xmin, fmin = brent_search(2.0, 3.0, 4.0, parabola)
        
        # Brent should be more accurate than golden
        assert abs(xmin - 3.0) < 0.01
        assert abs(fmin - 0.0) < 0.0001
    
    def test_quartic(self):
        """Test on quartic function."""
        def quartic(x, param):
            return (x - 2.5)**4
        
        xmin, fmin = brent_search(1.0, 2.5, 4.0, quartic)
        
        assert abs(xmin - 2.5) < 0.01
        assert fmin < 0.001
    
    def test_faster_than_golden(self):
        """Verify Brent converges faster than golden section."""
        def steep_valley(x, param):
            return 100 * (x - 2.0)**2 + 0.01 * x**4
        
        # Brent should give more accurate result
        xmin_b, fmin_b = brent_search(0.0, 2.0, 4.0, steep_valley)
        xmin_g, fmin_g = golden_search(0.0, 2.0, 4.0, steep_valley)
        
        # Brent typically more accurate for smooth functions
        assert abs(xmin_b - 2.0) <= abs(xmin_g - 2.0)


class TestMinimizeScalar:
    """Test minimize_scalar high-level interface."""
    
    def test_bounded(self):
        """Test bounded minimization."""
        def cubic(x, param):
            return (x - 2)**3 + 10
        
        xmin, fmin = minimize_scalar(cubic, bounds=(0, 5))
        
        # Minimum at boundary (x=0) for cubic within bounds
        assert xmin < 0.1  # Near lower bound
    
    def test_unbounded(self):
        """Test unbounded minimization."""
        def parabola(x, param):
            return (x + 1.5)**2
        
        xmin, fmin = minimize_scalar(parabola)
        
        assert abs(xmin - (-1.5)) < 0.01
        assert abs(fmin) < 0.001
    
    def test_golden_method(self):
        """Test with golden method explicitly."""
        def parabola(x, param):
            return (x - 3)**2
        
        xmin, fmin = minimize_scalar(parabola, bounds=(2, 4), method='golden')
        
        assert abs(xmin - 3.0) < 0.05
    
    def test_brent_method(self):
        """Test with Brent method explicitly."""
        def parabola(x, param):
            return (x - 3)**2
        
        xmin, fmin = minimize_scalar(parabola, bounds=(2, 4), method='brent')
        
        assert abs(xmin - 3.0) < 0.01


class TestFindMinimum:
    """Test find_minimum complete workflow."""
    
    def test_simple_parabola(self):
        """Test complete workflow on parabola."""
        def parabola(x, param):
            return (x - 5.0)**2
        
        xmin, fmin = find_minimum(0.0, 1.0, parabola)
        
        assert abs(xmin - 5.0) < 0.1
        assert abs(fmin) < 0.01
    
    def test_quartic(self):
        """Test on quartic function."""
        def quartic(x, param):
            return (x + 2.3)**4 + 5.0
        
        xmin, fmin = find_minimum(-5.0, 0.0, quartic)
        
        assert abs(xmin - (-2.3)) < 0.1
        assert abs(fmin - 5.0) < 0.1
    
    def test_with_params(self):
        """Test with parameter passing."""
        def scaled_parabola(x, param):
            scale = param if param else 1.0
            return scale * (x - 2.0)**2
        
        xmin, fmin = find_minimum(0.0, 1.0, scaled_parabola, param=3.0)
        
        assert abs(xmin - 2.0) < 0.1
        assert abs(fmin) < 0.1


class TestRealWorldFunctions:
    """Test with realistic scientific functions."""
    
    def test_gaussian(self):
        """Test minimizing negative Gaussian (finding maximum)."""
        def neg_gaussian(x, param):
            mean, sigma = 2.0, 0.5
            return -np.exp(-0.5 * ((x - mean) / sigma)**2)
        
        xmin, fmin = find_minimum(0.0, 3.0, neg_gaussian)
        
        # Should find peak at mean
        assert abs(xmin - 2.0) < 0.1
        assert abs(fmin - (-1.0)) < 0.01
    
    def test_rosenbrock_slice(self):
        """Test on 1D slice of Rosenbrock function."""
        def rosenbrock_1d(x, param):
            # Along y=1 line: f(x,1) = (1-x)^2 + 100(1-x^2)^2
            return (1 - x)**2 + 100 * (1 - x**2)**2
        
        xmin, fmin = find_minimum(0.0, 0.5, rosenbrock_1d)
        
        # Minimum should be at x=1
        assert abs(xmin - 1.0) < 0.1
        assert fmin < 1.0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_bracket(self):
        """Test with invalid initial bracket."""
        def parabola(x, param):
            return (x - 3)**2
        
        # Should still work - bracket_minimum will find valid bracket
        ax, bx, cx = bracket_minimum(10.0, 11.0, parabola)
        assert ax < bx < cx or cx < bx < ax
    
    def test_flat_function(self):
        """Test with constant function."""
        def constant(x, param):
            return 5.0
        
        # SciPy will reject this - expect error
        with pytest.raises(Fit1dError):
            xmin, fmin = golden_search(0.0, 1.0, 2.0, constant)
    
    def test_no_minimum_bounded(self):
        """Test linear function in bounded region."""
        def linear(x, param):
            return 2 * x + 1
        
        # Should return boundary point
        xmin, fmin = minimize_scalar(linear, bounds=(0, 10))
        assert xmin < 0.05  # Lower bound within tolerance


class TestToleranceEffect:
    """Test effect of tolerance parameter."""
    
    def test_tolerance_accuracy(self):
        """Verify tighter tolerance gives more accurate result."""
        def parabola(x, param):
            return (x - math.pi)**2
        
        # Loose tolerance
        xmin_loose, _ = golden_search(2.0, 3.0, 4.0, parabola, tol=0.1)
        
        # Tight tolerance
        xmin_tight, _ = golden_search(2.0, 3.0, 4.0, parabola, tol=0.001)
        
        # Tight should be more accurate
        assert abs(xmin_tight - math.pi) < abs(xmin_loose - math.pi)
    
    def test_default_tolerance(self):
        """Verify default tolerance is 0.03."""
        def parabola(x, param):
            return (x - 3.0)**2
        
        xmin, _ = golden_search(2.0, 3.0, 4.0, parabola)
        
        # With default tolerance, should be within ~0.05 of true minimum
        assert abs(xmin - 3.0) < 0.05


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
