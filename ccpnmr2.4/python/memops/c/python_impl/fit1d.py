"""
======================COPYRIGHT/LICENSE START==========================

fit1d.py: Part of the CcpNmr Analysis program

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

Python implementation of 1D function minimization using SciPy.

This replaces the custom C implementation of golden section search and
Brent's method with SciPy's optimize.minimize_scalar, which uses the
same algorithms but with better numerical stability and convergence.
"""

import numpy as np
from scipy import optimize
from typing import Callable, Tuple, Optional, Any


class Fit1dError(Exception):
    """Exception raised when 1D minimization fails."""
    pass


def bracket_minimum(ax: float, bx: float, func: Callable[[float, Any], float],
                   param: Any = None, 
                   grow_limit: float = 100.0,
                   max_iter: int = 100) -> Tuple[float, float, float]:
    """Bracket the minimum of a 1D function.
    
    Given two initial points ax and bx, search in the downhill direction
    and return three points (a, b, c) such that b is between a and c, and
    f(b) < f(a) and f(b) < f(c). This brackets a minimum.
    
    This implements the golden section bracketing algorithm, equivalent to
    the C implementation but using SciPy's optimized version.
    
    Args:
        ax: First initial point
        bx: Second initial point
        func: Function to minimize, signature func(x, param)
        param: Optional parameters to pass to func
        grow_limit: Maximum growth factor for bracket expansion
        max_iter: Maximum iterations for bracketing
        
    Returns:
        Tuple (a, b, c) bracketing the minimum
        
    Raises:
        Fit1dError: If bracketing fails after max_iter iterations
        
    Example:
        >>> def parabola(x, p): return (x - 3)**2
        >>> a, b, c = bracket_minimum(0.0, 1.0, parabola)
        >>> # b should be close to minimum at x=3
    """
    # Wrapper to handle optional param
    if param is None:
        f = lambda x: func(x, None)
    else:
        f = lambda x: func(x, param)
    
    # Use SciPy's bracket function which implements golden section search
    try:
        result = optimize.bracket(f, xa=ax, xb=bx, grow_limit=grow_limit, maxiter=max_iter)
        # SciPy returns (xa, xb, xc, fa, fb, fc, funcalls)
        return result[0], result[1], result[2]
    except Exception as e:
        raise Fit1dError(f"Bracketing failed: {e}")


def golden_search(ax: float, bx: float, cx: float,
                  func: Callable[[float, Any], float],
                  param: Any = None,
                  tol: float = 0.03) -> Tuple[float, float]:
    """Find minimum using golden section search.
    
    Given a bracketed minimum (ax, bx, cx), use golden section search
    to find the minimum with specified tolerance.
    
    This is equivalent to the C implementation but uses SciPy's optimized
    version of the golden section algorithm.
    
    Args:
        ax: Left bracket point
        bx: Middle bracket point  
        cx: Right bracket point
        func: Function to minimize, signature func(x, param)
        param: Optional parameters to pass to func
        tol: Relative tolerance for convergence (default 0.03, matches C)
        
    Returns:
        Tuple (xmin, fmin) where xmin is location of minimum and fmin is value
        
    Example:
        >>> def parabola(x, p): return (x - 3)**2
        >>> xmin, fmin = golden_search(2.0, 3.0, 4.0, parabola)
        >>> # xmin should be close to 3.0
    """
    # Wrapper to handle optional param
    if param is None:
        f = lambda x: func(x, None)
    else:
        f = lambda x: func(x, param)
    
    # Use SciPy's golden section search
    try:
        result = optimize.golden(f, brack=(ax, bx, cx), tol=tol, full_output=True)
        xmin = result[0]
        fmin = result[1]
        return xmin, fmin
    except Exception as e:
        raise Fit1dError(f"Golden search failed: {e}")


def brent_search(ax: float, bx: float, cx: float,
                func: Callable[[float, Any], float],
                param: Any = None,
                tol: float = 0.03) -> Tuple[float, float]:
    """Find minimum using Brent's method.
    
    Brent's method combines golden section search with parabolic interpolation
    for faster convergence. This is generally preferred over pure golden section.
    
    Args:
        ax: Left bracket point
        bx: Middle bracket point
        cx: Right bracket point  
        func: Function to minimize, signature func(x, param)
        param: Optional parameters to pass to func
        tol: Relative tolerance for convergence
        
    Returns:
        Tuple (xmin, fmin) where xmin is location of minimum and fmin is value
        
    Example:
        >>> def parabola(x, p): return (x - 3)**2
        >>> xmin, fmin = brent_search(2.0, 3.0, 4.0, parabola)
        >>> # xmin should be very close to 3.0 (faster than golden)
    """
    # Wrapper to handle optional param
    if param is None:
        f = lambda x: func(x, None)
    else:
        f = lambda x: func(x, param)
    
    # Use SciPy's Brent method
    try:
        result = optimize.brent(f, brack=(ax, bx, cx), tol=tol, full_output=True)
        xmin = result[0]
        fmin = result[1]
        return xmin, fmin
    except Exception as e:
        raise Fit1dError(f"Brent search failed: {e}")


