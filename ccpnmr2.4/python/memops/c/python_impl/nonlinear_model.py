"""
======================COPYRIGHT/LICENSE START==========================

nonlinear_model.py: Part of the CcpNmr Analysis program

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

Python implementation of nonlinear model fitting using SciPy.

Uses Levenberg-Marquardt algorithm (Trust Region Reflective by default)
to fit nonlinear models to data points. Based on Numerical Recipes approach
but implemented using SciPy's optimized routines.

References:
- Numerical Recipes in C, pp 521-528
- SciPy optimize.least_squares and optimize.curve_fit
"""

import numpy as np
from scipy import optimize
from typing import Callable, Tuple, Optional, Any
import warnings


class NonlinearModelError(Exception):
    """Exception raised when nonlinear model fitting fails."""
    pass


def nonlinear_fit(x: np.ndarray,
                  y: np.ndarray,
                  model_func: Callable,
                  params_init: np.ndarray,
                  weights: Optional[np.ndarray] = None,
                  max_iter: int = 20,
                  noise: float = 0.0,
                  bounds: Tuple = (-np.inf, np.inf),
                  method: str = 'trf') -> dict:
    """Fit a nonlinear model to data using Levenberg-Marquardt algorithm.
    
    This is the main interface function that wraps SciPy's least_squares
    optimizer to provide C-compatible API.
    
    Args:
        x: Independent variable data (n points)
        y: Dependent variable data (n points)
        model_func: Model function with signature func(x, *params) -> y
                   or func(params, x) -> y
        params_init: Initial parameter estimates (m parameters)
        weights: Optional weights for each data point (n points)
                If None, uniform weights assumed
        max_iter: Maximum iterations (default 20, matches C MAX_MODEL_ITER)
        noise: Estimated noise level. If 0, estimated as 5% of max(|y|)
        bounds: Parameter bounds as (lower, upper) tuples or arrays
        method: Optimization method - 'trf' (default), 'dogbox', or 'lm'
                'trf' = Trust Region Reflective (robust, handles bounds)
                'dogbox' = Dogleg with rectangular trust regions
                'lm' = Levenberg-Marquardt (classic, no bounds)
    
    Returns:
        Dictionary containing:
        - 'params': Fitted parameters (m,)
        - 'params_dev': Parameter standard deviations (m,)
        - 'y_fit': Fitted y values (n,)
        - 'chisq': Reduced chi-squared statistic
        - 'covar': Covariance matrix (m, m)
        - 'success': Whether fit converged
        - 'message': Optimization message
        - 'nfev': Number of function evaluations
        
    Raises:
        NonlinearModelError: If fitting fails or data is singular
        
    Example:
        >>> # Exponential decay model
        >>> def exp_decay(x, A, k):
        ...     return A * np.exp(-k * x)
        >>> x = np.linspace(0, 5, 50)
        >>> y_true = exp_decay(x, 10.0, 0.5)
        >>> y_noisy = y_true + np.random.normal(0, 0.5, len(x))
        >>> result = nonlinear_fit(x, y_noisy, exp_decay, [8.0, 0.4])
        >>> print(f"A = {result['params'][0]:.2f}, k = {result['params'][1]:.2f}")
    """
    # Convert to numpy arrays
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    params_init = np.asarray(params_init, dtype=np.float64)
    
    npts = len(x)
    nparams = len(params_init)
    
    if len(y) != npts:
        raise NonlinearModelError(f"x and y must have same length: {npts} vs {len(y)}")
    
    if npts < nparams:
        raise NonlinearModelError(
            f"Need more data points than parameters: {npts} < {nparams}"
        )
    
    # Estimate noise if not provided
    if noise == 0:
        noise = 0.05 * np.max(np.abs(y))
        if noise == 0:
            noise = 1.0  # Fallback
    
    # Handle weights
    if weights is not None:
        weights = np.asarray(weights, dtype=np.float64)
        if len(weights) != npts:
            raise NonlinearModelError(
                f"Weights must match data length: {len(weights)} vs {npts}"
            )
        # SciPy expects standard deviations, not weights
        # weight = 1/sigma^2, so sigma = 1/sqrt(weight)
        sigma = 1.0 / np.sqrt(weights)
    else:
        sigma = np.ones(npts) * noise
    
    # Detect model function signature
    # Try to determine if func takes (x, *params) or (params, x)
    try:
        # Try standard signature: func(x, *params)
        test_result = model_func(x[0], *params_init)
        
        def residuals(params):
            """Residual function for optimization."""
            y_model = np.array([model_func(xi, *params) for xi in x])
            return (y - y_model) / sigma
        
    except (TypeError, IndexError):
        # Try alternate signature: func(params, x)
        try:
            test_result = model_func(params_init, x[0])
            
            def residuals(params):
                """Residual function for optimization."""
                y_model = np.array([model_func(params, xi) for xi in x])
                return (y - y_model) / sigma
                
        except:
            # Try vectorized versions
            try:
                test_result = model_func(x, *params_init)
                if np.isscalar(test_result) or len(test_result) != npts:
                    raise ValueError("Unexpected return shape")
                
                def residuals(params):
                    """Residual function for optimization (vectorized)."""
                    return (y - model_func(x, *params)) / sigma
                    
            except:
                raise NonlinearModelError(
                    "Could not determine model function signature. "
                    "Expected func(x, *params) or func(params, x)"
                )
    
    # Perform optimization using SciPy's least_squares
    # This implements Trust Region Reflective algorithm (similar to Levenberg-Marquardt)
    try:
        result = optimize.least_squares(
            residuals,
            params_init,
            method=method,
            max_nfev=max_iter * (nparams + 1) * 10,  # Give more function evals
            bounds=bounds,
            ftol=1e-8,  # Function tolerance
            xtol=1e-8,  # Parameter tolerance
            gtol=1e-8   # Gradient tolerance
        )
    except Exception as e:
        raise NonlinearModelError(f"Optimization failed: {e}")
    
    if not result.success:
        # Check if we're close enough despite non-convergence
        if result.cost > 1e3:  # Arbitrary threshold
            raise NonlinearModelError(f"Fit did not converge: {result.message}")
        else:
            warnings.warn(f"Fit may not have fully converged: {result.message}")
    
    params_fit = result.x
    
    # Calculate fitted y values
    try:
        y_fit = np.array([model_func(xi, *params_fit) for xi in x])
    except:
        try:
            y_fit = np.array([model_func(params_fit, xi) for xi in x])
        except:
            y_fit = model_func(x, *params_fit)
    
    # Calculate chi-squared
    residuals_final = (y - y_fit) / sigma
    chisq_total = np.sum(residuals_final**2)
    
    # Reduced chi-squared
    if npts > nparams:
        chisq_reduced = chisq_total / (npts - nparams)
    else:
        chisq_reduced = 0.0
    
    # Normalize by noise
    chisq_normalized = chisq_reduced / (noise * noise)
    
    # Calculate covariance matrix from Jacobian
    # covar = inv(J^T J) where J is the Jacobian
    try:
        # result.jac is the Jacobian at the solution
        # For weighted least squares: covar = (J^T W J)^-1
        # where W is the weight matrix (diagonal with 1/sigma^2)
        jacobian = result.jac
        
        # Compute covariance: (J^T J)^-1 * residual_variance
        # Since residuals are already weighted, we use result directly
        _, s, VT = np.linalg.svd(jacobian, full_matrices=False)
        threshold = np.finfo(float).eps * max(jacobian.shape) * s[0]
        s_inv = np.array([1/val if val > threshold else 0 for val in s])
        covar = np.dot(VT.T, np.dot(np.diag(s_inv**2), VT))
        
        # Scale by residual variance
        if npts > nparams:
            covar *= (chisq_total / (npts - nparams))
        
    except np.linalg.LinAlgError:
        # Singular matrix - use diagonal approximation
        warnings.warn("Covariance matrix singular, using diagonal approximation")
        covar = np.eye(nparams) * (noise * noise)
    
    # Calculate parameter standard deviations
    params_dev = np.sqrt(np.maximum(np.diag(covar), 0))
    
    return {
        'params': params_fit,
        'params_dev': params_dev,
        'y_fit': y_fit,
        'chisq': chisq_normalized,
        'covar': covar,
        'success': result.success,
        'message': result.message,
        'nfev': result.nfev,
        'cost': result.cost
    }


