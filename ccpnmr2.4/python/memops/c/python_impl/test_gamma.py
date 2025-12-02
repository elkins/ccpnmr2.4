"""
Tests for gamma.py - Gamma functions using SciPy special functions
"""

import pytest
import numpy as np
import math
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gamma import (
    gamma_func, log_gamma, incomplete_gamma, incomplete_gamma_complement,
    regularized_incomplete_gamma, regularized_incomplete_gamma_complement,
    digamma, polygamma, beta_func, log_beta, factorial, log_factorial
)


class TestGammaFunction:
    """Test the gamma function."""
    
    def test_gamma_positive_integers(self):
        """Test gamma function for positive integers: Γ(n) = (n-1)!"""
        assert abs(gamma_func(1) - 1.0) < 1e-10  # Γ(1) = 0! = 1
        assert abs(gamma_func(2) - 1.0) < 1e-10  # Γ(2) = 1! = 1
        assert abs(gamma_func(3) - 2.0) < 1e-10  # Γ(3) = 2! = 2
        assert abs(gamma_func(4) - 6.0) < 1e-10  # Γ(4) = 3! = 6
        assert abs(gamma_func(5) - 24.0) < 1e-10  # Γ(5) = 4! = 24
    
    def test_gamma_half_integer(self):
        """Test gamma function at 1/2: Γ(1/2) = √π."""
        result = gamma_func(0.5)
        expected = math.sqrt(math.pi)
        assert abs(result - expected) < 1e-10
    
    def test_gamma_array(self):
        """Test gamma function with array input."""
        x = np.array([1.0, 2.0, 3.0, 4.0])
        result = gamma_func(x)
        expected = np.array([1.0, 1.0, 2.0, 6.0])
        np.testing.assert_allclose(result, expected, rtol=1e-10)
    
    def test_gamma_large_value(self):
        """Test gamma function with large argument."""
        result = gamma_func(10)
        expected = math.factorial(9)  # Γ(10) = 9!
        assert abs(result - expected) < 1e-8


class TestLogGamma:
    """Test the log-gamma function."""
    
    def test_log_gamma_small(self):
        """Test log-gamma for small values."""
        result = log_gamma(1)
        expected = 0.0  # ln(Γ(1)) = ln(1) = 0
        assert abs(result - expected) < 1e-10
    
    def test_log_gamma_consistency(self):
        """Test log_gamma is consistent with log(gamma(x))."""
        x = 5.0
        result = log_gamma(x)
        expected = math.log(gamma_func(x))
        assert abs(result - expected) < 1e-10
    
    def test_log_gamma_large_value(self):
        """Test log-gamma for large values (more stable than gamma)."""
        result = log_gamma(100)
        # Stirling approximation: ln(n!) ≈ n*ln(n) - n
        # For Γ(100) = 99!, should be around 359
        assert 355 < result < 365
    
    def test_log_gamma_array(self):
        """Test log-gamma with array input."""
        x = np.array([1.0, 2.0, 3.0, 4.0])
        result = log_gamma(x)
        expected = np.log([1.0, 1.0, 2.0, 6.0])
        np.testing.assert_allclose(result, expected, rtol=1e-10)


class TestIncompleteGamma:
    """Test incomplete gamma functions."""
    
    def test_incomplete_gamma_lower(self):
        """Test lower incomplete gamma function."""
        # γ(a, 0) = 0
        result = incomplete_gamma(2.0, 0.0)
        assert abs(result) < 1e-10
    
    def test_incomplete_gamma_upper_limit(self):
        """Test that γ(a, ∞) = Γ(a)."""
        a = 3.0
        # At large x, γ(a, x) → Γ(a)
        result = incomplete_gamma(a, 100.0)
        expected = gamma_func(a)
        assert abs(result - expected) < 1e-5
    
    def test_incomplete_gamma_complement(self):
        """Test upper incomplete gamma function."""
        # Γ(a, 0) = Γ(a)
        a = 3.0
        result = incomplete_gamma_complement(a, 0.0)
        expected = gamma_func(a)
        assert abs(result - expected) < 1e-10
    
    def test_incomplete_gamma_sum(self):
        """Test that γ(a, x) + Γ(a, x) = Γ(a)."""
        a, x = 3.0, 2.0
        lower = incomplete_gamma(a, x)
        upper = incomplete_gamma_complement(a, x)
        total = lower + upper
        expected = gamma_func(a)
        assert abs(total - expected) < 1e-10


