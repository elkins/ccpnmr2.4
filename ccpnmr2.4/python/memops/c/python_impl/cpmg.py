"""
======================COPYRIGHT/LICENSE START==========================

cpmg.py: Part of the CcpNmr Analysis program

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

Python implementation of CPMG relaxation dispersion curve fitting using SciPy.

CPMG (Carr-Purcell-Meiboom-Gill) experiments measure exchange dynamics in proteins.
This module fits relaxation dispersion curves to extract kinetic and thermodynamic
parameters.

References:
- Mulder, Mittermaier, Hon, Dahlquist and Kay
  Nature Structural Biology 8 (2001) 932-935
"""

import numpy as np
from scipy import optimize
from typing import Tuple, Callable
import math


class CpmgError(Exception):
    """Exception raised when CPMG fitting fails."""
    pass


def cpmg3(nu: float, params: np.ndarray) -> float:
    """Calculate R2 effective for 3-parameter CPMG model.
    
    This is the Carver-Richards equation for two-site chemical exchange.
    
    Args:
        nu: CPMG frequency nu = 1/(2*tau) where tau is delay between refocusing pulses
        params: Array [R2max, kex, dw] where:
            - R2max: Intrinsic R2 relaxation rate (s^-1)
            - kex: Exchange rate constant kex = kAB + kBA (s^-1)
            - dw: Chemical shift difference (rad/s)
            
    Returns:
        R2_eff: Effective R2 relaxation rate at this CPMG frequency
        
    Reference:
        Nature Structural Biology 8 (2001) 932-935
    """
    R2max, kex, dw = params
    
    psi = kex**2 - dw**2
    
    if psi > 0:
        # Fast exchange regime
        Dp = kex**2 / psi
        Dm = dw**2 / psi
        etap = math.sqrt(psi) / (2.0 * nu)
        v = Dp * math.cosh(etap) - Dm
    else:
        # Slow exchange regime  
        psi = -psi
        Dp = dw**2 / psi
        Dm = kex**2 / psi
        etam = math.sqrt(psi) / (2.0 * nu)
        v = Dp - Dm * math.cos(etam)
    
    return R2max + 0.5 * kex - nu * math.acosh(v)


def cpmg4(nu: float, params: np.ndarray) -> float:
    """Calculate R2 effective for 4-parameter CPMG model.
    
    This is the full Carver-Richards equation with separate forward and
    reverse rate constants.
    
    Args:
        nu: CPMG frequency nu = 1/(2*tau)
        params: Array [R2max, kAB, kBA, dw] where:
            - R2max: Intrinsic R2 relaxation rate (s^-1)
            - kAB: Forward exchange rate A→B (s^-1)
            - kBA: Reverse exchange rate B→A (s^-1)
            - dw: Chemical shift difference (rad/s)
            
    Returns:
        R2_eff: Effective R2 relaxation rate
    """
    R2max, kAB, kBA, dw = params
    
    kex = kAB + kBA
    psi = kex**2 - dw**2
    zeta = 2 * dw * (kAB - kBA)
    t = math.sqrt(psi**2 + zeta**2)
    s = (psi + 2 * dw**2) / t
    
    Dp = 0.5 * (1 + s)
    Dm = 0.5 * (-1 + s)
    etap = math.sqrt(0.5 * (psi + t)) / (2.0 * nu)
    etam = math.sqrt(0.5 * (-psi + t)) / (2.0 * nu)
    v = Dp * math.cosh(etap) - Dm * math.cos(etam)
    
    return R2max + 0.5 * kex - nu * math.acosh(v)


def _diff2(nu_values: np.ndarray, r2_obs: np.ndarray, params: np.ndarray,
          model_func: Callable) -> float:
    """Calculate sum of squared residuals.
    
    Args:
        nu_values: Array of CPMG frequencies
        r2_obs: Array of observed R2_eff values
        params: Model parameters
        model_func: Either cpmg3 or cpmg4
        
    Returns:
        Sum of squared differences between observed and calculated
    """
    residuals = 0.0
    for i in range(len(nu_values)):
        calc = model_func(nu_values[i], params)
        diff = calc - r2_obs[i]
        residuals += diff * diff
    return residuals


