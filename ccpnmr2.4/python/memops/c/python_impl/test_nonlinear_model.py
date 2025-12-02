"""
Tests for nonlinear_model.py - Nonlinear model fitting with Levenberg-Marquardt
"""

import pytest
import numpy as np
from memops.c.python_impl.nonlinear_model import (
    nonlinear_fit, curve_fit_wrapper, exponential_fit, gaussian_fit,
    NonlinearModelError
)


class TestBasicFitting:
    """Test basic nonlinear fitting functionality."""
    
    def test_simple_exponential(self):
        """Test fitting simple exponential decay."""
        # Generate clean data
        x = np.linspace(0, 5, 50)
        A_true, k_true = 10.0, 0.5
        y_true = A_true * np.exp(-k_true * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y_true, exp_model, [8.0, 0.4])
        
        # Should recover true parameters closely
        assert abs(result['params'][0] - A_true) < 0.1
        assert abs(result['params'][1] - k_true) < 0.01
        assert result['success']
        assert result['chisq'] < 0.01  # Very small for noise-free data
    
    def test_exponential_with_noise(self):
        """Test fitting with noisy data."""
        np.random.seed(42)
        x = np.linspace(0, 5, 50)
        A_true, k_true = 10.0, 0.5
        y_true = A_true * np.exp(-k_true * x)
        y_noisy = y_true + np.random.normal(0, 0.5, len(x))
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y_noisy, exp_model, [8.0, 0.4], noise=0.5)
        
        # Should be close despite noise
        assert abs(result['params'][0] - A_true) < 1.0
        assert abs(result['params'][1] - k_true) < 0.1
        assert result['chisq'] < 5.0  # Reasonable for noisy data
    
    def test_gaussian_fitting(self):
        """Test fitting Gaussian peak."""
        x = np.linspace(-5, 5, 100)
        A, mu, sigma = 5.0, 0.0, 1.0
        y_true = A * np.exp(-(x - mu)**2 / (2 * sigma**2))
        
        def gauss(x, A, mu, sigma):
            return A * np.exp(-(x - mu)**2 / (2 * sigma**2))
        
        result = nonlinear_fit(x, y_true, gauss, [4.0, 0.2, 1.2])
        
        assert abs(result['params'][0] - A) < 0.1
        assert abs(result['params'][1] - mu) < 0.1
        assert abs(result['params'][2] - sigma) < 0.1
        assert result['success']


