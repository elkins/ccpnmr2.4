"""
Pure Python implementation of weighted linear least squares fitting.

This module implements linear regression (y = a + bx) with optional weighting
by standard deviations. It computes the best-fit line along with statistical
measures including standard errors, correlation coefficient, and goodness of fit.

Based on weighted least squares from Numerical Recipes.

Original C code: ccpnmr2.4/c/memops/global/line_fit.c
"""

import math


def line_fit(x, y, sigma=None):
    """
    Fit a straight line y = a + bx to data with optional weights.
    
    Uses weighted least squares if sigma (standard deviations) provided.
    Computes fit parameters, their uncertainties, and goodness of fit.
    
    Args:
        x: List of x values (independent variable)
        y: List of y values (dependent variable)
        sigma: Optional list of standard deviations for weighting
               If None, unweighted fit is performed
    
    Returns:
        dict: {
            'a': Intercept
            'b': Slope
            'std_a': Standard error in intercept
            'std_b': Standard error in slope
            'corr_ab': Correlation coefficient between a and b
            'goodness': Goodness of fit (chi-squared or Q-value)
            'yfit': Fitted y values
            'error': Error message if any, None otherwise
        }
    
    Example:
        >>> x = [0.0, 1.0, 2.0, 3.0]
        >>> y = [1.0, 3.0, 5.0, 7.0]
        >>> result = line_fit(x, y)
        >>> print(f"y = {result['a']:.2f} + {result['b']:.2f}x")
    """
    n = len(x)
    
    if n != len(y):
        return {'error': 'x and y must have same length'}
    
    if n < 2:
        return {'error': 'number of parameters < 2'}
    
    if sigma is not None and len(sigma) != n:
        return {'error': 'sigma must have same length as x and y'}
    
    # Initialize accumulators
    if sigma is not None:
        # Weighted sums
        s = 0.0
        sx = 0.0
        sy = 0.0
        
        for i in range(n):
            sig2 = sigma[i] * sigma[i]
            s += 1.0 / sig2
            sx += x[i] / sig2
            sy += y[i] / sig2
    else:
        # Unweighted sums
        s = float(n)
        sx = sum(x)
        sy = sum(y)
    
    # Compute intermediate values t[i] = (x[i] - mean_x) / sigma[i]
    t = []
    for i in range(n):
        ti = x[i] - sx / s
        if sigma is not None:
            ti /= sigma[i]
        t.append(ti)
    
    # Compute slope b
    b = 0.0
    for i in range(n):
        d = t[i] * y[i]
        if sigma is not None:
            d /= sigma[i]
        b += d
    
    # Compute stt = sum of t[i]^2
    stt = sum(ti * ti for ti in t)
    
    STT_EPS = 1.0e-10
    if stt < STT_EPS:
        return {'error': 'x values all the same (it seems)'}
    
    b /= stt
    
    # Compute intercept a
    a = (sy - b * sx) / s
    
    # Compute fitted values and chi-squared
    yfit = []
    chi2 = 0.0
    for i in range(n):
        yfit_i = a + b * x[i]
        yfit.append(yfit_i)
        
        d = y[i] - yfit_i
        if sigma is not None:
            d /= sigma[i]
        
        chi2 += d * d
    
    # Compute standard errors
    std_a = (1.0 + sx * sx / (s * stt)) / s
    std_b = 1.0 / stt
    
    if sigma is None and n > 2:
        # For unweighted fit, scale by reduced chi-squared
        d = chi2 / (n - 2)
        std_a *= d
        std_b *= d
    
    std_a = math.sqrt(std_a)
    std_b = math.sqrt(std_b)
    
    # Compute correlation between a and b
    denominator = s * stt * std_a * std_b
    if abs(denominator) > 1e-20:
        corr_ab = -sx / denominator
    else:
        corr_ab = 0.0
    
    # Compute goodness of fit
    if sigma is not None:
        # For weighted fit, use incomplete gamma function (Q-value)
        # This requires the gamma module - for now use chi2 as approximation
        goodness = chi2  # Simplified - could use scipy.special.gammaincc
    else:
        # For unweighted fit, just return chi-squared
        goodness = chi2
    
    return {
        'a': a,
        'b': b,
        'std_a': std_a,
        'std_b': std_b,
        'corr_ab': corr_ab,
        'goodness': goodness,
        'yfit': yfit,
        'error': None
    }


def simple_line_fit(x, y):
    """
    Simple wrapper for unweighted linear fit.
    
    Args:
        x: List of x values
        y: List of y values
    
    Returns:
        tuple: (a, b) where y = a + bx
    """
    result = line_fit(x, y)
    if result['error']:
        raise ValueError(result['error'])
    return (result['a'], result['b'])


def weighted_line_fit(x, y, sigma):
    """
    Simple wrapper for weighted linear fit.
    
    Args:
        x: List of x values
        y: List of y values
        sigma: List of standard deviations
    
    Returns:
        tuple: (a, b, std_a, std_b) fit parameters with errors
    """
    result = line_fit(x, y, sigma)
    if result['error']:
        raise ValueError(result['error'])
    return (result['a'], result['b'], result['std_a'], result['std_b'])