def curve_fit_wrapper(x: np.ndarray,
                      y: np.ndarray,
                      model_func: Callable,
                      params_init: np.ndarray,
                      weights: Optional[np.ndarray] = None,
                      max_iter: int = 20,
                      bounds: Tuple = (-np.inf, np.inf)) -> dict:
    """Alternative interface using scipy.optimize.curve_fit.
    
    This provides a higher-level interface that may be more convenient
    for some use cases. Uses Levenberg-Marquardt by default.
    
    Args:
        x: Independent variable data
        y: Dependent variable data
        model_func: Model function with signature func(x, *params)
        params_init: Initial parameter estimates
        weights: Optional weights (will be converted to sigma)
        max_iter: Maximum iterations
        bounds: Parameter bounds
        
    Returns:
        Dictionary with same structure as nonlinear_fit()
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    params_init = np.asarray(params_init, dtype=np.float64)
    
    npts = len(x)
    nparams = len(params_init)
    
    # Handle weights
    if weights is not None:
        weights = np.asarray(weights, dtype=np.float64)
        sigma = 1.0 / np.sqrt(weights)
    else:
        sigma = None
    
    try:
        # Use curve_fit which implements Levenberg-Marquardt
        params_fit, covar = optimize.curve_fit(
            model_func,
            x, y,
            p0=params_init,
            sigma=sigma,
            absolute_sigma=False,  # Use reduced chi-squared
            maxfev=max_iter * (nparams + 1) * 10,
            bounds=bounds
        )
    except RuntimeError as e:
        raise NonlinearModelError(f"curve_fit failed: {e}")
    except Exception as e:
        raise NonlinearModelError(f"Optimization failed: {e}")
    
    # Calculate fitted values
    y_fit = model_func(x, *params_fit)
    
    # Calculate chi-squared
    residuals = y - y_fit
    if sigma is not None:
        residuals = residuals / sigma
    
    chisq_total = np.sum(residuals**2)
    if npts > nparams:
        chisq_reduced = chisq_total / (npts - nparams)
    else:
        chisq_reduced = 0.0
    
    # Parameter standard deviations
    params_dev = np.sqrt(np.maximum(np.diag(covar), 0))
    
    return {
        'params': params_fit,
        'params_dev': params_dev,
        'y_fit': y_fit,
        'chisq': chisq_reduced,
        'covar': covar,
        'success': True,
        'message': 'curve_fit succeeded',
        'nfev': -1,  # Not available from curve_fit
        'cost': chisq_total / 2
    }


# Convenience aliases for common fitting scenarios
def exponential_fit(x: np.ndarray, y: np.ndarray,
                   params_init: np.ndarray = None,
                   weights: Optional[np.ndarray] = None) -> dict:
    """Fit exponential decay: y = A * exp(-k * x) + C
    
    Args:
        x: Independent variable
        y: Dependent variable
        params_init: Initial [A, k, C] (default: estimated from data)
        weights: Optional weights
        
    Returns:
        Fit results dictionary
    """
    def exp_model(x, A, k, C):
        return A * np.exp(-k * x) + C
    
    if params_init is None:
        # Estimate initial parameters
        C_est = np.min(y)
        A_est = np.max(y) - C_est
        k_est = 1.0 / (np.max(x) - np.min(x)) if np.max(x) > np.min(x) else 1.0
        params_init = [A_est, k_est, C_est]
    
    return nonlinear_fit(x, y, exp_model, params_init, weights=weights)


def gaussian_fit(x: np.ndarray, y: np.ndarray,
                params_init: np.ndarray = None,
                weights: Optional[np.ndarray] = None) -> dict:
    """Fit Gaussian: y = A * exp(-(x - mu)^2 / (2 * sigma^2)) + C
    
    Args:
        x: Independent variable
        y: Dependent variable  
        params_init: Initial [A, mu, sigma, C] (default: estimated from data)
        weights: Optional weights
        
    Returns:
        Fit results dictionary
    """
    def gauss_model(x, A, mu, sigma, C):
        return A * np.exp(-(x - mu)**2 / (2 * sigma**2)) + C
    
    if params_init is None:
        # Estimate initial parameters
        C_est = np.min(y)
        A_est = np.max(y) - C_est
        mu_est = x[np.argmax(y)]
        sigma_est = (np.max(x) - np.min(x)) / 4
        params_init = [A_est, mu_est, sigma_est, C_est]
    
    return nonlinear_fit(x, y, gauss_model, params_init, weights=weights)