class TestRegularizedIncompleteGamma:
    """Test regularized (normalized) incomplete gamma functions."""
    
    def test_regularized_bounds(self):
        """Test regularized gamma is in [0, 1]."""
        a, x = 2.0, 1.0
        result = regularized_incomplete_gamma(a, x)
        assert 0.0 <= result <= 1.0
    
    def test_regularized_at_zero(self):
        """Test P(a, 0) = 0."""
        result = regularized_incomplete_gamma(2.0, 0.0)
        assert abs(result) < 1e-10
    
    def test_regularized_at_infinity(self):
        """Test P(a, ∞) = 1."""
        result = regularized_incomplete_gamma(2.0, 100.0)
        assert abs(result - 1.0) < 1e-10
    
    def test_regularized_complement_bounds(self):
        """Test Q(a, x) is in [0, 1]."""
        result = regularized_incomplete_gamma_complement(2.0, 1.0)
        assert 0.0 <= result <= 1.0
    
    def test_regularized_sum_to_one(self):
        """Test P(a, x) + Q(a, x) = 1."""
        a, x = 3.0, 2.0
        p = regularized_incomplete_gamma(a, x)
        q = regularized_incomplete_gamma_complement(a, x)
        assert abs(p + q - 1.0) < 1e-10


class TestDigamma:
    """Test digamma function (psi function)."""
    
    def test_digamma_positive(self):
        """Test digamma for positive integers."""
        # ψ(1) = -γ (Euler-Mascheroni constant ≈ -0.5772)
        result = digamma(1.0)
        assert -0.58 < result < -0.57
        
        # For large n, ψ(n) ≈ ln(n)
        result = digamma(100.0)
        expected = math.log(100.0)
        assert abs(result - expected) < 0.1
    
    def test_digamma_derivative(self):
        """Test digamma is derivative of log-gamma."""
        # ψ(x) = d/dx[ln(Γ(x))]
        # Use finite difference to approximate
        x = 5.0
        h = 1e-8
        approx_deriv = (log_gamma(x + h) - log_gamma(x - h)) / (2 * h)
        result = digamma(x)
        assert abs(result - approx_deriv) < 1e-6


class TestPolygamma:
    """Test polygamma function (derivatives of digamma)."""
    
    def test_polygamma_order_zero(self):
        """Test polygamma of order 0 equals digamma."""
        x = 5.0
        result = polygamma(0, x)
        expected = digamma(x)
        assert abs(result - expected) < 1e-10
    
    def test_polygamma_order_one(self):
        """Test polygamma of order 1 (trigamma)."""
        # ψ^(1)(x) should be positive for positive x
        result = polygamma(1, 2.0)
        assert result > 0
    
    def test_polygamma_array(self):
        """Test polygamma with array input."""
        x = np.array([1.0, 2.0, 3.0])
        result = polygamma(0, x)
        assert result.shape == (3,)


class TestBetaFunction:
    """Test beta function."""
    
    def test_beta_symmetry(self):
        """Test B(a, b) = B(b, a)."""
        a, b = 2.0, 3.0
        result1 = beta_func(a, b)
        result2 = beta_func(b, a)
        assert abs(result1 - result2) < 1e-10
    
    def test_beta_formula(self):
        """Test B(a, b) = Γ(a)Γ(b)/Γ(a+b)."""
        a, b = 2.0, 3.0
        result = beta_func(a, b)
        expected = gamma_func(a) * gamma_func(b) / gamma_func(a + b)
        assert abs(result - expected) < 1e-10
    
    def test_beta_integers(self):
        """Test beta with integer arguments."""
        # B(2, 3) = Γ(2)Γ(3)/Γ(5) = 1*2/24 = 1/12
        result = beta_func(2, 3)
        expected = 1.0 / 12.0
        assert abs(result - expected) < 1e-10