def minimize_scalar(func: Callable[[float, Any], float],
                   param: Any = None,
                   bounds: Optional[Tuple[float, float]] = None,
                   method: str = 'brent',
                   tol: float = 0.03,
                   bracket: Optional[Tuple[float, float, float]] = None) -> Tuple[float, float]:
    """General-purpose 1D minimization (recommended interface).
    
    This is the recommended high-level interface for 1D minimization.
    It automatically handles bracketing and uses the most appropriate
    algorithm based on whether bounds are provided.
    
    Args:
        func: Function to minimize, signature func(x, param)
        param: Optional parameters to pass to func
        bounds: Optional tuple (xmin, xmax) for bounded minimization
        method: Minimization method ('brent', 'golden', 'bounded')
        tol: Relative tolerance for convergence
        bracket: Optional initial bracket (ax, bx, cx)
        
    Returns:
        Tuple (xmin, fmin) where xmin is location of minimum and fmin is value
        
    Raises:
        Fit1dError: If minimization fails
        
    Example:
        >>> def parabola(x, p): return (x - 3)**2
        >>> xmin, fmin = minimize_scalar(parabola)
        >>> # xmin should be close to 3.0
        
        >>> # With bounds
        >>> xmin, fmin = minimize_scalar(parabola, bounds=(0, 10))
    """
    # Wrapper to handle optional param
    if param is None:
        f = lambda x: func(x, None)
    else:
        f = lambda x: func(x, param)
    
    try:
        if bounds is not None:
            # Use bounded method
            result = optimize.minimize_scalar(
                f, bounds=bounds, method='bounded',
                options={'xatol': tol}
            )
        else:
            # Use unbounded method (Brent or golden)
            result = optimize.minimize_scalar(
                f, method=method, bracket=bracket,
                options={'xtol': tol}
            )
        
        if not result.success:
            raise Fit1dError(f"Minimization failed: {result.message}")
        
        return result.x, result.fun
        
    except Exception as e:
        raise Fit1dError(f"Minimization failed: {e}")


def find_minimum(ax: float, bx: float, 
                func: Callable[[float, Any], float],
                param: Any = None,
                method: str = 'brent',
                tol: float = 0.03) -> Tuple[float, float]:
    """Complete minimization: bracket then minimize.
    
    This is equivalent to the typical C usage pattern:
    1. Bracket the minimum
    2. Use golden section or Brent to refine
    
    Args:
        ax: First initial guess
        bx: Second initial guess
        func: Function to minimize, signature func(x, param)
        param: Optional parameters to pass to func
        method: 'brent' (faster) or 'golden' (more robust)
        tol: Relative tolerance for convergence
        
    Returns:
        Tuple (xmin, fmin) where xmin is location of minimum and fmin is value
        
    Example:
        >>> def parabola(x, p): return (x - 3)**2
        >>> xmin, fmin = find_minimum(0.0, 1.0, parabola)
        >>> # xmin should be close to 3.0
    """
    # First bracket the minimum
    a, b, c = bracket_minimum(ax, bx, func, param)
    
    # Then refine with chosen method
    if method == 'golden':
        return golden_search(a, b, c, func, param, tol)
    elif method == 'brent':
        return brent_search(a, b, c, func, param, tol)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'golden' or 'brent'")


# C-compatible function names for legacy code
def bracket_minimum_c(ax_ptr: np.ndarray, bx_ptr: np.ndarray, cx_ptr: np.ndarray,
                     param: Any, func: Callable[[float, Any], float]) -> None:
    """C-compatible bracketing that modifies arrays in-place.
    
    This matches the C signature where pointers are passed and modified.
    Python equivalent uses single-element arrays.
    
    Args:
        ax_ptr: Array containing first point (modified in-place)
        bx_ptr: Array containing second point (modified in-place)
        cx_ptr: Array containing third point (modified in-place)
        param: Parameters to pass to func
        func: Function to minimize
    """
    a, b, c = bracket_minimum(ax_ptr[0], bx_ptr[0], func, param)
    ax_ptr[0] = a
    bx_ptr[0] = b
    cx_ptr[0] = c


def golden_search_c(ax: float, bx: float, cx: float, param: Any,
                   func: Callable[[float, Any], float],
                   xmin_ptr: np.ndarray) -> float:
    """C-compatible golden search that returns fmin and sets xmin via pointer.
    
    Args:
        ax: Left bracket
        bx: Middle bracket
        cx: Right bracket
        param: Parameters to pass to func
        func: Function to minimize
        xmin_ptr: Array to store location of minimum (modified in-place)
        
    Returns:
        Minimum function value
    """
    xmin, fmin = golden_search(ax, bx, cx, func, param)
    xmin_ptr[0] = xmin
    return fmin
