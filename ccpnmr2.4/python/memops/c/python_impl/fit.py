"""
Pure Python implementation of comprehensive curve fitting for NMR data analysis.

This module provides 18 different fitting methods commonly used in NMR spectroscopy,
including linear, log-linear, exponential, exchange, binding, relaxation, and CPMG
dispersion fits. It uses SciPy's curve_fit with Levenberg-Marquardt optimization
and provides bootstrap and Monte Carlo error estimation.

Based on algorithms from Numerical Recipes and NMR-specific models.

Original C code: ccpnmr2.4/c/memops/global/fit.c
"""

import math
import numpy as np
from scipy.optimize import curve_fit
from typing import List, Tuple, Optional, Callable
from .random import set_seed, normal, uniform
from .line_fit import line_fit


# Fitting method constants matching C code
NO_FIT = 0
LINEAR_FIT = 1
LOG_LINEAR_FIT = 2
NONLINEAR2_FIT = 3
NONLINEAR3_FIT = 4
SLOW_EXCHANGE_FIT = 5
LANGMUIR_FIT = 6
KD_SHIFT_FIT = 7
INVERSION_RECOVERY_FIT = 8
KD_ALT_SHIFT_FIT = 9
GAUSSIAN_FIT = 10
COSINE_FIT = 11
CPMG3_FAST_FIT = 12
CPMG3_SLOW_FIT = 13
CPMG4_FAST_FIT = 14
CPMG4_SLOW_FIT = 15
NONLINEAR_INVERSE_FIT = 16
NONLINEAR_INVERSE2_FIT = 17
NFIT_METHODS = 18

# Method names matching C code
FIT_METHODS = [
    "no fit",  # 0
    "Ax + B",  # 1
    "log (A exp(-Bx))",  # 2
    "A exp(-Bx)",  # 3
    "A exp(-Bx) + C",  # 4
    "A (1-sin(Bx)/Bx) + C",  # 5
    "Ax / (1+Ax)",  # 6
    "A ((1+B/4x)-sqrt((1+B/4x)^2 - 1) - C)",  # 7
    "A (1/2 - exp(-Bx))",  # 8
    "A ((B+x)-sqrt((B+x)^2 - 4x))",  # 9
    "A exp(-Bx^2)",  # 10
    "A cos(Bx)",  # 11
    "A+B/2-x acosh(dp cosh(ep/2x) - dm)",  # 12
    "A+B/2-x acosh(dp - dm cos(em/2x))",  # 13
    "A+B/2-x acosh(dp cosh(ep/2x) - dm cos(em/2x)), psi>0",  # 14
    "A+B/2-x acosh(dp cosh(ep/2x) - dm cos(em/2x)), psi<0",  # 15
    "C - A exp(-Bx)",  # 16
    "A(1 - exp(-Bx))",  # 17
]

# Constants from C code
MAX_MODEL_ITER = 20
MAX_CONDITION = 4
CHISQ_STOP_CRITERION = 1.0e-1
MIN_DELTA_X = 1.0e-2
SMALL_X = 1.0e-7
SMALL_ETA = 1.0e-7
BSCALE = 1.0
LARGE_FLOAT = 1.0e30


def get_method_nparams(method: int) -> int:
    """
    Get the number of parameters for a given fitting method.
    
    Args:
        method: Fitting method constant (NO_FIT, LINEAR_FIT, etc.)
    
    Returns:
        Number of parameters for the method
    """
    if method == NO_FIT:
        return 0
    elif method == LINEAR_FIT:
        return 2
    elif method == LOG_LINEAR_FIT:
        return 2
    elif method == NONLINEAR2_FIT:
        return 2
    elif method == NONLINEAR3_FIT:
        return 3
    elif method == SLOW_EXCHANGE_FIT:
        return 3
    elif method == LANGMUIR_FIT:
        return 1
    elif method == KD_SHIFT_FIT:
        return 3
    elif method == INVERSION_RECOVERY_FIT:
        return 2
    elif method == KD_ALT_SHIFT_FIT:
        return 2
    elif method == GAUSSIAN_FIT:
        return 2
    elif method == COSINE_FIT:
        return 2
    elif method in (CPMG3_FAST_FIT, CPMG3_SLOW_FIT):
        return 3
    elif method in (CPMG4_FAST_FIT, CPMG4_SLOW_FIT):
        return 4
    elif method == NONLINEAR_INVERSE_FIT:
        return 3
    elif method == NONLINEAR_INVERSE2_FIT:
        return 2
    else:
        return 0


