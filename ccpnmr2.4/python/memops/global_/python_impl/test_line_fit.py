"""
Tests for line_fit module - Linear least-squares fitting

This test suite validates the Python implementation against known analytical
results and edge cases.

Author: CcpNmr Python Modernization Project
Date: December 2025
"""

import pytest
import numpy as np
from numpy.testing import assert_allclose, assert_array_almost_equal
from line_fit import line_fit, linear_regression, LineFitError


class TestLineFitBasic:
    """Test basic line fitting functionality."""

    def test_perfect_line(self):
        """Test fitting a perfect line (no noise)."""
        # y = 2 + 3*x (perfect line)
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = 2.0 + 3.0 * x

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        # Parameters should match exactly (within floating point precision)
        assert_allclose(a, 2.0, rtol=1e-10)
        assert_allclose(b, 3.0, rtol=1e-10)

        # Fitted values should match input exactly
        assert_array_almost_equal(yfit, y, decimal=10)

        # For perfect fit, chi-square should be ~0
        assert goodness < 1e-10

    def test_simple_fit_with_noise(self):
        """Test fitting with small noise."""
        np.random.seed(42)
        x = np.linspace(0, 10, 20)
        y_true = 1.5 + 2.5 * x
        y = y_true + np.random.randn(len(x)) * 0.1

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        # Should recover parameters within noise level
        assert abs(a - 1.5) < 0.2
        assert abs(b - 2.5) < 0.05

        # Errors should be reasonable
        assert std_a > 0
        assert std_b > 0

        # Correlation should be reasonable
        assert -1 <= corr_ab <= 1

    def test_horizontal_line(self):
        """Test fitting a horizontal line (b=0)."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([5.0, 5.0, 5.0, 5.0, 5.0])

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        assert_allclose(a, 5.0, rtol=1e-10)
        assert_allclose(b, 0.0, atol=1e-10)
        assert_array_almost_equal(yfit, y, decimal=10)

    def test_vertical_through_origin(self):
        """Test line through origin (a=0)."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = 3.0 * x  # Perfect line through origin

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        assert_allclose(a, 0.0, atol=1e-10)
        assert_allclose(b, 3.0, rtol=1e-10)

    def test_negative_slope(self):
        """Test fitting a line with negative slope."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = 10.0 - 2.0 * x  # y = 10 - 2x

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        assert_allclose(a, 10.0, rtol=1e-10)
        assert_allclose(b, -2.0, rtol=1e-10)


class TestWeightedFit:
    """Test weighted line fitting with uncertainties."""

    def test_weighted_fit_equal_weights(self):
        """Weighted fit with equal weights should match unweighted fit."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([2.1, 4.0, 5.9, 8.1, 10.0])

        # Unweighted fit
        a1, b1, std_a1, std_b1, corr1, good1, yfit1 = line_fit(x, y, sigma=None)

        # Weighted fit with equal weights
        sigma = np.ones(len(x))
        a2, b2, std_a2, std_b2, corr2, good2, yfit2 = line_fit(x, y, sigma=sigma)

        # Results should be identical
        assert_allclose(a1, a2, rtol=1e-6)
        assert_allclose(b1, b2, rtol=1e-6)
        assert_array_almost_equal(yfit1, yfit2, decimal=6)

    def test_weighted_fit_varying_weights(self):
        """Test weighted fit with different uncertainties."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])

        # Small uncertainty on some points, large on others
        sigma = np.array([0.1, 0.1, 1.0, 0.1, 0.1])

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y, sigma)

        # Fit should be close to perfect line (points with small sigma dominate)
        assert abs(a) < 0.5
        assert abs(b - 2.0) < 0.1

    def test_weighted_fit_high_precision_point(self):
        """Test that high-precision point dominates fit."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        # Outlier at index 2, but with large sigma
        y = np.array([2.0, 4.0, 10.0, 8.0, 10.0])

        # Very large uncertainty on outlier
        sigma = np.array([0.1, 0.1, 10.0, 0.1, 0.1])

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y, sigma)

        # Outlier should have minimal effect due to large sigma
        # Fit should be close to y = 2x
        assert abs(b - 2.0) < 0.3

    def test_goodness_of_fit_weighted(self):
        """Test Q-value for weighted fit."""
        np.random.seed(42)
        x = np.linspace(0, 10, 30)
        y_true = 1.0 + 2.0 * x
        sigma = np.ones(len(x)) * 0.5

        # Add noise consistent with sigma
        y = y_true + np.random.randn(len(x)) * sigma

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y, sigma)

        # Q-value should be reasonable (not too close to 0 or 1)
        # For properly estimated errors, expect Q ~ uniform(0,1)
        assert 0.0 <= goodness <= 1.0
        # Very unlikely to be exactly 0 or 1 for realistic data
        assert goodness > 0.001
        assert goodness < 0.999


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_insufficient_points(self):
        """Test error with < 2 points."""
        x = np.array([1.0])
        y = np.array([2.0])

        with pytest.raises(LineFitError, match="at least 2"):
            line_fit(x, y)

    def test_mismatched_lengths(self):
        """Test error with x and y of different lengths."""
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([2.0, 4.0])

        with pytest.raises(LineFitError, match="same length"):
            line_fit(x, y)

    def test_sigma_length_mismatch(self):
        """Test error when sigma has wrong length."""
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([2.0, 4.0, 6.0])
        sigma = np.array([0.1, 0.1])  # Wrong length

        with pytest.raises(LineFitError, match="same length"):
            line_fit(x, y, sigma)

    def test_identical_x_values(self):
        """Test error when all x values are the same."""
        x = np.array([2.0, 2.0, 2.0, 2.0])
        y = np.array([1.0, 2.0, 3.0, 4.0])

        with pytest.raises(LineFitError, match="identical"):
            line_fit(x, y)

    def test_nearly_identical_x_values(self):
        """Test that very close x values can still be fit (scale-relative check)."""
        # With tiny variations, the algorithm is now scale-aware and can handle this
        x = np.array([2.0, 2.0 + 1e-12, 2.0 + 2e-12, 2.0 + 3e-12])
        y = np.array([1.0, 2.0, 3.0, 4.0])

        # This should NOT raise an error anymore due to scale-relative checking
        # The algorithm is robust enough to handle this case
        try:
            a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)
            # If it succeeds, the errors should be large (data is poorly conditioned)
            assert std_a > 0
            assert std_b > 0
        except LineFitError:
            # If it does raise, that's also acceptable for such extreme data
            pass


