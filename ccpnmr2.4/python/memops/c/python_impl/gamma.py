"""
======================COPYRIGHT/LICENSE START==========================

gamma.py: Part of the CcpNmr Analysis program

Copyright (C) 2003-2010 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

The CCPN license can be found in ../../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

Python implementation of gamma functions using SciPy special functions.

This replaces the C implementation with SciPy's special module, which wraps
the same Cephes library for equivalent performance and accuracy.
"""

import numpy as np
from scipy import special
from typing import Union


NumberType = Union[float, np.ndarray]


def gamma_func(x: NumberType) -> NumberType:
    """Compute the gamma function Γ(x).
    
    The gamma function is defined as:
        Γ(x) = ∫₀^∞ t^(x-1) e^(-t) dt
        
    For positive integers n: Γ(n) = (n-1)!
    
    Args:
        x: Input value(s). Can be a scalar or numpy array.
        
    Returns:
        Γ(x) value(s)
        
    Example:
        >>> gamma_func(5)  # Should be 24.0 (= 4!)
        24.0
        >>> gamma_func(0.5)  # Should be √π
        1.7724538509055159
    """
    return special.gamma(x)


def log_gamma(x: NumberType) -> NumberType:
    """Compute the natural logarithm of the absolute value of gamma function.
    
    This is more numerically stable than computing log(gamma(x)) directly
    for large x values.
    
    Args:
        x: Input value(s). Can be a scalar or numpy array.
        
    Returns:
        ln|Γ(x)| value(s)
        
    Example:
        >>> log_gamma(100)
        359.1342053695754
    """
    return special.gammaln(x)


def incomplete_gamma(a: NumberType, x: NumberType) -> NumberType:
    """Compute the lower incomplete gamma function γ(a, x).
    
    The lower incomplete gamma function is defined as:
        γ(a, x) = ∫₀^x t^(a-1) e^(-t) dt
        
    This is the integral of the gamma function from 0 to x.
    
    Args:
        a: Shape parameter (must be positive)
        x: Upper integration limit (must be non-negative)
        
    Returns:
        γ(a, x) value(s)
        
    Note:
        The normalized version is gammainc(a, x) = γ(a, x) / Γ(a)
    """
    # SciPy's gammainc returns the normalized version γ(a,x)/Γ(a)
    # To get the actual incomplete gamma, multiply by Γ(a)
    return special.gammainc(a, x) * special.gamma(a)


def incomplete_gamma_complement(a: NumberType, x: NumberType) -> NumberType:
    """Compute the upper incomplete gamma function Γ(a, x).
    
    The upper incomplete gamma function is defined as:
        Γ(a, x) = ∫ₓ^∞ t^(a-1) e^(-t) dt
        
    This is the integral of the gamma function from x to infinity.
    
    Args:
        a: Shape parameter (must be positive)
        x: Lower integration limit (must be non-negative)
        
    Returns:
        Γ(a, x) value(s)
        
    Note:
        Γ(a, x) + γ(a, x) = Γ(a)
    """
    # SciPy's gammaincc returns the normalized version Γ(a,x)/Γ(a)
    # To get the actual incomplete gamma, multiply by Γ(a)
    return special.gammaincc(a, x) * special.gamma(a)


def regularized_incomplete_gamma(a: NumberType, x: NumberType) -> NumberType:
    """Compute the regularized (normalized) lower incomplete gamma function.
    
    This is defined as:
        P(a, x) = γ(a, x) / Γ(a)
        
    This represents the CDF of the gamma distribution.
    
    Args:
        a: Shape parameter (must be positive)
        x: Upper integration limit (must be non-negative)
        
    Returns:
        P(a, x) value(s) in range [0, 1]
    """
    return special.gammainc(a, x)


def regularized_incomplete_gamma_complement(a: NumberType, x: NumberType) -> NumberType:
    """Compute the regularized (normalized) upper incomplete gamma function.
    
    This is defined as:
        Q(a, x) = Γ(a, x) / Γ(a) = 1 - P(a, x)
        
    Args:
        a: Shape parameter (must be positive)
        x: Lower integration limit (must be non-negative)
        
    Returns:
        Q(a, x) value(s) in range [0, 1]
    """
    return special.gammaincc(a, x)


def digamma(x: NumberType) -> NumberType:
    """Compute the digamma function ψ(x) = d/dx[ln(Γ(x))].
    
    The digamma function is the logarithmic derivative of the gamma function.
    
    Args:
        x: Input value(s)
        
    Returns:
        ψ(x) value(s)
    """
    return special.digamma(x)


def polygamma(n: int, x: NumberType) -> NumberType:
    """Compute the n-th derivative of the digamma function.
    
    This is the (n+1)-th derivative of ln(Γ(x)).
    
    Args:
        n: Order of derivative (0 = digamma, 1 = trigamma, etc.)
        x: Input value(s)
        
    Returns:
        ψ^(n)(x) value(s)
    """
    return special.polygamma(n, x)


def beta_func(a: NumberType, b: NumberType) -> NumberType:
    """Compute the beta function B(a, b).
    
    The beta function is defined as:
        B(a, b) = Γ(a)Γ(b) / Γ(a+b)
        
    Args:
        a: First parameter (must be positive)
        b: Second parameter (must be positive)
        
    Returns:
        B(a, b) value(s)
    """
    return special.beta(a, b)


def log_beta(a: NumberType, b: NumberType) -> NumberType:
    """Compute the natural logarithm of the beta function.
    
    This is more numerically stable than computing log(beta(a, b)) directly.
    
    Args:
        a: First parameter (must be positive)
        b: Second parameter (must be positive)
        
    Returns:
        ln(B(a, b)) value(s)
    """
    return special.betaln(a, b)


# Convenience functions for common use cases
def factorial(n: int) -> float:
    """Compute n! using the gamma function.
    
    Args:
        n: Non-negative integer
        
    Returns:
        n!
        
    Note:
        For large n, use log_factorial to avoid overflow.
    """
    return special.gamma(n + 1)


def log_factorial(n: int) -> float:
    """Compute ln(n!) using the log-gamma function.
    
    Args:
        n: Non-negative integer
        
    Returns:
        ln(n!)
    """
    return special.gammaln(n + 1)
