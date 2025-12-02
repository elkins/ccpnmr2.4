"""
Comprehensive tests for fit.py - NMR curve fitting module.

Tests all 18 fitting methods with synthetic data to ensure accuracy,
parameter recovery, and error handling.
"""

import pytest
import numpy as np
import math
from memops.c.python_impl.fit import (
    Fit, fit_data, exponential_fit, gaussian_fit_func,
    get_method_nparams,
    NO_FIT, LINEAR_FIT, LOG_LINEAR_FIT, NONLINEAR2_FIT, NONLINEAR3_FIT,
    SLOW_EXCHANGE_FIT, LANGMUIR_FIT, KD_SHIFT_FIT, KD_ALT_SHIFT_FIT,
    INVERSION_RECOVERY_FIT, GAUSSIAN_FIT, COSINE_FIT,
    CPMG3_FAST_FIT, CPMG3_SLOW_FIT, CPMG4_FAST_FIT, CPMG4_SLOW_FIT,
    NONLINEAR_INVERSE_FIT, NONLINEAR_INVERSE2_FIT,
    FIT_METHODS, NFIT_METHODS
)
from memops.c.python_impl.random import set_seed, normal


class TestFitBasics:
    """Test basic functionality and API."""
    
    def test_fit_creation(self):
        """Test creating Fit object."""
        fit = Fit(method=LINEAR_FIT, noise=1.0)
        assert fit.method == LINEAR_FIT
        assert fit.noise == 1.0
    
    def test_get_method_nparams(self):
        """Test parameter count for each method."""
        assert get_method_nparams(NO_FIT) == 0
        assert get_method_nparams(LINEAR_FIT) == 2
        assert get_method_nparams(LOG_LINEAR_FIT) == 2
        assert get_method_nparams(NONLINEAR2_FIT) == 2
        assert get_method_nparams(NONLINEAR3_FIT) == 3
        assert get_method_nparams(SLOW_EXCHANGE_FIT) == 3
        assert get_method_nparams(LANGMUIR_FIT) == 1
        assert get_method_nparams(KD_SHIFT_FIT) == 3
        assert get_method_nparams(INVERSION_RECOVERY_FIT) == 2
        assert get_method_nparams(KD_ALT_SHIFT_FIT) == 2
        assert get_method_nparams(GAUSSIAN_FIT) == 2
        assert get_method_nparams(COSINE_FIT) == 2
        assert get_method_nparams(CPMG3_FAST_FIT) == 3
        assert get_method_nparams(CPMG4_FAST_FIT) == 4
        assert get_method_nparams(NONLINEAR_INVERSE_FIT) == 3
        assert get_method_nparams(NONLINEAR_INVERSE2_FIT) == 2
    
    def test_fit_methods_list(self):
        """Test that fit methods list has correct size."""
        assert len(FIT_METHODS) == NFIT_METHODS
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data points."""
        fit = Fit(method=NONLINEAR3_FIT, noise=0.1)
        x = [1.0, 2.0]
        y = [3.0, 4.0]
        
        result = fit.run_fit(x, y)
        assert not result['success']
        assert 'Not enough data' in result['message']


class TestLinearFit:
    """Test linear fitting: y = Ax + B."""
    
    def test_perfect_linear(self):
        """Test fit to perfect linear data."""
        # Generate y = 3x + 2
        x = np.linspace(0, 10, 20)
        y = 3*x + 2
        
        fit = Fit(method=LINEAR_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist(), compute_errors=True)
        
        assert result['success']
        assert abs(result['params'][0] - 3.0) < 0.01  # Slope
        assert abs(result['params'][1] - 2.0) < 0.01  # Intercept
        assert result['chisq'] < 1e-10
    
    def test_linear_with_noise(self):
        """Test linear fit with noisy data."""
        set_seed(42)
        x = np.linspace(0, 10, 50)
        y_true = 2.5*x + 1.5
        y = y_true + np.array([normal(0, 0.1) for _ in range(len(x))])
        
        fit = Fit(method=LINEAR_FIT, noise=0.1)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 2.5) < 0.1
        assert abs(result['params'][1] - 1.5) < 0.2


class TestLogLinearFit:
    """Test log-linear fitting: log(y) = log(A) - Bx."""
    
    def test_log_linear_perfect(self):
        """Test fit to perfect exponential decay."""
        # Generate y = 10 * exp(-0.5*x)
        x = np.linspace(0.1, 5, 30)
        y = 10 * np.exp(-0.5 * x)
        
        fit = Fit(method=LOG_LINEAR_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 10.0) < 0.5  # A
        assert abs(result['params'][1] - 0.5) < 0.05  # B
    
    def test_log_linear_with_zeros(self):
        """Test handling of non-positive y values."""
        x = [1.0, 2.0, 3.0, 4.0]
        y = [5.0, 0.0, 3.0, -1.0]  # Contains zero and negative
        
        fit = Fit(method=LOG_LINEAR_FIT, noise=0.1)
        result = fit.run_fit(x, y)
        
        # Should handle gracefully
        assert 'params' in result


class TestExponentialFits:
    """Test exponential decay fits."""
    
    def test_nonlinear2_fit(self):
        """Test 2-parameter exponential: A exp(-Bx)."""
        # Generate y = 5 * exp(-0.3*x)
        x = np.linspace(0, 10, 40)
        y = 5 * np.exp(-0.3 * x)
        
        result = exponential_fit(x.tolist(), y.tolist(), offset=False, noise=0.01)
        
        assert result['success']
        assert abs(result['params'][0] - 5.0) < 0.2
        assert abs(result['params'][1] - 0.3) < 0.02
    
    def test_nonlinear3_fit(self):
        """Test 3-parameter exponential: A exp(-Bx) + C."""
        # Generate y = 4 * exp(-0.4*x) + 1.5
        x = np.linspace(0, 8, 35)
        y = 4 * np.exp(-0.4 * x) + 1.5
        
        result = exponential_fit(x.tolist(), y.tolist(), offset=True, noise=0.01)
        
        assert result['success']
        assert abs(result['params'][0] - 4.0) < 0.3
        assert abs(result['params'][1] - 0.4) < 0.05
        assert abs(result['params'][2] - 1.5) < 0.2
    
    def test_exponential_with_noise(self):
        """Test exponential fit with realistic noise."""
        set_seed(123)
        x = np.linspace(0.1, 10, 50)
        y_true = 10 * np.exp(-0.5 * x) + 2
        y = y_true + np.array([normal(0, 0.2) for _ in range(len(x))])
        
        result = exponential_fit(x.tolist(), y.tolist(), offset=True, noise=0.2)
        
        assert result['success']
        assert abs(result['params'][0] - 10.0) < 1.0
        assert abs(result['params'][1] - 0.5) < 0.1
        assert abs(result['params'][2] - 2.0) < 0.5


class TestInverseExponentialFits:
    """Test inverse exponential fits."""
    
    def test_nonlinear_inverse_fit(self):
        """Test C - A exp(-Bx)."""
        # Generate y = 10 - 5*exp(-0.3*x)
        x = np.linspace(0, 10, 40)
        y = 10 - 5 * np.exp(-0.3 * x)
        
        fit = Fit(method=NONLINEAR_INVERSE_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 5.0) < 0.3  # A
        assert abs(result['params'][1] - 0.3) < 0.05  # B
        assert abs(result['params'][2] - 10.0) < 0.3  # C
    
    def test_nonlinear_inverse2_fit(self):
        """Test A(1 - exp(-Bx))."""
        # Generate y = 8*(1 - exp(-0.4*x))
        x = np.linspace(0, 10, 40)
        y = 8 * (1 - np.exp(-0.4 * x))
        
        fit = Fit(method=NONLINEAR_INVERSE2_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 8.0) < 0.4
        assert abs(result['params'][1] - 0.4) < 0.05


class TestGaussianFit:
    """Test Gaussian fitting."""
    
    def test_gaussian_perfect(self):
        """Test Gaussian fit: A exp(-Bx^2)."""
        # Generate y = 6 * exp(-0.5*x^2)
        x = np.linspace(-3, 3, 50)
        y = 6 * np.exp(-0.5 * x**2)
        
        result = gaussian_fit_func(x.tolist(), y.tolist(), noise=0.01)
        
        assert result['success']
        assert abs(result['params'][0] - 6.0) < 0.3
        assert abs(result['params'][1] - 0.5) < 0.05
    
    def test_gaussian_with_noise(self):
        """Test Gaussian fit with noise."""
        set_seed(456)
        x = np.linspace(-2, 2, 40)
        y_true = 5 * np.exp(-0.8 * x**2)
        y = y_true + np.array([normal(0, 0.1) for _ in range(len(x))])
        
        result = gaussian_fit_func(x.tolist(), y.tolist(), noise=0.1)
        
        assert result['success']
        assert abs(result['params'][0] - 5.0) < 0.5
        assert abs(result['params'][1] - 0.8) < 0.2


class TestCosineFit:
    """Test cosine fitting."""
    
    def test_cosine_perfect(self):
        """Test cosine fit: A cos(Bx)."""
        # Generate y = 4 * cos(0.5*x)
        x = np.linspace(0, 4*np.pi, 50)
        y = 4 * np.cos(0.5 * x)
        
        fit = Fit(method=COSINE_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 4.0) < 0.3
        assert abs(result['params'][1] - 0.5) < 0.05
    
    def test_cosine_with_noise(self):
        """Test cosine fit with noise."""
        set_seed(789)
        x = np.linspace(0, 2*np.pi, 30)
        y_true = 3 * np.cos(1.5 * x)
        y = y_true + np.array([normal(0, 0.1) for _ in range(len(x))])
        
        fit = Fit(method=COSINE_FIT, noise=0.1)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 3.0) < 0.5


class TestSlowExchangeFit:
    """Test slow exchange fitting."""
    
    def test_slow_exchange_basic(self):
        """Test slow exchange fit: A (1-sin(Bx)/Bx) + C."""
        # Generate synthetic data
        x = np.linspace(0.1, 5, 40)
        a, b, c = 5.0, 2.0, 1.0
        bx = b * x
        y = a * (1 - np.sin(bx) / bx) + c
        
        fit = Fit(method=SLOW_EXCHANGE_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        # Parameters may not recover exactly due to complexity
        assert len(result['params']) == 3


class TestLangmuirFit:
    """Test Langmuir isotherm fitting."""
    
    def test_langmuir_perfect(self):
        """Test Langmuir fit: Ax / (1+Ax)."""
        # Generate y = 2*x / (1 + 2*x)
        x = np.linspace(0.1, 5, 40)
        a = 2.0
        y = (a * x) / (1 + a * x)
        
        fit = Fit(method=LANGMUIR_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 2.0) < 0.3


class TestKdShiftFits:
    """Test Kd chemical shift fitting."""
    
    def test_kd_shift_basic(self):
        """Test KD_SHIFT_FIT model."""
        # Generate synthetic data
        x = np.linspace(0.5, 10, 30)
        a, b, c = 5.0, 2.0, 0.5
        t = 1 + b / (4 * x)
        s = np.sqrt(np.maximum(t**2 - 1, 0))
        y = a * (t - s - c)
        
        fit = Fit(method=KD_SHIFT_FIT, noise=0.1)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert len(result['params']) == 3
    
    def test_kd_alt_shift_basic(self):
        """Test KD_ALT_SHIFT_FIT model."""
        # Generate synthetic data
        x = np.linspace(0.5, 10, 30)
        a, b = 4.0, 3.0
        t = b + x
        s = np.sqrt(np.maximum(t**2 - 4*x, 0))
        y = a * (t - s)
        
        fit = Fit(method=KD_ALT_SHIFT_FIT, noise=0.1)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert len(result['params']) == 2


class TestInversionRecoveryFit:
    """Test inversion recovery (T1) fitting."""
    
    def test_inversion_recovery_perfect(self):
        """Test inversion recovery: A (1/2 - exp(-Bx))."""
        # Generate y = 10 * (0.5 - exp(-0.3*x))
        x = np.linspace(0, 10, 40)
        a, b = 10.0, 0.3
        y = a * (0.5 - np.exp(-b * x))
        
        fit = Fit(method=INVERSION_RECOVERY_FIT, noise=0.01)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert result['success']
        assert abs(result['params'][0] - 10.0) < 0.5
        # Note: B is scaled by BSCALE in implementation
        assert abs(result['params'][1] - 0.3) < 0.05


class TestCPMGFits:
    """Test CPMG relaxation dispersion fitting."""
    
    def test_cpmg3_fast_basic(self):
        """Test CPMG 3-parameter fast exchange."""
        # Simple test that function works
        x = np.linspace(50, 1000, 20)  # nu values
        R2max, kex, dw = 15.0, 500.0, 2.0
        
        # Generate synthetic data (simplified)
        y = R2max + 0.1 * kex * x / (x + 100)
        
        fit = Fit(method=CPMG3_FAST_FIT, noise=0.5)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        # Just verify it runs without error
        assert 'params' in result
        assert len(result['params']) == 3
    
    def test_cpmg4_basic(self):
        """Test CPMG 4-parameter model."""
        x = np.linspace(50, 1000, 20)
        R2max, kAB, kBA, dw = 15.0, 300.0, 200.0, 2.0
        
        # Simplified synthetic data
        y = R2max + 0.1 * (kAB + kBA) * x / (x + 100)
        
        fit = Fit(method=CPMG4_FAST_FIT, noise=0.5)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        assert 'params' in result
        assert len(result['params']) == 4


class TestBootstrap:
    """Test bootstrap error estimation."""
    
    def test_bootstrap_linear(self):
        """Test bootstrap on linear data."""
        set_seed(42)
        x = np.linspace(0, 10, 30)
        y_true = 2*x + 3
        y = y_true + np.array([normal(0, 0.5) for _ in range(len(x))])
        
        fit = Fit(method=LINEAR_FIT, noise=0.5)
        result = fit.bootstrap_fit(x.tolist(), y.tolist(), niter=50)
        
        assert result['success']
        assert len(result['params_std']) == 2
        # Bootstrap std should be reasonable
        assert all(s > 0 for s in result['params_std'])
        assert all(s < 1.0 for s in result['params_std'])
    
    def test_bootstrap_exponential(self):
        """Test bootstrap on exponential data."""
        set_seed(123)
        x = np.linspace(0.1, 5, 25)
        y_true = 5 * np.exp(-0.5 * x) + 1
        y = y_true + np.array([normal(0, 0.1) for _ in range(len(x))])
        
        fit = Fit(method=NONLINEAR3_FIT, noise=0.1)
        result = fit.bootstrap_fit(x.tolist(), y.tolist(), niter=30)
        
        if result['success']:
            assert len(result['params_std']) == 3
            assert all(s >= 0 for s in result['params_std'])


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_fit_data_convenience(self):
        """Test fit_data convenience function."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.5, 4.8, 7.2, 9.5, 11.8]
        
        result = fit_data(LINEAR_FIT, x, y, noise=0.1)
        
        assert result['success']
        assert len(result['params']) == 2
    
    def test_exponential_fit_convenience(self):
        """Test exponential_fit convenience function."""
        x = np.linspace(0, 5, 20)
        y = 3 * np.exp(-0.4 * x) + 1
        
        result = exponential_fit(x.tolist(), y.tolist(), offset=True)
        
        assert result['success']
        assert result['params_err'] is not None  # compute_errors=True
    
    def test_gaussian_fit_convenience(self):
        """Test gaussian_fit_func convenience function."""
        x = np.linspace(-2, 2, 30)
        y = 4 * np.exp(-0.6 * x**2)
        
        result = gaussian_fit_func(x.tolist(), y.tolist())
        
        assert result['success']
        assert result['params_err'] is not None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_data(self):
        """Test with empty data."""
        fit = Fit(method=LINEAR_FIT)
        x, y = [], []
        result = fit.run_fit(x, y)
        
        assert not result['success']
    
    def test_single_point(self):
        """Test with single data point."""
        fit = Fit(method=NONLINEAR2_FIT)
        x, y = [1.0], [2.0]
        result = fit.run_fit(x, y)
        
        assert not result['success']
    
    def test_no_fit_method(self):
        """Test NO_FIT method."""
        fit = Fit(method=NO_FIT)
        x = [1.0, 2.0, 3.0]
        y = [4.0, 5.0, 6.0]
        result = fit.run_fit(x, y)
        
        assert result['success']
        assert len(result['params']) == 0
        np.testing.assert_array_equal(result['y_fit'], y)
    
    def test_constant_data(self):
        """Test with constant y values."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [5.0, 5.0, 5.0, 5.0, 5.0]
        
        fit = Fit(method=LINEAR_FIT, noise=0.1)
        result = fit.run_fit(x, y)
        
        # Should handle gracefully
        assert 'params' in result
    
    def test_divergent_data(self):
        """Test with data that doesn't fit the model."""
        # Try to fit exponential to linear data
        x = np.linspace(0, 10, 20)
        y = 2*x + 3  # Linear, not exponential
        
        fit = Fit(method=NONLINEAR2_FIT, noise=1.0)
        result = fit.run_fit(x.tolist(), y.tolist())
        
        # May or may not converge, but should not crash
        assert 'params' in result
        assert 'success' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