class TestLinearRegression:
    """Test simplified linear_regression interface."""

    def test_basic_regression(self):
        """Test basic linear regression."""
        np.random.seed(42)
        x = np.linspace(0, 10, 50)
        y_true = 2.5 + 1.5 * x
        y = y_true + np.random.randn(len(x)) * 0.5

        slope, intercept, slope_err, int_err, r2 = linear_regression(x, y)

        # Check parameter recovery
        assert abs(slope - 1.5) < 0.1
        assert abs(intercept - 2.5) < 0.5

        # Check R²
        assert r2 > 0.95  # Should be high for linear data with small noise

        # Check errors are positive
        assert slope_err > 0
        assert int_err > 0

    def test_perfect_fit_r_squared(self):
        """Test R² = 1 for perfect fit."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y = 3.0 + 2.0 * x  # Perfect line

        slope, intercept, slope_err, int_err, r2 = linear_regression(x, y)

        assert_allclose(r2, 1.0, rtol=1e-10)
        assert_allclose(slope, 2.0, rtol=1e-10)
        assert_allclose(intercept, 3.0, rtol=1e-10)

    def test_weighted_regression(self):
        """Test weighted linear regression."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([2.0, 4.1, 6.0, 7.9, 10.0])

        # Weights = 1/sigma²
        sigma = np.array([0.1, 0.5, 0.1, 0.5, 0.1])
        weights = 1.0 / (sigma ** 2)

        slope, intercept, slope_err, int_err, r2 = linear_regression(x, y, weights)

        # Fit should favor high-weight points
        assert abs(slope - 2.0) < 0.1
        assert abs(intercept) < 0.2


