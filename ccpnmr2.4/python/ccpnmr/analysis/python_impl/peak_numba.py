"""
Numba-accelerated peak implementation for NMR spectroscopy.

This version uses numba for numerical operations like region checking
and aliasing calculations which can benefit from JIT compilation.
"""

from typing import Optional, List

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
    NUMBA_AVAILABLE = False

# Constants
MAX_NDIM = 16


# Numba-accelerated region checking
@jit(nopython=True)
def _check_in_region(pos: float, low: float, high: float,
                     num_alias: int, npoints: int, allow_alias: bool) -> bool:
    """Check if position is in region, considering aliasing (numba-optimized)."""
    # Check direct position
    if low <= pos <= high:
        return True
    
    # Check aliased positions if allowed
    if allow_alias and npoints > 0:
        aliased_pos = pos + num_alias * npoints
        if low <= aliased_pos <= high:
            return True
    
    return False


@jit(nopython=True)
def _calculate_scaled_position(pos: float, scale: float, offset: float) -> float:
    """Calculate scaled position (numba-optimized)."""
    return pos * scale + offset


class Peak:
    """
    NMR spectral peak with numba-accelerated numerical operations.
    """
    
    def __init__(self, ndim: int):
        if ndim < 1 or ndim > MAX_NDIM:
            raise ValueError(f"ndim must be between 1 and {MAX_NDIM}")
        
        self.ndim = ndim
        self.position = [0.0] * ndim
        self.text_offset = [0.0] * ndim
        self.num_aliasing = [0] * ndim
        self.line_width = [0.0] * ndim
        
        self.intensity = 0.0
        self.volume = 0.0
        self.is_selected = False
        self.text = ""
        self.text_color = None
    
    def __repr__(self) -> str:
        return (f"Peak(ndim={self.ndim}, pos={self.position}, "
                f"intensity={self.intensity:.2f}, selected={self.is_selected})")


# C-style API functions
def new_peak(ndim: int) -> Peak:
    """Create a new peak."""
    return Peak(ndim)


def delete_peak(peak: Peak) -> None:
    """Delete peak (cleanup)."""
    pass


def get_selected_peak(peak: Peak) -> bool:
    """Get peak selection state."""
    return peak.is_selected


def set_selected_peak(peak: Peak, is_selected: bool) -> None:
    """Set peak selection state."""
    peak.is_selected = is_selected


def get_text_peak(peak: Peak) -> str:
    """Get peak text label."""
    return peak.text


def set_text_peak(peak: Peak, text: Optional[str], color: Optional[List[float]]) -> bool:
    """Set peak text label and optional color."""
    if text is None:
        peak.text = ""
    else:
        peak.text = text
    
    if color is None:
        peak.text_color = None
    else:
        peak.text_color = list(color)
    
    return True


def set_position_peak(peak: Peak, position: List[float]) -> bool:
    """Set peak position."""
    if len(position) != peak.ndim:
        return False
    peak.position = list(position)
    return True


def set_intensity_peak(peak: Peak, intensity: float) -> None:
    """Set peak intensity."""
    peak.intensity = intensity


def set_volume_peak(peak: Peak, volume: float) -> None:
    """Set peak volume."""
    peak.volume = volume


def set_num_aliasing_peak(peak: Peak, dim: int, num_aliasing: int) -> bool:
    """Set number of aliasing folds for dimension."""
    if dim < 0 or dim >= peak.ndim:
        return False
    peak.num_aliasing[dim] = num_aliasing
    return True


def set_line_width_peak(peak: Peak, dim: int, line_width: float) -> bool:
    """Set line width for dimension."""
    if dim < 0 or dim >= peak.ndim:
        return False
    peak.line_width[dim] = line_width
    return True


def set_text_offset_peak(peak: Peak, dim: int, offset: float) -> bool:
    """Set text label offset for dimension."""
    if dim < 0 or dim >= peak.ndim:
        return False
    peak.text_offset[dim] = offset
    return True


def is_in_region_peak(peak: Peak, region_low: List[float], region_high: List[float],
                      npoints: List[int], allow_aliasing: bool) -> bool:
    """
    Check if peak is in specified region (numba-accelerated).
    
    Args:
        peak: The peak to check
        region_low: Lower bounds for each dimension
        region_high: Upper bounds for each dimension
        npoints: Number of points per dimension (for aliasing)
        allow_aliasing: Whether to consider aliased positions
    
    Returns:
        True if peak is in region
    """
    if len(region_low) != peak.ndim or len(region_high) != peak.ndim:
        return False
    
    if len(npoints) != peak.ndim:
        return False
    
    # Check each dimension
    for dim in range(peak.ndim):
        pos = peak.position[dim]
        low = region_low[dim]
        high = region_high[dim]
        num_alias = peak.num_aliasing[dim]
        npts = npoints[dim]
        
        if not _check_in_region(pos, low, high, num_alias, npts, allow_aliasing):
            return False
    
    return True


def get_scaled_region_peak(peak: Peak, scale: List[float], offset: List[float],
                           region: List[float]) -> bool:
    """
    Calculate scaled region around peak (numba-accelerated).
    
    Args:
        peak: The peak
        scale: Scale factors per dimension
        offset: Offset values per dimension
        region: Output array [x0_low, x0_high, x1_low, x1_high, ...]
    
    Returns:
        True on success
    """
    if len(scale) != peak.ndim or len(offset) != peak.ndim:
        return False
    
    if len(region) != 2 * peak.ndim:
        return False
    
    for dim in range(peak.ndim):
        pos = peak.position[dim]
        lw = peak.line_width[dim]
        
        # Calculate scaled bounds
        low = _calculate_scaled_position(pos - lw, scale[dim], offset[dim])
        high = _calculate_scaled_position(pos + lw, scale[dim], offset[dim])
        
        region[2 * dim] = low
        region[2 * dim + 1] = high
    
    return True


def fit_volume_peak(peak: Peak, block_file) -> bool:
    """
    Fit peak volume (stub - requires block_file infrastructure).
    
    The C implementation:
    - Reads data from block_file around peak position
    - Integrates signal within line_width bounds
    - Updates peak.volume
    """
    raise NotImplementedError("fit_volume_peak requires block_file infrastructure")


def fit_center_peak(peak: Peak, block_file) -> bool:
    """
    Fit peak center (stub - requires block_file infrastructure).
    
    The C implementation:
    - Reads data from block_file
    - Calculates center of mass or parabolic fit
    - Updates peak.position
    """
    raise NotImplementedError("fit_center_peak requires block_file infrastructure")


def fit_linewidth_peak(peak: Peak, block_file) -> bool:
    """
    Fit peak linewidth (stub - requires block_file infrastructure).
    
    The C implementation:
    - Reads data from block_file
    - Calculates FWHM or similar width measure
    - Updates peak.line_width
    """
    raise NotImplementedError("fit_linewidth_peak requires block_file infrastructure")


def draw_peak(peak: Peak, x_screen: List[float], y_screen: List[float],
              color: List[float]) -> None:
    """
    Draw peak (stub - requires drawing_funcs infrastructure).
    
    The C implementation:
    - Draws crosshair or marker at peak position
    - Draws text label with offset
    - Uses peak color or default
    - Highlights if selected
    """
    raise NotImplementedError("draw_peak requires drawing_funcs infrastructure")