class TestWeightedFitting:
    """Test fitting with weights."""
    
    def test_uniform_weights(self):
        """Test with uniform weights (should match unweighted)."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result_unweighted = nonlinear_fit(x, y, exp_model, [8.0, 0.4])
        weights = np.ones(len(x))
        result_weighted = nonlinear_fit(x, y, exp_model, [8.0, 0.4], weights=weights)
        
        # Results should be very similar
        np.testing.assert_allclose(result_unweighted['params'], 
                                  result_weighted['params'], rtol=0.01)
    
    def test_varying_weights(self):
        """Test with varying weights."""
        np.random.seed(123)
        x = np.linspace(0, 5, 50)
        y_true = 10.0 * np.exp(-0.5 * x)
        
        # Add heteroscedastic noise (more noise at high x)
        noise = 0.1 + 0.5 * x / 5
        y_noisy = y_true + np.random.normal(0, 1, len(x)) * noise
        
        # Weights inversely proportional to noise variance
        weights = 1.0 / (noise**2)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y_noisy, exp_model, [8.0, 0.4], 
                              weights=weights, noise=1.0)
        
        # Weighted fit should give reasonable results
        assert abs(result['params'][0] - 10.0) < 2.0
        assert abs(result['params'][1] - 0.5) < 0.2


class TestParameterBounds:
    """Test fitting with parameter bounds."""
    
    def test_bounded_fitting(self):
        """Test fitting with parameter constraints."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        # Constrain parameters
        bounds = ([5, 0.1], [15, 1.0])  # A in [5,15], k in [0.1, 1.0]
        
        result = nonlinear_fit(x, y, exp_model, [8.0, 0.4], bounds=bounds)
        
        # Parameters should be within bounds
        assert 5 <= result['params'][0] <= 15
        assert 0.1 <= result['params'][1] <= 1.0
        assert result['success']
    
    def test_tight_bounds(self):
        """Test with very tight bounds."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        # Very tight bounds around true values
        bounds = ([9.5, 0.45], [10.5, 0.55])
        
        result = nonlinear_fit(x, y, exp_model, [10.0, 0.5], bounds=bounds)
        
        # Should converge to true values within bounds
        assert abs(result['params'][0] - 10.0) < 0.1
        assert abs(result['params'][1] - 0.5) < 0.01


class TestMultiParameter:
    """Test fitting models with many parameters."""
    
    def test_four_parameter_model(self):
        """Test 4-parameter logistic curve."""
        x = np.linspace(0, 10, 100)
        A, B, C, D = 0.5, 10.0, 5.0, 0.8
        y_true = A + (B - A) / (1 + (x / C)**D)
        
        def logistic(x, A, B, C, D):
            return A + (B - A) / (1 + (x / C)**D)
        
        result = nonlinear_fit(x, y_true, logistic, [0.4, 9.0, 4.5, 0.7])
        
        assert abs(result['params'][0] - A) < 0.1
        assert abs(result['params'][1] - B) < 0.5
        assert abs(result['params'][2] - C) < 0.2
        assert abs(result['params'][3] - D) < 0.1
    
    def test_polynomial_alternative(self):
        """Test nonlinear fit on polynomial (compare to polyfit)."""
        x = np.linspace(0, 5, 50)
        # y = ax^2 + bx + c (but fitted nonlinearly)
        a, b, c = 2.0, -3.0, 1.0
        y = a * x**2 + b * x + c
        
        def poly(x, a, b, c):
            return a * x**2 + b * x + c
        
        result = nonlinear_fit(x, y, poly, [1.5, -2.5, 0.8])
        
        # Should match polynomial coefficients
        assert abs(result['params'][0] - a) < 0.01
        assert abs(result['params'][1] - b) < 0.01
        assert abs(result['params'][2] - c) < 0.01


class TestCovarianceMatrix:
    """Test covariance matrix and parameter uncertainties."""
    
    def test_covariance_structure(self):
        """Test covariance matrix structure."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y, exp_model, [8.0, 0.4])
        
        # Covariance should be symmetric
        covar = result['covar']
        assert covar.shape == (2, 2)
        np.testing.assert_allclose(covar, covar.T, rtol=1e-10)
        
        # Diagonal elements should be positive
        assert np.all(np.diag(covar) >= 0)
    
    def test_parameter_uncertainties(self):
        """Test parameter standard deviations."""
        np.random.seed(42)
        x = np.linspace(0, 5, 50)
        y_true = 10.0 * np.exp(-0.5 * x)
        y_noisy = y_true + np.random.normal(0, 0.5, len(x))
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y_noisy, exp_model, [8.0, 0.4], noise=0.5)
        
        # Parameter uncertainties should be reasonable
        params_dev = result['params_dev']
        assert len(params_dev) == 2
        assert all(params_dev > 0)
        assert all(params_dev < 5.0)  # Not unreasonably large
    
    def test_tight_data_small_uncertainty(self):
        """Test that clean data gives small uncertainties."""
        x = np.linspace(0, 5, 100)  # More points
        y = 10.0 * np.exp(-0.5 * x)  # Clean data
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y, exp_model, [8.0, 0.4], noise=0.01)
        
        # Uncertainties should be very small
        assert all(result['params_dev'] < 0.1)


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_exponential_fit_helper(self):
        """Test exponential_fit convenience function."""
        x = np.linspace(0, 5, 50)
        A, k, C = 10.0, 0.5, 2.0
        y = A * np.exp(-k * x) + C
        
        result = exponential_fit(x, y, params_init=[8.0, 0.4, 1.5])
        
        assert abs(result['params'][0] - A) < 0.1
        assert abs(result['params'][1] - k) < 0.01
        assert abs(result['params'][2] - C) < 0.1
    
    def test_exponential_auto_init(self):
        """Test automatic parameter initialization."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x) + 2.0
        
        # No initial parameters - should estimate automatically
        result = exponential_fit(x, y)
        
        assert result['success']
        assert abs(result['params'][0] - 10.0) < 2.0
        assert abs(result['params'][1] - 0.5) < 0.2
    
    def test_gaussian_fit_helper(self):
        """Test gaussian_fit convenience function."""
        x = np.linspace(-5, 5, 100)
        A, mu, sigma, C = 5.0, 0.0, 1.0, 0.5
        y = A * np.exp(-(x - mu)**2 / (2 * sigma**2)) + C
        
        result = gaussian_fit(x, y, params_init=[4.0, 0.2, 1.2, 0.3])
        
        assert abs(result['params'][0] - A) < 0.2
        assert abs(result['params'][1] - mu) < 0.1
        assert abs(result['params'][2] - sigma) < 0.1
        assert abs(result['params'][3] - C) < 0.1


class TestCurveFitWrapper:
    """Test curve_fit wrapper interface."""
    
    def test_curve_fit_basic(self):
        """Test curve_fit_wrapper basic functionality."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = curve_fit_wrapper(x, y, exp_model, [8.0, 0.4])
        
        assert abs(result['params'][0] - 10.0) < 0.1
        assert abs(result['params'][1] - 0.5) < 0.01
        assert result['success']
    
    def test_curve_fit_vs_nonlinear_fit(self):
        """Compare curve_fit_wrapper with nonlinear_fit."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result1 = nonlinear_fit(x, y, exp_model, [8.0, 0.4])
        result2 = curve_fit_wrapper(x, y, exp_model, [8.0, 0.4])
        
        # Both should give similar results
        np.testing.assert_allclose(result1['params'], result2['params'], rtol=0.1)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_mismatched_data_length(self):
        """Test error when x and y have different lengths."""
        x = np.linspace(0, 5, 50)
        y = np.linspace(0, 5, 40)  # Wrong length
        
        def dummy(x, a): return a * x
        
        with pytest.raises(NonlinearModelError, match="same length"):
            nonlinear_fit(x, y, dummy, [1.0])
    
    def test_too_few_points(self):
        """Test error when fewer points than parameters."""
        x = np.array([1.0, 2.0])
        y = np.array([1.0, 2.0])
        
        def model(x, a, b, c): return a * x**2 + b * x + c
        
        with pytest.raises(NonlinearModelError, match="more data points"):
            nonlinear_fit(x, y, model, [1.0, 1.0, 1.0])
    
    def test_bad_initial_guess(self):
        """Test fitting with poor initial guess."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        # Very bad initial guess but should still converge
        result = nonlinear_fit(x, y, exp_model, [100.0, 5.0])
        
        # Should still find reasonable solution
        assert abs(result['params'][0] - 10.0) < 1.0
        assert abs(result['params'][1] - 0.5) < 0.1
    
    def test_wrong_weight_length(self):
        """Test error when weights have wrong length."""
        x = np.linspace(0, 5, 50)
        y = 10.0 * np.exp(-0.5 * x)
        weights = np.ones(40)  # Wrong length
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        with pytest.raises(NonlinearModelError, match="Weights must match"):
            nonlinear_fit(x, y, exp_model, [8.0, 0.4], weights=weights)


