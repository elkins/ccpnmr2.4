"""
Pure Python implementation of peak.c

Represents NMR spectral peaks with position, intensity, volume, and metadata.
This implementation matches the C API for drop-in compatibility.
"""

from typing import List, Optional, Tuple
import copy

# Constants matching C implementation
GAUSSIAN_METHOD = 0
LORENTZIAN_METHOD = 1
NMETHODS = 2

DEFAULT_TEXT_OFFSET = -999.9


class Peak:
    """
    Represents an NMR spectral peak.
    
    Attributes:
        ndim: Number of dimensions
        position: Peak position in points (counts from 1)
        num_aliasing: Aliasing numbers for each dimension
        text: Peak label text
        isSelected: Selection state
        intensity: Peak intensity value
        volume: Peak volume (integrated intensity)
        text_offset: Text label offset from default position (points)
        value_offset: Value offset for 1D windows
        line_width: Line width in each dimension (points)
    """
    
    def __init__(self, ndim: int):
        """
        Create a new peak.
        
        Args:
            ndim: Number of dimensions
        """
        self.ndim = ndim
        self.position = [0.0] * ndim
        self.text_offset = [DEFAULT_TEXT_OFFSET] * ndim
        self.value_offset = DEFAULT_TEXT_OFFSET
        self.num_aliasing = [0] * ndim
        self.line_width = [0.0] * ndim
        self.text = ""
        self.isSelected = False
        self.intensity = 0.0
        self.volume = 0.0
    
    def get_is_selected(self) -> bool:
        """Get peak selection state."""
        return self.isSelected
    
    def set_is_selected(self, isSelected: bool):
        """Set peak selection state."""
        self.isSelected = isSelected
    
    def set_text(self, text: str) -> bool:
        """
        Set peak label text.
        
        Args:
            text: Label text
            
        Returns:
            True on success
        """
        self.text = str(text)
        return True
    
    def set_position(self, position: List[float]):
        """
        Set peak position.
        
        Args:
            position: List of coordinates (one per dimension)
        """
        if len(position) != self.ndim:
            raise ValueError(f"Position length {len(position)} doesn't match ndim {self.ndim}")
        self.position = list(position)
    
    def set_text_offset(self, dim: int, text_offset: float):
        """
        Set text label offset for a dimension.
        
        Args:
            dim: Dimension index (or -1 for value_offset)
            text_offset: Offset in points
        """
        if dim == -1:
            self.value_offset = text_offset
        elif 0 <= dim < self.ndim:
            self.text_offset[dim] = text_offset
    
    def reset_text_offset(self, dim: int):
        """
        Reset text offset to default for a dimension.
        
        Args:
            dim: Dimension index (or -1 for value_offset)
        """
        if dim == -1:
            self.value_offset = DEFAULT_TEXT_OFFSET
        elif 0 <= dim < self.ndim:
            self.text_offset[dim] = DEFAULT_TEXT_OFFSET
    
    def set_num_aliasing(self, num_aliasing: List[int]):
        """
        Set aliasing numbers.
        
        Args:
            num_aliasing: List of aliasing numbers (one per dimension)
        """
        if len(num_aliasing) != self.ndim:
            raise ValueError(f"Aliasing length {len(num_aliasing)} doesn't match ndim {self.ndim}")
        self.num_aliasing = list(num_aliasing)
    
    def set_intensity(self, intensity: float):
        """Set peak intensity."""
        self.intensity = float(intensity)
    
    def set_volume(self, volume: float):
        """Set peak volume."""
        self.volume = float(volume)
    
    def set_line_width(self, dim: int, line_width: float):
        """
        Set line width for a dimension.
        
        Args:
            dim: Dimension index
            line_width: Line width in points
        """
        if 0 <= dim < self.ndim:
            self.line_width[dim] = float(line_width)
    
    def is_in_region(self, first: List[float], last: List[float],
                     npoints: List[int], allow_aliasing: Optional[List[bool]] = None,
                     d2_array: Optional[List[float]] = None) -> bool:
        """
        Check if peak is within a specified region.
        
        Args:
            first: Starting coordinates
            last: Ending coordinates  
            npoints: Number of points in each dimension
            allow_aliasing: Whether to allow aliasing per dimension (optional)
            d2_array: Distance squared array (optional, not used in Python impl)
            
        Returns:
            True if peak is in region
        """
        if len(first) != self.ndim or len(last) != self.ndim:
            return False
        
        if allow_aliasing is None:
            allow_aliasing = [False] * self.ndim
        
        for dim in range(self.ndim):
            pos = self.position[dim]
            
            # Handle aliasing if allowed
            if allow_aliasing[dim] and npoints[dim] > 0:
                # Adjust position for aliasing
                n_alias = self.num_aliasing[dim]
                aliased_pos = pos + n_alias * npoints[dim]
                
                # Check if aliased position is in range
                if not (first[dim] <= aliased_pos <= last[dim]):
                    return False
            else:
                # Direct position check
                if not (first[dim] <= pos <= last[dim]):
                    return False
        
        return True
    
    def find_scaled_region(self, xdim: int, ydim: int, scale: float, 
                          yscale: float) -> Tuple[List[float], List[float]]:
        """
        Find scaled region around peak.
        
        Args:
            xdim: X dimension index
            ydim: Y dimension index
            scale: X scale factor
            yscale: Y scale factor
            
        Returns:
            Tuple of (first, last) coordinate lists
        """
        first = [0.0] * self.ndim
        last = [0.0] * self.ndim
        
        for dim in range(self.ndim):
            if dim == xdim:
                first[dim] = self.position[dim] - scale
                last[dim] = self.position[dim] + scale
            elif dim == ydim:
                first[dim] = self.position[dim] - yscale
                last[dim] = self.position[dim] + yscale
            else:
                first[dim] = self.position[dim]
                last[dim] = self.position[dim]
        
        return first, last
    
    def __repr__(self) -> str:
        """String representation of peak."""
        return (f"Peak(ndim={self.ndim}, pos={self.position}, "
                f"intensity={self.intensity}, volume={self.volume}, "
                f"text='{self.text}', selected={self.isSelected})")


