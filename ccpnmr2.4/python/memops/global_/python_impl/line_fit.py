"""
======================COPYRIGHT/LICENSE START==========================

line_fit.py: Part of the CcpNmr Analysis program (Python implementation)

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)
Copyright (C) 2025 CcpNmr Python Modernization Project

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

For further information, please contact:

- CCPN website (http://www.ccpn.ac.uk/)
- email: ccpn@bioc.cam.ac.uk

=======================================================================

Linear Least-Squares Fitting
============================

Pure Python implementation of linear regression with optional weighted fitting.

This module provides linear least-squares fitting functionality equivalent to
the original C implementation in line_fit.c. It supports both unweighted and
weighted linear regression with comprehensive error estimates.

Key Features:
- Weighted and unweighted linear regression
- Standard error calculations for slope and intercept
- Correlation coefficient between parameters
- Goodness-of-fit statistics (chi-square)
- NumPy vectorization for performance

Mathematical Background:
-----------------------
Fits data to the model: y = a + b*x

Where:
- a: intercept (y-intercept when x=0)
- b: slope (rate of change)

For weighted fits, each data point can have an associated uncertainty (sigma).
The fit minimizes the weighted chi-square:

    χ² = Σ ((y_i - (a + b*x_i)) / σ_i)²

For unweighted fits, all points have equal weight (σ_i = 1).

Error Estimates:
--------------
- std_a: Standard deviation of intercept
- std_b: Standard deviation of slope
- corr_ab: Correlation coefficient between a and b
- goodness: Chi-square or Q-value (probability of fit quality)

Author: CcpNmr Python Modernization Project
Date: December 2025
"""

import numpy as np
from typing import Tuple, Optional
from scipy.special import gammaincc  # Complement of incomplete gamma function


class LineFitError(Exception):
    """Exception raised for errors in line fitting."""
    pass


def line_fit(
    x: np.ndarray,
    y: np.ndarray,
    sigma: Optional[np.ndarray] = None
) -> Tuple[float, float, float, float, float, float, np.ndarray]:
    """
    Perform weighted or unweighted linear least-squares fit: y = a + b*x.

    This function fits a straight line to the provided data points, optionally
    with weights (inverse variance) for each point. It returns the fitted
    parameters (intercept and slope) along with their standard errors, the
    correlation between them, the goodness-of-fit statistic, and the fitted y values.

    Parameters
    ----------
    x : np.ndarray
        Independent variable (1D array of length n)
    y : np.ndarray
        Dependent variable (1D array of length n)
    sigma : np.ndarray, optional
        Standard deviations (uncertainties) for each y value (1D array of length n)
        If None, unweighted fit is performed (all points have equal weight)

    Returns
    -------
    a : float
        Intercept of the fitted line (y-intercept)
    b : float
        Slope of the fitted line
    std_a : float
        Standard deviation (uncertainty) of the intercept
    std_b : float
        Standard deviation (uncertainty) of the slope
    corr_ab : float
        Correlation coefficient between intercept and slope (-1 to 1)
    goodness : float
        Goodness-of-fit statistic:
        - If sigma is provided: Q-value from incomplete gamma function (0 to 1)
          Values near 1 indicate good fit, near 0 indicate poor fit
        - If sigma is None: chi-square value (unnormalized)
    yfit : np.ndarray
        Fitted y values at each x position (1D array of length n)

    Raises
    ------
    LineFitError
        If fewer than 2 data points are provided
        If all x values are identical (no variation)

    Notes
    -----
    The algorithm is based on the standard weighted least-squares formulation:

    For weighted fit (sigma provided):
        w_i = 1 / σ_i²
        a, b minimize: Σ w_i (y_i - a - b*x_i)²

    For unweighted fit (sigma is None):
        w_i = 1 for all i
        Standard errors are scaled by sqrt(χ²/(n-2))

    The correlation coefficient corr_ab measures how the uncertainties in a and b
    are related. A value of -1 or 1 indicates perfect correlation (positive or
    negative), while 0 indicates no correlation.

    Examples
    --------
    Simple unweighted fit:

    >>> x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> y = np.array([2.1, 3.9, 6.1, 8.0, 10.1])
    >>> a, b, std_a, std_b, corr, good, yfit = line_fit(x, y)
    >>> print(f"y = {a:.2f} + {b:.2f}*x")
    y = 0.08 + 2.00*x

    Weighted fit with uncertainties:

    >>> x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> y = np.array([2.1, 3.9, 6.1, 8.0, 10.1])
    >>> sigma = np.array([0.1, 0.1, 0.2, 0.1, 0.1])  # y uncertainties
    >>> a, b, std_a, std_b, corr, good, yfit = line_fit(x, y, sigma)
    >>> print(f"y = {a:.2f} ± {std_a:.2f} + ({b:.2f} ± {std_b:.2f})*x")
    y = 0.08 ± 0.08 + (2.00 ± 0.03)*x

    Check goodness of fit:

    >>> if good > 0.05:  # Q-value > 0.05 suggests acceptable fit
    ...     print("Fit quality is acceptable")
    ... else:
    ...     print("Fit quality is questionable")

    References
    ----------
    - Press, W. H., et al. "Numerical Recipes in C" (1992), Chapter 15
    - Bevington, P. R. "Data Reduction and Error Analysis" (1969)
    """
    # Convert inputs to numpy arrays
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)

    n = len(x)

    # Validate input
    if n < 2:
        raise LineFitError("Number of data points must be at least 2")

    if len(y) != n:
        raise LineFitError(f"x and y must have same length (x: {n}, y: {len(y)})")

    if sigma is not None:
        sigma = np.asarray(sigma, dtype=np.float64)
        if len(sigma) != n:
            raise LineFitError(f"sigma must have same length as x and y ({n})")

    # Calculate sums for weighted or unweighted fit
    if sigma is not None:
        # Weighted fit: weights are 1/sigma^2
        sig2 = sigma * sigma
        s = np.sum(1.0 / sig2)
        sx = np.sum(x / sig2)
        sy = np.sum(y / sig2)
    else:
        # Unweighted fit: all weights are 1
        s = float(n)
        sx = np.sum(x)
        sy = np.sum(y)

    # Calculate centered x values (t = x - mean_x)
    t = x - sx / s

    if sigma is not None:
        t = t / sigma

    # Calculate slope b
    if sigma is not None:
        b = np.sum(t * y / sigma)
    else:
        b = np.sum(t * y)

    # Calculate stt = sum of squared t values
    stt = np.sum(t * t)

    # Check for degenerate case (all x values identical)
    # Use relative threshold compared to the scale of the data
    x_range = np.max(x) - np.min(x)
    if x_range > 0:
        relative_stt = stt / (x_range * x_range * n)
        if relative_stt < 1.0e-10:
            raise LineFitError("All x values appear to be identical (stt < 1e-10)")
    else:
        # Absolute range is zero - x values are truly identical
        raise LineFitError("All x values are identical")

    # Finalize slope and calculate intercept
    b = b / stt
    a = (sy - b * sx) / s

    # Calculate fitted y values and chi-square
    yfit = a + b * x
    residuals = y - yfit

    if sigma is not None:
        residuals = residuals / sigma

    chi2 = np.sum(residuals * residuals)

    # Calculate standard errors for a and b
    std_a = (1.0 + sx * sx / (s * stt)) / s
    std_b = 1.0 / stt

    # For unweighted fit, scale errors by reduced chi-square
    if sigma is None and n > 2:
        scale = chi2 / (n - 2)
        std_a *= scale
        std_b *= scale

    std_a = np.sqrt(std_a)
    std_b = np.sqrt(std_b)

    # Calculate correlation coefficient between a and b
    denominator = s * stt * std_a * std_b
    if abs(denominator) > 1e-100:
        corr_ab = -sx / denominator
        # Clamp to valid range due to numerical precision issues
        corr_ab = np.clip(corr_ab, -1.0, 1.0)
    else:
        corr_ab = 0.0

    # Calculate goodness-of-fit
    if sigma is not None:
        # For weighted fit: Q-value from incomplete gamma function
        # Q(ν/2, χ²/2) where ν = n-2 degrees of freedom
        # This gives probability that chi-square exceeds this value by chance
        nu = n - 2  # degrees of freedom
        goodness = float(gammaincc(nu / 2.0, chi2 / 2.0))
    else:
        # For unweighted fit: just return chi-square
        goodness = float(chi2)

    return (
        float(a),
        float(b),
        float(std_a),
        float(std_b),
        float(corr_ab),
        goodness,
        yfit.astype(np.float32)
    )


