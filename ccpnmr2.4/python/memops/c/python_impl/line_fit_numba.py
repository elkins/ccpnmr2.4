"""
Numba JIT-compiled implementation of weighted linear least squares fitting.

High-performance version using Numba for fast numerical computation.
"""

try:
    import numpy as np
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from line_fit import line_fit as _fallback_fit


if NUMBA_AVAILABLE:
    @jit(nopython=True)
    def line_fit_numba(x, y, sigma=None):
        """
        Numba JIT-compiled weighted linear least squares fit.
        
        Fits y = a + bx to data with optional weighting.
        
        Args:
            x: NumPy array of x values
            y: NumPy array of y values
            sigma: Optional NumPy array of standard deviations
        
        Returns:
            tuple: (success, a, b, std_a, std_b, corr_ab, goodness, yfit)
                success: True if fit succeeded, False if error
                If success=False, other values are undefined
        """
        n = len(x)
        
        if n < 2:
            # Return error condition
            return (False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, np.zeros(n))
        
        # Initialize accumulators
        has_sigma = sigma is not None
        
        if has_sigma:
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
            sx = 0.0
            sy = 0.0
            
            for i in range(n):
                sx += x[i]
                sy += y[i]
        
        # Compute t array
        t = np.empty(n, dtype=np.float64)
        for i in range(n):
            t[i] = x[i] - sx / s
            if has_sigma:
                t[i] /= sigma[i]
        
        # Compute slope b
        b = 0.0
        for i in range(n):
            d = t[i] * y[i]
            if has_sigma:
                d /= sigma[i]
            b += d
        
        # Compute stt
        stt = 0.0
        for i in range(n):
            stt += t[i] * t[i]
        
        STT_EPS = 1.0e-10
        if stt < STT_EPS:
            # x values all the same
            return (False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, np.zeros(n))
        
        b /= stt
        
        # Compute intercept a
        a = (sy - b * sx) / s
        
        # Compute fitted values and chi-squared
        yfit = np.empty(n, dtype=np.float64)
        chi2 = 0.0
        
        for i in range(n):
            yfit[i] = a + b * x[i]
            d = y[i] - yfit[i]
            
            if has_sigma:
                d /= sigma[i]
            
            chi2 += d * d
        
        # Compute standard errors
        std_a = (1.0 + sx * sx / (s * stt)) / s
        std_b = 1.0 / stt
        
        if not has_sigma and n > 2:
            d = chi2 / (n - 2)
            std_a *= d
            std_b *= d
        
        std_a = np.sqrt(std_a)
        std_b = np.sqrt(std_b)
        
        # Compute correlation
        denominator = s * stt * std_a * std_b
        if abs(denominator) > 1e-20:
            corr_ab = -sx / denominator
        else:
            corr_ab = 0.0
        
        # Goodness of fit
        goodness = chi2
        
        return (True, a, b, std_a, std_b, corr_ab, goodness, yfit)


class LineFitOps:
    """High-level API for line fitting using Numba."""
    
    @staticmethod
    def fit(x, y, sigma=None):
        """
        Fit a straight line y = a + bx to data.
        
        Args:
            x: Array-like x values
            y: Array-like y values
            sigma: Optional array-like standard deviations
        
        Returns:
            dict: Same format as pure Python line_fit
        """
        if not NUMBA_AVAILABLE:
            return _fallback_fit(x, y, sigma)
        
        # Convert to NumPy arrays
        x_arr = np.asarray(x, dtype=np.float64)
        y_arr = np.asarray(y, dtype=np.float64)
        
        if sigma is not None:
            sigma_arr = np.asarray(sigma, dtype=np.float64)
        else:
            sigma_arr = None
        
        success, a, b, std_a, std_b, corr_ab, goodness, yfit = \
            line_fit_numba(x_arr, y_arr, sigma_arr)
        
        if not success:
            if len(x) < 2:
                error_msg = 'number of parameters < 2'
            else:
                error_msg = 'x values all the same (it seems)'
            
            return {
                'a': 0.0,
                'b': 0.0,
                'std_a': 0.0,
                'std_b': 0.0,
                'corr_ab': 0.0,
                'goodness': 0.0,
                'yfit': [],
                'error': error_msg
            }
        
        return {
            'a': float(a),
            'b': float(b),
            'std_a': float(std_a),
            'std_b': float(std_b),
            'corr_ab': float(corr_ab),
            'goodness': float(goodness),
            'yfit': yfit.tolist(),
            'error': None
        }
    
    @staticmethod
    def simple_fit(x, y):
        """
        Simple unweighted line fit returning just (a, b).
        
        Args:
            x: Array-like x values
            y: Array-like y values
        
        Returns:
            tuple: (a, b) where y = a + bx
        """
        result = LineFitOps.fit(x, y)
        if result['error']:
            raise ValueError(result['error'])
        return (result['a'], result['b'])
    
    @staticmethod
    def weighted_fit(x, y, sigma):
        """
        Weighted line fit returning parameters with errors.
        
        Args:
            x: Array-like x values
            y: Array-like y values
            sigma: Array-like standard deviations
        
        Returns:
            tuple: (a, b, std_a, std_b)
        """
        result = LineFitOps.fit(x, y, sigma)
        if result['error']:
            raise ValueError(result['error'])
        return (result['a'], result['b'], result['std_a'], result['std_b'])


# Module-level convenience functions
def line_fit(x, y, sigma=None):
    """Fit a straight line using Numba-optimized code."""
    return LineFitOps.fit(x, y, sigma)


def simple_line_fit(x, y):
    """Simple wrapper for unweighted linear fit."""
    return LineFitOps.simple_fit(x, y)


def weighted_line_fit(x, y, sigma):
    """Simple wrapper for weighted linear fit."""
    return LineFitOps.weighted_fit(x, y, sigma)