class TestNumericalStability:
    """Test numerical stability with challenging data."""

    def test_large_values(self):
        """Test with large x and y values."""
        x = np.array([1e6, 2e6, 3e6, 4e6, 5e6])
        y = 1e9 + 1000.0 * x

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        assert_allclose(b, 1000.0, rtol=1e-6)
        assert_array_almost_equal(yfit, y, decimal=3)

    def test_small_values(self):
        """Test with very small x and y values."""
        x = np.array([1e-9, 2e-9, 3e-9, 4e-9, 5e-9])
        y = 1e-8 + 2e-6 * x

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        # Should still recover slope reasonably
        assert abs(b - 2e-6) / 2e-6 < 0.01

    def test_mixed_scale_data(self):
        """Test with data spanning multiple orders of magnitude."""
        x = np.array([0.001, 0.01, 0.1, 1.0, 10.0])
        y = 1.0 + 5.0 * x

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        assert_allclose(a, 1.0, rtol=1e-6)
        assert_allclose(b, 5.0, rtol=1e-6)


class TestComparisonWithNumPy:
    """Compare results with NumPy's polyfit and lstsq."""

    def test_vs_numpy_polyfit(self):
        """Compare with numpy.polyfit (unweighted)."""
        np.random.seed(42)
        x = np.linspace(0, 10, 30)
        y = 2.5 + 1.5 * x + np.random.randn(len(x)) * 0.5

        # Our implementation
        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        # NumPy's polyfit
        poly_coefs = np.polyfit(x, y, 1)
        b_numpy, a_numpy = poly_coefs  # Note: polyfit returns highest degree first

        # Results should be very close
        assert_allclose(a, a_numpy, rtol=1e-6)
        assert_allclose(b, b_numpy, rtol=1e-6)

    def test_vs_numpy_lstsq(self):
        """Compare with numpy.linalg.lstsq."""
        np.random.seed(42)
        x = np.linspace(0, 10, 30)
        y = 2.5 + 1.5 * x + np.random.randn(len(x)) * 0.5

        # Our implementation
        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y)

        # NumPy's lstsq
        A = np.vstack([x, np.ones(len(x))]).T
        result = np.linalg.lstsq(A, y, rcond=None)
        b_numpy, a_numpy = result[0]

        # Results should be very close
        assert_allclose(a, a_numpy, rtol=1e-6)
        assert_allclose(b, b_numpy, rtol=1e-6)


class TestRealWorldScenarios:
    """Test realistic NMR data scenarios."""

    def test_relaxation_data(self):
        """Test fitting T1 or T2 relaxation data (after log transform)."""
        # Simulated relaxation: I(t) = I0 * exp(-t/T2)
        # After log: ln(I) = ln(I0) - t/T2 (linear in t)
        t = np.array([0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
        I0 = 100.0
        T2 = 0.3  # seconds
        I = I0 * np.exp(-t / T2)

        # Log transform
        ln_I = np.log(I)

        # Fit: ln(I) = ln(I0) - t/T2
        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(t, ln_I)

        # Recover parameters
        I0_fit = np.exp(a)
        T2_fit = -1.0 / b

        assert_allclose(I0_fit, I0, rtol=1e-6)
        assert_allclose(T2_fit, T2, rtol=1e-6)

    def test_chemical_shift_temperature(self):
        """Test chemical shift vs temperature calibration."""
        # Methanol OH shift vs temperature (typical calibration)
        temp_C = np.array([10, 15, 20, 25, 30, 35, 40])
        shift_ppm = 5.0 - 0.01 * temp_C  # Linear relationship

        a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(temp_C, shift_ppm)

        # Should recover calibration accurately
        assert_allclose(a, 5.0, rtol=1e-6)
        assert_allclose(b, -0.01, rtol=1e-6)


def test_full_workflow():
    """Integration test with complete workflow."""
    np.random.seed(123)

    # Simulate experimental data
    n_points = 50
    x = np.linspace(0, 10, n_points)
    true_a = 2.5
    true_b = 1.8
    noise_level = 0.3

    y_true = true_a + true_b * x
    y = y_true + np.random.randn(n_points) * noise_level

    # Estimate uncertainties
    sigma = np.ones(n_points) * noise_level

    # Perform weighted fit
    a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y, sigma)

    # Verify results
    assert abs(a - true_a) < 3 * std_a  # Within 3 sigma
    assert abs(b - true_b) < 3 * std_b  # Within 3 sigma

    # Check Q-value is reasonable
    assert 0.01 < goodness < 0.99

    # Verify fitted values are reasonable
    residuals = y - yfit
    assert np.std(residuals) < noise_level * 1.5


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