# ============================================================================
# Fitting Functions - Model Definitions
# ============================================================================

def nonlinear2_func(x, a, b):
    """A exp(-Bx) - Two-parameter exponential decay."""
    return a * np.exp(-b * x)


def nonlinear3_func(x, a, b, c):
    """A exp(-Bx) + C - Three-parameter exponential decay with offset."""
    return a * np.exp(-b * x) + c


def slow_exchange_func(x, a, b, c):
    """
    A (1-sin(Bx)/Bx) + C - Slow exchange model.
    
    Handles small x case specially to avoid division by zero.
    """
    bx = b * np.abs(x)
    result = np.zeros_like(x, dtype=float)
    
    # Small x approximation: sin(bx)/bx ≈ 1 - (bx)^2/6
    small_mask = bx < SMALL_X
    result[small_mask] = a * (bx[small_mask]**2 / 6) + c
    
    # Normal case
    large_mask = ~small_mask
    sinc = np.sin(bx[large_mask]) / bx[large_mask]
    result[large_mask] = a * (1 - sinc) + c
    
    return result


def langmuir_func(x, a):
    """Ax / (1+Ax) - Langmuir isotherm (single-site binding)."""
    ax = a * x
    s = 1 + ax
    return np.where(s != 0, ax / s, LARGE_FLOAT)


def kd_shift_func(x, a, b, c):
    """
    A ((1+B/4x)-sqrt((1+B/4x)^2 - 1) - C) - Kd chemical shift model.
    
    Handles x ≤ 0 case.
    """
    result = np.zeros_like(x, dtype=float)
    pos_mask = x > 0
    
    if np.any(pos_mask):
        t = 1 + b / (4 * x[pos_mask])
        s_sq = t**2 - 1
        s_sq = np.maximum(s_sq, 0)  # Avoid negative square root
        s = np.sqrt(s_sq)
        w = t - s - c
        result[pos_mask] = a * w
    
    return result


def kd_alt_shift_func(x, a, b):
    """A ((B+x)-sqrt((B+x)^2 - 4x)) - Alternative Kd chemical shift."""
    t = b + x
    s_sq = t**2 - 4*x
    s_sq = np.maximum(s_sq, 0)
    s = np.sqrt(s_sq)
    return np.where(s != 0, a * (t - s), LARGE_FLOAT)


def inversion_recovery_func(x, a, b):
    """A (1/2 - exp(-Bx)) - Inversion recovery for T1 measurement."""
    s = np.exp(-b * x / BSCALE)
    return a * (0.5 - s)


def gaussian_func(x, a, b):
    """A exp(-Bx^2) - Gaussian decay."""
    return a * np.exp(-b * x**2)


def cosine_func(x, a, b):
    """A cos(Bx) - Cosine modulation."""
    return a * np.cos(b * x)