def linear_regression(
    x: np.ndarray,
    y: np.ndarray,
    weights: Optional[np.ndarray] = None
) -> Tuple[float, float, float, float, float]:
    """
    Simplified linear regression interface for common use cases.

    This is a convenience wrapper around line_fit() that provides a simpler
    interface for basic linear regression without requiring uncertainty estimates.

    Parameters
    ----------
    x : np.ndarray
        Independent variable
    y : np.ndarray
        Dependent variable
    weights : np.ndarray, optional
        Weights for each data point (w_i = 1/σ_i², where σ_i is uncertainty).
        If provided, these are converted to sigma for line_fit().
        If None, unweighted fit is performed.

    Returns
    -------
    slope : float
        Slope of the fitted line
    intercept : float
        Intercept of the fitted line
    slope_error : float
        Standard error of the slope
    intercept_error : float
        Standard error of the intercept
    r_squared : float
        Coefficient of determination (R², 0 to 1)
        Measures fraction of variance explained by the fit

    Examples
    --------
    >>> x = np.linspace(0, 10, 50)
    >>> y = 2.5 * x + 1.0 + np.random.randn(50) * 0.5
    >>> slope, intercept, slope_err, int_err, r2 = linear_regression(x, y)
    >>> print(f"y = {intercept:.2f} + {slope:.2f}*x (R² = {r2:.3f})")
    y = 1.05 + 2.48*x (R² = 0.996)
    """
    # Convert weights to sigma if provided
    sigma = None
    if weights is not None:
        weights = np.asarray(weights, dtype=np.float64)
        # sigma = 1 / sqrt(weight)
        sigma = 1.0 / np.sqrt(weights)

    # Perform fit
    a, b, std_a, std_b, corr_ab, goodness, yfit = line_fit(x, y, sigma)

    # Calculate R²
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean) ** 2)
    ss_res = np.sum((y - yfit) ** 2)

    if ss_tot > 0:
        r_squared = 1.0 - (ss_res / ss_tot)
    else:
        r_squared = 0.0

    # Return in more intuitive order: slope, intercept
    return (
        float(b),  # slope
        float(a),  # intercept
        float(std_b),  # slope error
        float(std_a),  # intercept error
        float(r_squared)
    )


# Convenience aliases for different naming conventions
def fit_line(*args, **kwargs):
    """Alias for line_fit() for consistency with C naming."""
    return line_fit(*args, **kwargs)


def weighted_linear_fit(*args, **kwargs):
    """Alias for line_fit() emphasizing weighted capability."""
    return line_fit(*args, **kwargs)