class TestLogBeta:
    """Test log-beta function."""
    
    def test_log_beta_consistency(self):
        """Test log_beta is consistent with log(beta(a, b))."""
        a, b = 2.0, 3.0
        result = log_beta(a, b)
        expected = math.log(beta_func(a, b))
        assert abs(result - expected) < 1e-10
    
    def test_log_beta_large_values(self):
        """Test log-beta for large values (more stable)."""
        result = log_beta(100, 100)
        # Should be negative (beta is small for large arguments)
        assert result < 0


class TestFactorial:
    """Test factorial functions."""
    
    def test_factorial_small(self):
        """Test factorial for small integers."""
        assert abs(factorial(0) - 1.0) < 1e-10
        assert abs(factorial(1) - 1.0) < 1e-10
        assert abs(factorial(2) - 2.0) < 1e-10
        assert abs(factorial(3) - 6.0) < 1e-10
        assert abs(factorial(4) - 24.0) < 1e-10
        assert abs(factorial(5) - 120.0) < 1e-10
    
    def test_factorial_consistency(self):
        """Test factorial is consistent with gamma."""
        n = 7
        result = factorial(n)
        expected = gamma_func(n + 1)
        assert abs(result - expected) < 1e-10
    
    def test_log_factorial_small(self):
        """Test log-factorial for small integers."""
        assert abs(log_factorial(0) - 0.0) < 1e-10  # ln(0!) = ln(1) = 0
        assert abs(log_factorial(1) - 0.0) < 1e-10  # ln(1!) = ln(1) = 0
        assert abs(log_factorial(5) - math.log(120)) < 1e-10
    
    def test_log_factorial_large(self):
        """Test log-factorial for large integers (more stable)."""
        result = log_factorial(100)
        # ln(100!) ≈ 363.7
        assert 360 < result < 370
    
    def test_log_factorial_consistency(self):
        """Test log_factorial is consistent with log(factorial(n))."""
        n = 10
        result = log_factorial(n)
        expected = math.log(math.factorial(n))
        assert abs(result - expected) < 1e-10


class TestSpecialValues:
    """Test special values and edge cases."""
    
    def test_gamma_half(self):
        """Test Γ(1/2) = √π."""
        result = gamma_func(0.5)
        expected = math.sqrt(math.pi)
        assert abs(result - expected) < 1e-10
    
    def test_gamma_three_halves(self):
        """Test Γ(3/2) = √π/2."""
        result = gamma_func(1.5)
        expected = math.sqrt(math.pi) / 2.0
        assert abs(result - expected) < 1e-10
    
    def test_gamma_reflection(self):
        """Test reflection formula: Γ(z)Γ(1-z) = π/sin(πz)."""
        z = 0.3
        result = gamma_func(z) * gamma_func(1 - z)
        expected = math.pi / math.sin(math.pi * z)
        assert abs(result - expected) < 1e-8


class TestNumericalStability:
    """Test numerical stability for extreme values."""
    
    def test_gamma_large_argument(self):
        """Test gamma doesn't overflow for moderately large arguments."""
        # Γ(20) should be computable
        result = gamma_func(20)
        assert result > 0
        assert not math.isinf(result)
    
    def test_log_gamma_very_large(self):
        """Test log-gamma for very large arguments."""
        result = log_gamma(1000)
        assert result > 0
        assert not math.isinf(result)
    
    def test_gamma_small_positive(self):
        """Test gamma for small positive values."""
        result = gamma_func(0.01)
        # Should be large but finite
        assert result > 10
        assert not math.isinf(result)


class TestArrayOperations:
    """Test vectorized operations with numpy arrays."""
    
    def test_gamma_array(self):
        """Test gamma with array input."""
        x = np.linspace(1, 5, 10)
        result = gamma_func(x)
        assert result.shape == x.shape
        assert np.all(result > 0)
    
    def test_log_gamma_array(self):
        """Test log-gamma with array."""
        x = np.linspace(1, 10, 20)
        result = log_gamma(x)
        assert result.shape == x.shape
    
    def test_incomplete_gamma_arrays(self):
        """Test incomplete gamma with arrays."""
        a = np.array([1.0, 2.0, 3.0])
        x = np.array([0.5, 1.0, 1.5])
        result = incomplete_gamma(a, x)
        assert result.shape == a.shape


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