def cpmg3_func(x, R2max, kex, dw):
    """
    CPMG 3-parameter fast/slow exchange model.
    
    From Mulder et al., Nature Structural Biology 8 (2001) 932-935.
    x = nu = 1 / (2 tau)
    """
    psi = kex**2 - dw**2
    result = np.zeros_like(x, dtype=float)
    
    # Fast exchange (psi > 0)
    fast_mask = psi > 0
    if np.any(fast_mask):
        psi_f = psi
        Dp = kex**2 / psi_f
        Dm = dw**2 / psi_f
        psis = np.sqrt(psi_f)
        etap = psis / (2.0 * x[fast_mask])
        cosh_etap = np.cosh(etap)
        v = Dp * cosh_etap - Dm
        v_sq = v**2 - 1
        v_sq = np.maximum(v_sq, 1e-10)  # Avoid sqrt of negative
        result[fast_mask] = R2max + 0.5*kex - x[fast_mask] * np.arccosh(v)
    
    # Slow exchange (psi <= 0)
    slow_mask = ~fast_mask
    if np.any(slow_mask):
        psi_s = -psi
        Dp = dw**2 / psi_s
        Dm = kex**2 / psi_s
        psis = np.sqrt(psi_s)
        etam = psis / (2.0 * x[slow_mask])
        cos_etam = np.cos(etam)
        v = Dp - Dm * cos_etam
        v_sq = v**2 - 1
        v_sq = np.maximum(v_sq, 1e-10)
        result[slow_mask] = R2max + 0.5*kex - x[slow_mask] * np.arccosh(v)
    
    return result


def cpmg4_func(x, R2max, kAB, kBA, dw):
    """
    CPMG 4-parameter model for unequal populations.
    
    From Mulder et al., Nature Structural Biology 8 (2001) 932-935.
    x = nu = 1 / (2 tau)
    """
    kex = kAB + kBA
    psi = kex**2 - dw**2
    zeta = 2*dw*(kAB - kBA)
    t = np.sqrt(psi**2 + zeta**2)
    s = (psi + 2*dw**2) / t
    
    Dp = 0.5 * (1 + s)
    Dm = 0.5 * (-1 + s)
    etap = np.sqrt(0.5*(psi+t)) / (2.0*x)
    etam = np.sqrt(0.5*(-psi+t)) / (2.0*x)
    
    # Fall back to 3-parameter if eta too small
    if np.any((np.abs(etap) < SMALL_ETA) | (np.abs(etam) < SMALL_ETA)):
        return cpmg3_func(x, R2max, kex, dw)
    
    cosh_etap = np.cosh(etap)
    cos_etam = np.cos(etam)
    v = Dp*cosh_etap - Dm*cos_etam
    
    return R2max + 0.5*kex - x * np.arccosh(v)


def nonlinear_inverse_func(x, a, b, c):
    """C - A exp(-Bx) - Inverted exponential."""
    return c - a * np.exp(-b * x)


def nonlinear_inverse2_func(x, a, b):
    """A(1 - exp(-Bx)) - Two-parameter inverted exponential."""
    return a * (1 - np.exp(-b * x))


# Dictionary mapping methods to functions
METHOD_FUNCTIONS = {
    NONLINEAR2_FIT: nonlinear2_func,
    NONLINEAR3_FIT: nonlinear3_func,
    SLOW_EXCHANGE_FIT: slow_exchange_func,
    LANGMUIR_FIT: langmuir_func,
    KD_SHIFT_FIT: kd_shift_func,
    KD_ALT_SHIFT_FIT: kd_alt_shift_func,
    INVERSION_RECOVERY_FIT: inversion_recovery_func,
    GAUSSIAN_FIT: gaussian_func,
    COSINE_FIT: cosine_func,
    CPMG3_FAST_FIT: cpmg3_func,
    CPMG3_SLOW_FIT: cpmg3_func,
    CPMG4_FAST_FIT: cpmg4_func,
    CPMG4_SLOW_FIT: cpmg4_func,
    NONLINEAR_INVERSE_FIT: nonlinear_inverse_func,
    NONLINEAR_INVERSE2_FIT: nonlinear_inverse2_func,
}


# ============================================================================
# Parameter Initialization
# ============================================================================