class TestRealWorldExamples:
    """Test with realistic scientific data scenarios."""
    
    def test_enzyme_kinetics(self):
        """Test Michaelis-Menten enzyme kinetics fitting."""
        # v = Vmax * [S] / (Km + [S])
        S = np.linspace(0.1, 20, 50)  # Substrate concentration
        Vmax_true, Km_true = 10.0, 2.0
        v = Vmax_true * S / (Km_true + S)
        
        def michaelis_menten(S, Vmax, Km):
            return Vmax * S / (Km + S)
        
        result = nonlinear_fit(S, v, michaelis_menten, [8.0, 1.5])
        
        assert abs(result['params'][0] - Vmax_true) < 0.5
        assert abs(result['params'][1] - Km_true) < 0.2
    
    def test_binding_isotherm(self):
        """Test binding isotherm (similar to NMR titration)."""
        # Fraction bound: f = [L] / (Kd + [L])
        L = np.logspace(-2, 2, 50)  # Ligand concentration
        Kd_true = 1.0
        f = L / (Kd_true + L)
        
        def binding(L, Kd):
            return L / (Kd + L)
        
        result = nonlinear_fit(L, f, binding, [0.5])
        
        assert abs(result['params'][0] - Kd_true) < 0.1
    
    def test_multi_exponential_decay(self):
        """Test biexponential decay (common in NMR)."""
        t = np.linspace(0, 5, 100)
        A1, k1, A2, k2 = 5.0, 2.0, 3.0, 0.5
        y = A1 * np.exp(-k1 * t) + A2 * np.exp(-k2 * t)
        
        def biexp(t, A1, k1, A2, k2):
            return A1 * np.exp(-k1 * t) + A2 * np.exp(-k2 * t)
        
        result = nonlinear_fit(t, y, biexp, [4.0, 1.5, 2.5, 0.4])
        
        # Parameters may be correlated, but fit should be good
        assert np.max(np.abs(result['y_fit'] - y)) < 0.1
        assert result['chisq'] < 0.01


class TestNumericalStability:
    """Test numerical stability with difficult cases."""
    
    def test_large_parameter_values(self):
        """Test with large parameter values."""
        x = np.linspace(0, 5, 50)
        y = 1000.0 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y, exp_model, [900.0, 0.4])
        
        assert abs(result['params'][0] - 1000.0) < 50
        assert abs(result['params'][1] - 0.5) < 0.05
    
    def test_small_parameter_values(self):
        """Test with very small parameter values."""
        x = np.linspace(0, 5, 50)
        y = 0.001 * np.exp(-0.5 * x)
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y, exp_model, [0.0008, 0.4])
        
        assert abs(result['params'][0] - 0.001) < 0.0002
        assert abs(result['params'][1] - 0.5) < 0.05
    
    def test_steep_function(self):
        """Test with steep function (large gradients)."""
        x = np.linspace(0, 2, 50)
        y = 10.0 * np.exp(-10 * x)  # Very steep decay
        
        def exp_model(x, A, k):
            return A * np.exp(-k * x)
        
        result = nonlinear_fit(x, y, exp_model, [8.0, 8.0])
        
        assert abs(result['params'][0] - 10.0) < 1.0
        assert abs(result['params'][1] - 10.0) < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