def cpmg3_fast_init_params(nu_values: np.ndarray, r2_obs: np.ndarray) -> np.ndarray:
    """Initialize parameters for fast exchange 3-parameter CPMG model.
    
    Uses heuristics to estimate initial parameters based on min/max R2_eff.
    
    Args:
        nu_values: Array of CPMG frequencies (Hz)
        r2_obs: Array of observed R2_eff values (s^-1)
        
    Returns:
        Array [R2max, kex, dw] of initial parameter estimates
    """
    ymin = np.min(r2_obs)
    ymax = np.max(r2_obs)
    
    R2max = ymin
    z = 2 * (ymax - ymin)  # Rough estimate
    
    # For fast exchange: kex = 0.5 * (z^2 + dw^2) / z
    # We need to find optimal dw by minimizing residuals
    
    def objective(dw):
        kex = 0.5 * (z**2 + dw**2) / z
        params = np.array([R2max, kex, dw])
        return _diff2(nu_values, r2_obs, params, cpmg3)
    
    # Initial bracket based on z
    ax = 8 * z
    bx = 12 * z
    
    try:
        # Find optimal dw
        result = optimize.minimize_scalar(objective, bracket=(ax, bx))
        dw = result.x
        kex = 0.5 * (z**2 + dw**2) / z
        
        return np.array([R2max, kex, dw])
    except:
        # Fallback to simple estimate
        return np.array([R2max, z, 10 * z])


def cpmg3_slow_init_params(nu_values: np.ndarray, r2_obs: np.ndarray) -> np.ndarray:
    """Initialize parameters for slow exchange 3-parameter CPMG model.
    
    Args:
        nu_values: Array of CPMG frequencies (Hz)
        r2_obs: Array of observed R2_eff values (s^-1)
        
    Returns:
        Array [R2max, kex, dw] of initial parameter estimates
    """
    ymin = np.min(r2_obs)
    ymax = np.max(r2_obs)
    
    R2max = ymin
    kex = 2 * (ymax - ymin)  # For slow exchange, kex ~ z
    
    # Find optimal dw
    def objective(dw):
        params = np.array([R2max, kex, dw])
        return _diff2(nu_values, r2_obs, params, cpmg3)
    
    ax = 4 * kex
    bx = 6 * kex
    
    try:
        result = optimize.minimize_scalar(objective, bracket=(ax, bx))
        dw = result.x
        
        return np.array([R2max, kex, dw])
    except:
        # Fallback
        return np.array([R2max, kex, 5 * kex])


def cpmg4_fast_init_params(nu_values: np.ndarray, r2_obs: np.ndarray) -> np.ndarray:
    """Initialize parameters for fast exchange 4-parameter CPMG model.
    
    Args:
        nu_values: Array of CPMG frequencies
        r2_obs: Array of observed R2_eff values
        
    Returns:
        Array [R2max, kAB, kBA, dw] of initial parameter estimates
    """
    params3 = cpmg3_fast_init_params(nu_values, r2_obs)
    
    # Assume equal populations (pAB = pBA = 0.5)
    pAB = 0.5
    pBA = 1 - pAB
    
    R2max = params3[0]
    kex = params3[1]
    dw = params3[2]
    
    kAB = pAB * kex
    kBA = pBA * kex
    
    return np.array([R2max, kAB, kBA, dw])


def cpmg4_slow_init_params(nu_values: np.ndarray, r2_obs: np.ndarray) -> np.ndarray:
    """Initialize parameters for slow exchange 4-parameter CPMG model.
    
    Args:
        nu_values: Array of CPMG frequencies
        r2_obs: Array of observed R2_eff values
        
    Returns:
        Array [R2max, kAB, kBA, dw] of initial parameter estimates
    """
    params3 = cpmg3_slow_init_params(nu_values, r2_obs)
    
    # Assume equal populations
    pAB = 0.5
    pBA = 1 - pAB
    
    R2max = params3[0]
    kex = params3[1]
    dw = params3[2]
    
    kAB = pAB * kex
    kBA = pBA * kex
    
    return np.array([R2max, kAB, kBA, dw])


def fit_cpmg3(nu_values: np.ndarray, r2_obs: np.ndarray,
              exchange_regime: str = 'fast',
              bounds: Tuple = None) -> Tuple[np.ndarray, float]:
    """Fit 3-parameter CPMG model to relaxation dispersion data.
    
    Args:
        nu_values: Array of CPMG frequencies (Hz)
        r2_obs: Array of observed R2_eff values (s^-1)
        exchange_regime: 'fast' or 'slow' exchange
        bounds: Optional parameter bounds as ((R2min, kexmin, dwmin), (R2max, kexmax, dwmax))
        
    Returns:
        Tuple (params, chi2) where:
        - params: Fitted parameters [R2max, kex, dw]
        - chi2: Chi-squared goodness of fit
        
    Raises:
        CpmgError: If fitting fails
    """
    # Get initial parameters
    if exchange_regime == 'fast':
        p0 = cpmg3_fast_init_params(nu_values, r2_obs)
    else:
        p0 = cpmg3_slow_init_params(nu_values, r2_obs)
    
    # Define objective function
    def objective(params):
        return _diff2(nu_values, r2_obs, params, cpmg3)
    
    try:
        # Minimize
        result = optimize.minimize(objective, p0, method='Nelder-Mead',
                                   bounds=bounds)
        
        if not result.success:
            raise CpmgError(f"Fitting failed: {result.message}")
        
        params_fit = result.x
        chi2 = result.fun / len(nu_values)  # Reduced chi-squared
        
        return params_fit, chi2
        
    except Exception as e:
        raise CpmgError(f"CPMG3 fitting failed: {e}")