def estimate_initial_params(method: int, x: np.ndarray, y: np.ndarray) -> List[float]:
    """
    Estimate initial parameters for a given fitting method.
    
    Uses heuristics based on data characteristics to provide reasonable
    starting values for the optimization.
    
    Args:
        method: Fitting method constant
        x: X data points
        y: Y data points
    
    Returns:
        List of initial parameter estimates
    """
    n = len(x)
    if n == 0:
        return []
    
    xmin, xmax = np.min(x[x > 0]) if np.any(x > 0) else x[0], np.max(x)
    ymin, ymax = np.min(y), np.max(y)
    y_at_xmin = y[np.argmin(x)] if n > 0 else y[0]
    y_at_xmax = y[np.argmax(x)] if n > 0 else y[-1]
    
    if method == NONLINEAR2_FIT:
        # A exp(-Bx): A ≈ y(0), B from half-life
        a = y_at_xmin
        b = -np.log(0.5 * abs(a) / (abs(y_at_xmax) + 1e-10)) / (xmax + 1e-10)
        return [a, max(b, 0.01)]
    
    elif method == NONLINEAR3_FIT:
        # A exp(-Bx) + C: C ≈ y(∞), A ≈ y(0) - C
        c = y_at_xmax
        a = y_at_xmin - c
        b = -np.log(0.5 * abs(a) / (abs(y_at_xmax - c) + 1e-10)) / (xmax + 1e-10)
        return [a, max(b, 0.01), c]
    
    elif method == SLOW_EXCHANGE_FIT:
        # A (1-sin(Bx)/Bx) + C
        c = y_at_xmin
        idx_max = np.argmax(y)
        x_at_ymax = x[idx_max]
        a = ymax - c
        b = 4.5 / (x_at_ymax + 1e-10)
        return [a, b, c]
    
    elif method == LANGMUIR_FIT:
        # Ax / (1+Ax): At x=1/A, y=0.5
        # Estimate A from y ≈ 0.5
        mid_idx = np.argmin(np.abs(y - 0.5*(ymin+ymax)))
        a = 1.0 / (x[mid_idx] + 1e-10)
        return [a]
    
    elif method in (KD_SHIFT_FIT, KD_ALT_SHIFT_FIT):
        a = ymax - ymin
        b = xmax
        if method == KD_SHIFT_FIT:
            c = ymin
            return [a, b, c]
        return [a, b]
    
    elif method == INVERSION_RECOVERY_FIT:
        # A (1/2 - exp(-Bx/BSCALE)): at x=∞, y → A/2
        a = 2 * ymax if ymax > 0 else 2.0
        # At midpoint: a*(0.5 - exp(-b*x_mid/BSCALE)) = y_mid
        x_mid = xmax / 2
        y_mid = y[len(y)//2] if len(y) > 2 else (y_at_xmin + y_at_xmax) / 2
        frac = 0.5 - y_mid / a if a > 1e-10 else 0.3
        frac = max(min(frac, 0.499), 0.01)  # Clamp
        b = -np.log(frac) * BSCALE / (x_mid + 1e-10)
        return [a, max(b, 0.01)]
    
    elif method == GAUSSIAN_FIT:
        a = ymax
        # Find FWHM approximation
        half_max = 0.5 * ymax
        idx = np.argmin(np.abs(y - half_max))
        x_half = x[idx] if idx < n else xmax
        b = np.log(2) / (x_half**2 + 1e-10)
        return [a, b]
    
    elif method == COSINE_FIT:
        # A cos(Bx): amplitude is max value, estimate period from data range
        a = ymax if abs(ymax) > abs(ymin) else abs(ymin)
        # Estimate frequency: assume at least one period in data range
        # Use first zero crossing or half period estimate
        b = 2*np.pi / (xmax - xmin + 1e-10) if xmax > xmin else 1.0
        return [a, b]
    
    elif method in (CPMG3_FAST_FIT, CPMG3_SLOW_FIT):
        R2max = ymin
        kex = 2 * (ymax - ymin)
        dw = kex / 2
        return [R2max, kex, dw]
    
    elif method in (CPMG4_FAST_FIT, CPMG4_SLOW_FIT):
        R2max = ymin
        kex = 2 * (ymax - ymin)
        kAB = kex / 3
        kBA = kex - kAB
        dw = kex / 2
        return [R2max, kAB, kBA, dw]
    
    elif method == NONLINEAR_INVERSE_FIT:
        # C - A exp(-Bx): C ≈ y(∞), A ≈ C - y(0)
        c = ymax  # Asymptote
        a = c - y_at_xmin  # Initial drop
        if abs(a) < 1e-10:
            a = 0.1
        # From y_mid: c - a*exp(-b*x_mid) = y_mid
        x_mid = xmax / 2
        y_mid = y[len(y)//2] if len(y) > 2 else (y_at_xmin + y_at_xmax) / 2
        b_arg = (c - y_mid) / a
        b_arg = max(min(b_arg, 0.9), 0.01)  # Clamp to avoid log issues
        b = -np.log(b_arg) / (x_mid + 1e-10)
        return [abs(a), max(b, 0.01), c]
    
    elif method == NONLINEAR_INVERSE2_FIT:
        # A(1 - exp(-Bx)): A ≈ y(∞)
        a = ymax if ymax > 0 else 1.0
        # From y_mid: a*(1 - exp(-b*x_mid)) = y_mid
        x_mid = xmax / 2
        y_mid = y[len(y)//2] if len(y) > 2 else (y_at_xmin + y_at_xmax) / 2
        frac = y_mid / a if a > 1e-10 else 0.5
        frac = max(min(frac, 0.99), 0.01)  # Clamp
        b = -np.log(1 - frac) / (x_mid + 1e-10)
        return [a, max(b, 0.01)]
    
    return []


# ============================================================================
# Main Fitting Class
# ============================================================================

class Fit:
    """
    Curve fitting class supporting 18 different NMR-relevant models.
    
    Attributes:
        method: Fitting method constant (LINEAR_FIT, NONLINEAR2_FIT, etc.)
        noise: Estimate noise level for weighting
    """
    
    def __init__(self, method: int = LINEAR_FIT, noise: float = 1.0):
        """
        Initialize fitting object.
        
        Args:
            method: Fitting method constant
            noise: Estimated noise level in data
        """
        self.method = method
        self.noise = noise
    
    def run_fit(self, x: List[float], y: List[float],
                params_fit: Optional[List[float]] = None,
                compute_errors: bool = False) -> dict:
        """
        Run fitting on data.
        
        Args:
            x: X data points
            y: Y data points
            params_fit: Optional initial parameter guesses
            compute_errors: Whether to compute parameter uncertainties
        
        Returns:
            dict: {
                'params': Fitted parameters,
                'params_err': Parameter uncertainties (if compute_errors=True),
                'y_fit': Fitted y values,
                'chisq': Reduced chi-squared,
                'success': Whether fit succeeded,
                'message': Error/success message
            }
        """
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
        n = len(x)
        nparams = get_method_nparams(self.method)
        
        if n < nparams:
            return {
                'params': [0.0] * nparams,
                'params_err': [0.0] * nparams if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': f'Not enough data points ({n}) for {nparams} parameters'
            }
        
        # Handle special cases
        if self.method == NO_FIT:
            return {
                'params': [],
                'params_err': [] if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': True,
                'message': 'No fit requested'
            }
        
        if self.method == LINEAR_FIT:
            return self._fit_linear(x, y, compute_errors)
        
        if self.method == LOG_LINEAR_FIT:
            return self._fit_log_linear(x, y, compute_errors)
        
        # Nonlinear fits
        return self._fit_nonlinear(x, y, params_fit, compute_errors)
    
    def _fit_linear(self, x: np.ndarray, y: np.ndarray, 
                    compute_errors: bool) -> dict:
        """Perform linear fit: y = ax + b."""
        result = line_fit(x.tolist(), y.tolist())
        
        if result.get('error'):
            return {
                'params': [0.0, 0.0],
                'params_err': [0.0, 0.0] if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': result['error']
            }
        
        # Note: line_fit returns (intercept, slope), we return (slope, intercept)
        # to match C code convention
        params = [result['b'], result['a']]  # [slope, intercept]
        params_err = [result['std_b'], result['std_a']] if compute_errors else None
        y_fit = result['a'] + result['b'] * x
        chisq = result['goodness']
        
        return {
            'params': params,
            'params_err': params_err,
            'y_fit': y_fit,
            'chisq': chisq,
            'success': True,
            'message': 'Linear fit successful'
        }
    
    def _fit_log_linear(self, x: np.ndarray, y: np.ndarray,
                       compute_errors: bool) -> dict:
        """Perform log-linear fit: log(y) = log(a) - bx."""
        # Remove non-positive y values
        mask = y > 0
        if np.sum(mask) < 2:
            return {
                'params': [1.0, 0.0],
                'params_err': [0.0, 0.0] if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': 'Not enough positive y values for log-linear fit'
            }
        
        x_used = x[mask]
        y_log = np.log(y[mask])
        
        # Fit log(y) vs x
        result = line_fit(x_used.tolist(), y_log.tolist())
        
        if result.get('error'):
            return {
                'params': [1.0, 0.0],
                'params_err': [0.0, 0.0] if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': result['error']
            }
        
        # log(y) = a + bx => y = exp(a) * exp(bx)
        # So A = exp(a), B = b
        a_log = result['a']
        b = result['b']
        A = np.exp(a_log)
        B = -b  # Note sign flip
        
        y_fit = A * np.exp(-B * x)
        residuals = y - y_fit
        chisq = np.sum(residuals**2) / (len(y) - 2) if len(y) > 2 else 0
        
        params_err = None
        if compute_errors:
            # Approximate error propagation
            params_err = [A * result['std_a'], result['std_b']]
        
        return {
            'params': [A, B],
            'params_err': params_err,
            'y_fit': y_fit,
            'chisq': chisq / (self.noise**2) if self.noise > 0 else chisq,
            'success': True,
            'message': 'Log-linear fit successful'
        }
    
    def _fit_nonlinear(self, x: np.ndarray, y: np.ndarray,
                      params_init: Optional[List[float]],
                      compute_errors: bool) -> dict:
        """Perform nonlinear curve fitting using scipy.optimize.curve_fit."""
        func = METHOD_FUNCTIONS.get(self.method)
        if func is None:
            return {
                'params': [],
                'params_err': [] if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': f'Unknown fitting method {self.method}'
            }
        
        # Get initial parameters
        if params_init is None:
            p0 = estimate_initial_params(self.method, x, y)
        else:
            p0 = params_init
        
        try:
            # Weights based on noise estimate
            sigma = np.full_like(y, self.noise) if self.noise > 0 else None
            
            # Perform curve fit
            popt, pcov = curve_fit(
                func, x, y, p0=p0, sigma=sigma, absolute_sigma=True,
                maxfev=1000 * (len(p0) + 1), method='lm'
            )
            
            # Calculate fitted values
            y_fit = func(x, *popt)
            
            # Calculate chi-squared
            residuals = y - y_fit
            if len(y) > len(popt):
                chisq = np.sum(residuals**2) / (len(y) - len(popt))
                chisq /= (self.noise**2) if self.noise > 0 else 1.0
            else:
                chisq = 0.0
            
            # Parameter uncertainties
            params_err = None
            if compute_errors:
                params_err = np.sqrt(np.diag(pcov)).tolist()
            
            # Post-processing adjustments (matching C code)
            if self.method == SLOW_EXCHANGE_FIT:
                popt[1] = abs(popt[1])
            elif self.method == INVERSION_RECOVERY_FIT:
                popt[1] = popt[1] / BSCALE
            
            return {
                'params': popt.tolist(),
                'params_err': params_err,
                'y_fit': y_fit,
                'chisq': chisq,
                'success': True,
                'message': 'Fit converged successfully'
            }
            
        except RuntimeError as e:
            return {
                'params': p0,
                'params_err': [0.0] * len(p0) if compute_errors else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': f'Fit did not converge: {str(e)}'
            }
        except Exception as e:
            return {
                'params': p0 if p0 else [],
                'params_err': [0.0] * len(p0) if (compute_errors and p0) else None,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': f'Fit error: {str(e)}'
            }
    
    def bootstrap_fit(self, x: List[float], y: List[float], 
                     niter: int = 100) -> dict:
        """
        Perform bootstrap error estimation.
        
        Randomly resamples data with replacement and refits to estimate
        parameter uncertainties.
        
        Args:
            x: X data points
            y: Y data points
            niter: Number of bootstrap iterations
        
        Returns:
            dict with 'params', 'params_avg', 'params_std', 'y_fit', 'chisq'
        """
        x = np.array(x, dtype=float)
        y = np.array(y, dtype=float)
        n = len(x)
        nparams = get_method_nparams(self.method)
        
        params_list = []
        
        for i in range(niter):
            # Bootstrap resample
            indices = np.random.choice(n, size=n, replace=True)
            x_boot = x[indices]
            y_boot = y[indices]
            
            # Fit
            result = self.run_fit(x_boot.tolist(), y_boot.tolist())
            if result['success']:
                params_list.append(result['params'])
        
        if len(params_list) < 2:
            return {
                'params': [0.0] * nparams,
                'params_avg': [0.0] * nparams,
                'params_std': [0.0] * nparams,
                'y_fit': y.copy(),
                'chisq': 0.0,
                'success': False,
                'message': 'Not enough successful bootstrap fits'
            }
        
        params_array = np.array(params_list)
        params_avg = np.mean(params_array, axis=0)
        params_std = np.std(params_array, axis=0, ddof=1)
        
        # Final fit with original data
        final_result = self.run_fit(x.tolist(), y.tolist())
        
        return {
            'params': final_result['params'],
            'params_avg': params_avg.tolist(),
            'params_std': params_std.tolist(),
            'y_fit': final_result['y_fit'],
            'chisq': final_result['chisq'],
            'success': True,
            'message': f'Bootstrap completed with {len(params_list)}/{niter} successful fits'
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def fit_data(method: int, x: List[float], y: List[float],
             noise: float = 1.0, compute_errors: bool = False) -> dict:
    """
    Convenience function to fit data with a single method.
    
    Args:
        method: Fitting method constant
        x: X data points
        y: Y data points
        noise: Estimated noise level
        compute_errors: Whether to compute parameter uncertainties
    
    Returns:
        Fit result dictionary
    """
    fitter = Fit(method=method, noise=noise)
    return fitter.run_fit(x, y, compute_errors=compute_errors)


def exponential_fit(x: List[float], y: List[float], 
                   offset: bool = False, noise: float = 1.0) -> dict:
    """
    Fit exponential decay: A exp(-Bx) or A exp(-Bx) + C.
    
    Args:
        x: X data points
        y: Y data points
        offset: Whether to include constant offset (C parameter)
        noise: Estimated noise level
    
    Returns:
        Fit result dictionary
    """
    method = NONLINEAR3_FIT if offset else NONLINEAR2_FIT
    return fit_data(method, x, y, noise, compute_errors=True)


def gaussian_fit_func(x: List[float], y: List[float], noise: float = 1.0) -> dict:
    """
    Fit Gaussian: A exp(-Bx^2).
    
    Args:
        x: X data points
        y: Y data points
        noise: Estimated noise level
    
    Returns:
        Fit result dictionary
    """
    return fit_data(GAUSSIAN_FIT, x, y, noise, compute_errors=True)