# C-style API functions for compatibility
def new_peak(ndim: int) -> Peak:
    """Create a new peak."""
    return Peak(ndim)


def delete_peak(peak: Peak):
    """Delete a peak (Python handles memory automatically)."""
    pass  # Python garbage collection handles cleanup


def get_is_selected_peak(peak: Peak) -> bool:
    """Get peak selection state."""
    return peak.get_is_selected()


def set_is_selected_peak(peak: Peak, isSelected: bool):
    """Set peak selection state."""
    peak.set_is_selected(isSelected)


def set_text_peak(peak: Peak, text: str, error_msg: Optional[str] = None) -> bool:
    """Set peak label text."""
    return peak.set_text(text)


def set_position_peak(peak: Peak, position: List[float]):
    """Set peak position."""
    peak.set_position(position)


def set_text_offset_peak(peak: Peak, dim: int, text_offset: float):
    """Set text label offset."""
    peak.set_text_offset(dim, text_offset)


def reset_text_offset_peak(peak: Peak, dim: int):
    """Reset text offset to default."""
    peak.reset_text_offset(dim)


def set_num_aliasing_peak(peak: Peak, num_aliasing: List[int]):
    """Set aliasing numbers."""
    peak.set_num_aliasing(num_aliasing)


def set_intensity_peak(peak: Peak, intensity: float):
    """Set peak intensity."""
    peak.set_intensity(intensity)


def set_volume_peak(peak: Peak, volume: float):
    """Set peak volume."""
    peak.set_volume(volume)


def set_line_width_peak(peak: Peak, dim: int, line_width: float):
    """Set line width for a dimension."""
    peak.set_line_width(dim, line_width)


def is_in_region_peak(peak: Peak, first: List[float], last: List[float],
                      npoints: List[int], allow_aliasing: Optional[List[bool]] = None,
                      d2_array: Optional[List[float]] = None) -> bool:
    """Check if peak is in region."""
    return peak.is_in_region(first, last, npoints, allow_aliasing, d2_array)


def find_scaled_region_peak(peak: Peak, xdim: int, ydim: int, scale: float,
                            yscale: float) -> Tuple[List[float], List[float]]:
    """Find scaled region around peak."""
    return peak.find_scaled_region(xdim, ydim, scale, yscale)


# Note: Some C functions like draw_peak, get_intensity_peak, fit_volume_peak,
# fit_center_peak, and fit_linewidth_peak require Block_file and Drawing_funcs
# dependencies. Those would need to be implemented separately with their
# respective modules. These stubs are provided for API compatibility:

def draw_peak(peak: Peak, *args, **kwargs):
    """Draw peak (requires drawing infrastructure - stub for now)."""
    raise NotImplementedError("draw_peak requires drawing infrastructure")


def get_intensity_peak(peak: Peak, block_file, error_msg: Optional[str] = None) -> Tuple[bool, float]:
    """Get peak intensity from block file (requires block_file - stub for now)."""
    raise NotImplementedError("get_intensity_peak requires block_file implementation")


def fit_volume_peak(peak: Peak, method: int, block_file, dim_done: List[bool],
                   error_msg: Optional[str] = None) -> Tuple[bool, float, bool]:
    """Fit peak volume (requires block_file - stub for now)."""
    raise NotImplementedError("fit_volume_peak requires block_file implementation")


def fit_center_peak(peak: Peak, method: int, block_file, dim_done: List[bool],
                   error_msg: Optional[str] = None) -> Tuple[bool, List[float], bool]:
    """Fit peak center (requires block_file - stub for now)."""
    raise NotImplementedError("fit_center_peak requires block_file implementation")


def fit_linewidth_peak(peak: Peak, block_file, dim_done: List[bool],
                      error_msg: Optional[str] = None) -> Tuple[bool, List[float]]:
    """Fit peak linewidth (requires block_file - stub for now)."""
    raise NotImplementedError("fit_linewidth_peak requires block_file implementation")


def fit_peaks_in_region(npeaks: int, peaks: List[Peak], method: int,
                       first: List[int], last: List[int], block_file,
                       dim_done: List[bool], params: List[float],
                       params_dev: List[float], error_msg: Optional[str] = None) -> bool:
    """Fit multiple peaks in region (requires block_file - stub for now)."""
    raise NotImplementedError("fit_peaks_in_region requires block_file implementation")


# Export public API
__all__ = [
    'Peak',
    'GAUSSIAN_METHOD',
    'LORENTZIAN_METHOD',
    'NMETHODS',
    'new_peak',
    'delete_peak',
    'get_is_selected_peak',
    'set_is_selected_peak',
    'set_text_peak',
    'set_position_peak',
    'set_text_offset_peak',
    'reset_text_offset_peak',
    'set_num_aliasing_peak',
    'set_intensity_peak',
    'set_volume_peak',
    'set_line_width_peak',
    'is_in_region_peak',
    'find_scaled_region_peak',
    # Stubs for functions requiring additional infrastructure:
    'draw_peak',
    'get_intensity_peak',
    'fit_volume_peak',
    'fit_center_peak',
    'fit_linewidth_peak',
    'fit_peaks_in_region',
]
