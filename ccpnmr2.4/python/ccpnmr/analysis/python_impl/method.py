"""
Peak Fitting Methods

Python implementation of method.c for NMR peak position and volume fitting.

Provides two main fitting approaches:
1. Parabolic fitting - Simple quadratic interpolation for peak centers
2. Gaussian fitting - Log-space fitting assuming Gaussian line shapes

These methods refine peak positions and calculate volumes using three-point
fits (the peak value and its immediate neighbors in each dimension).

Original C implementation: ccpnmr2.4/c/ccpnmr/analysis/method.c (234 lines)
"""

import numpy as np
from typing import Tuple, List, Optional


# Method constants
FIT_VOLUME_GAUSSIAN3_METHOD = 0
NFIT_VOLUME_METHODS = 1

FIT_CENTER_PARABOLIC_METHOD = 0
FIT_CENTER_GAUSSIAN3_METHOD = 1
NFIT_CENTER_METHODS = 2

# Small value threshold for numerical stability
SMALL_VALUE = 1.0e-4

# Fudge factor for volume calculation (prevents divide by zero)
FUDGE_MULT = 0.01


def _fit_center3(u: float, v: float, w: float, use_log: bool) -> Tuple[float, float]:
    """
    Fit peak center using three adjacent points.
    
    Uses parabolic (quadratic) or Gaussian (log-space parabolic) fitting
    to find the sub-pixel peak position from three intensity values.
    
    Args:
        u: Intensity at position x-1
        v: Intensity at position x (peak)
        w: Intensity at position x+1
        use_log: If True, use log-space (Gaussian) fitting
        
    Returns:
        Tuple of (offset, b) where:
            offset: Fractional offset of true peak from x (range -0.499 to 0.499)
            b: Parameter used for volume calculation
            
    Note:
        Assumes v is the maximum (if positive) or minimum (if negative).
        Offset is positive if peak is toward w, negative if toward u.
    """
    is_positive = v > 0
    
    # For Gaussian fitting, work in log space with positive values
    if use_log:
        if not is_positive:
            u, v, w = -u, -v, -w
            
        if u > 0 and w > 0:
            u = np.log(u)
            v = np.log(v)
            w = np.log(w)
        # Otherwise fall back to non-log fit
    
    # Calculate parabola parameters
    d = 0.5 * abs(2*v - u - w)
    
    # b is used for volume calculation (preserves sign)
    b = d if is_positive else -d
    
    # Calculate fractional offset
    if d > SMALL_VALUE:
        c = 0.25 * abs(w - u) / d
        
        # Adjust sign based on whether peak is positive or negative
        if is_positive:
            if w < u:
                c = -c
        else:
            if w > u:
                c = -c
                
        # Clamp to reasonable range
        c = max(c, -0.499)
        c = min(c, 0.499)
    else:
        c = 0.0
        
    return c, b


def fit_volume_gaussian3_method(ndim: int, y: float,
                                ym: np.ndarray, yp: np.ndarray,
                                dim_done: np.ndarray) -> float:
    """
    Calculate peak volume using Gaussian 3-point fitting.
    
    Fits a Gaussian peak shape in each dimension and integrates to
    estimate total peak volume. Uses log-space fitting for robustness.
    
    Args:
        ndim: Number of dimensions
        y: Peak intensity at center
        ym: Intensities at position-1 in each dimension
        yp: Intensities at position+1 in each dimension
        dim_done: Boolean array indicating which dimensions to use
        
    Returns:
        Estimated peak volume
        
    Note:
        Volume calculation assumes Gaussian line shapes and integrates
        analytically. The result is scaled by the central intensity.
    """
    volume = 1.0
    
    for i in range(ndim):
        if not dim_done[i]:
            continue
            
        vm = ym[i]
        v = y
        vp = yp[i]
        
        # Ensure peak is actually a maximum/minimum
        if v > 0:
            if vm > v or vp > v:
                # Not a true maximum, adjust
                v = max(vm, vp)
                vm = vp = y
            else:
                # Ensure neighbors are positive for log
                vm = max(vm, FUDGE_MULT * y)
                vp = max(vp, FUDGE_MULT * y)
        else:
            if vm < v or vp < v:
                # Not a true minimum, adjust
                v = min(vm, vp)
                vm = vp = y
            else:
                # Ensure neighbors have right sign
                vm = min(vm, FUDGE_MULT * y)
                vp = min(vp, FUDGE_MULT * y)
        
        # Fit in this dimension
        c, b = _fit_center3(vm, v, vp, use_log=True)
        
        # Gaussian integral: y * sqrt(pi / b)
        # where b is the width parameter from the fit
        volume *= np.sqrt(np.pi / abs(b))
    
    # Scale by central intensity
    volume *= y
    
    return volume


def fit_center_parabolic_method(ndim: int, center: np.ndarray, y: float,
                                ym: np.ndarray, yp: np.ndarray,
                                dim_done: np.ndarray) -> None:
    """
    Fit peak center using parabolic (quadratic) interpolation.
    
    Updates the center array with fractional offsets from the grid
    points, using simple parabolic fitting in each dimension.
    
    Args:
        ndim: Number of dimensions
        center: Output array for fractional offsets (modified in place)
        y: Peak intensity at center
        ym: Intensities at position-1 in each dimension
        yp: Intensities at position+1 in each dimension
        dim_done: Boolean array indicating which dimensions to use
        
    Note:
        center[i] will be set to the fractional offset (typically -0.5 to 0.5)
        for dimensions where dim_done[i] is True, and 0 otherwise.
    """
    for i in range(ndim):
        if dim_done[i]:
            c, b = _fit_center3(ym[i], y, yp[i], use_log=False)
            center[i] = c
        else:
            center[i] = 0.0


def fit_center_gaussian3_method(ndim: int, center: np.ndarray, y: float,
                                ym: np.ndarray, yp: np.ndarray,
                                dim_done: np.ndarray) -> None:
    """
    Fit peak center using Gaussian (log-space parabolic) interpolation.
    
    Updates the center array with fractional offsets from the grid
    points, using Gaussian fitting (parabolic in log-space) in each dimension.
    This is more appropriate for Gaussian-shaped peaks.
    
    Args:
        ndim: Number of dimensions
        center: Output array for fractional offsets (modified in place)
        y: Peak intensity at center
        ym: Intensities at position-1 in each dimension
        yp: Intensities at position+1 in each dimension
        dim_done: Boolean array indicating which dimensions to use
        
    Note:
        center[i] will be set to the fractional offset (typically -0.5 to 0.5)
        for dimensions where dim_done[i] is True, and 0 otherwise.
        Uses logarithmic fitting which is better for Gaussian line shapes.
    """
    for i in range(ndim):
        if dim_done[i]:
            c, b = _fit_center3(ym[i], y, yp[i], use_log=True)
            center[i] = c
        else:
            center[i] = 0.0