def fit_cpmg4(nu_values: np.ndarray, r2_obs: np.ndarray,
              exchange_regime: str = 'fast',
              bounds: Tuple = None) -> Tuple[np.ndarray, float]:
    """Fit 4-parameter CPMG model to relaxation dispersion data.
    
    Args:
        nu_values: Array of CPMG frequencies (Hz)
        r2_obs: Array of observed R2_eff values (s^-1)
        exchange_regime: 'fast' or 'slow' exchange
        bounds: Optional parameter bounds
        
    Returns:
        Tuple (params, chi2) where:
        - params: Fitted parameters [R2max, kAB, kBA, dw]
        - chi2: Chi-squared goodness of fit
        
    Raises:
        CpmgError: If fitting fails
    """
    # Get initial parameters
    if exchange_regime == 'fast':
        p0 = cpmg4_fast_init_params(nu_values, r2_obs)
    else:
        p0 = cpmg4_slow_init_params(nu_values, r2_obs)
    
    # Define objective function
    def objective(params):
        return _diff2(nu_values, r2_obs, params, cpmg4)
    
    try:
        # Minimize
        result = optimize.minimize(objective, p0, method='Nelder-Mead',
                                   bounds=bounds)
        
        if not result.success:
            raise CpmgError(f"Fitting failed: {result.message}")
        
        params_fit = result.x
        chi2 = result.fun / len(nu_values)
        
        return params_fit, chi2
        
    except Exception as e:
        raise CpmgError(f"CPMG4 fitting failed: {e}")


def fit_cpmg_curve(nu_values: np.ndarray, r2_obs: np.ndarray,
                   model: str = 'cpmg3',
                   exchange_regime: str = 'fast') -> dict:
    """High-level interface for CPMG curve fitting.
    
    Args:
        nu_values: Array of CPMG frequencies (Hz)
        r2_obs: Array of observed R2_eff values (s^-1)
        model: 'cpmg3' (3 parameters) or 'cpmg4' (4 parameters)
        exchange_regime: 'fast' or 'slow'
        
    Returns:
        Dictionary with keys:
        - 'params': Fitted parameters
        - 'chi2': Reduced chi-squared
        - 'R2max': Intrinsic R2
        - 'kex': Exchange rate (if cpmg3)
        - 'kAB', 'kBA': Forward/reverse rates (if cpmg4)
        - 'dw': Chemical shift difference
        - 'r2_calc': Calculated R2_eff values
        
    Example:
        >>> nu = np.array([50, 100, 200, 400, 800])
        >>> r2 = np.array([10.5, 9.8, 8.5, 7.2, 6.5])
        >>> result = fit_cpmg_curve(nu, r2, model='cpmg3', exchange_regime='fast')
        >>> print(f"kex = {result['kex']:.2f} s^-1")
    """
    if model == 'cpmg3':
        params, chi2 = fit_cpmg3(nu_values, r2_obs, exchange_regime)
        r2_calc = np.array([cpmg3(nu, params) for nu in nu_values])
        
        return {
            'params': params,
            'chi2': chi2,
            'R2max': params[0],
            'kex': params[1],
            'dw': params[2],
            'r2_calc': r2_calc
        }
    elif model == 'cpmg4':
        params, chi2 = fit_cpmg4(nu_values, r2_obs, exchange_regime)
        r2_calc = np.array([cpmg4(nu, params) for nu in nu_values])
        
        return {
            'params': params,
            'chi2': chi2,
            'R2max': params[0],
            'kAB': params[1],
            'kBA': params[2],
            'kex': params[1] + params[2],
            'dw': params[3],
            'r2_calc': r2_calc
        }
    else:
        raise ValueError(f"Unknown model: {model}. Use 'cpmg3' or 'cpmg4'")
