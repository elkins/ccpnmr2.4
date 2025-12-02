"""
Window Peak List Rendering

Python implementation of win_peak_list.c for rendering NMR peak lists in spectrum windows.

Manages peak display in spectrum windows with:
- Symbol drawing (with aliasing indication)
- Text labels (peak annotations)
- Text pointers (lines from symbols to labels)
- Depth cueing (3D visualization)
- Intensity/volume-based scaling
- Selection highlighting

Original C implementation: ccpnmr2.4/c/ccpnmr/analysis/win_peak_list.c (258 lines)
"""

import numpy as np
from typing import Any, Dict, Optional, Callable


# Drawing method constants (matching C definitions)
DRAW_UNIFORM_METHOD = 0      # All peaks same size
DRAW_GLOBAL_METHOD = 1       # Scale by global max
DRAW_PEAKLIST_METHOD = 2     # Scale by peak list max
DRAW_LINE_WIDTH_METHOD = 3   # Scale by line width
NDRAW_METHODS = 4

# Number of color components (RGB)
NCOLORS = 3


class WinPeakList:
    """
    Peak list configured for window rendering.
    
    Wraps a PeakList with display settings for rendering in a spectrum window.
    Controls symbol, text, and pointer visibility.
    
    Attributes:
        peak_list: The underlying PeakList to render
        hasValueAxis: True if rendering 1D with value (intensity) axis
        isSymbolDrawn: Whether to draw peak symbols
        isTextDrawn: Whether to draw peak text labels
        isTextPointerDrawn: Whether to draw lines from symbols to text
    """
    
    def __init__(self, peak_list, hasValueAxis: bool = False):
        """
        Create window peak list wrapper.
        
        Args:
            peak_list: PeakList instance to render
            hasValueAxis: True for 1D spectrum with intensity axis
        """
        self.peak_list = peak_list  # Does not own peak_list
        self.hasValueAxis = hasValueAxis
        self.isSymbolDrawn = True
        self.isTextDrawn = True
        self.isTextPointerDrawn = True
        
    def set_symbol_drawn(self, isSymbolDrawn: bool) -> None:
        """Set whether symbols are drawn."""
        self.isSymbolDrawn = isSymbolDrawn
        
    def set_text_drawn(self, isTextDrawn: bool) -> None:
        """Set whether text labels are drawn."""
        self.isTextDrawn = isTextDrawn
        
    def set_text_pointer_drawn(self, isTextPointerDrawn: bool) -> None:
        """Set whether text pointers are drawn."""
        self.isTextPointerDrawn = isTextPointerDrawn


def _is_peak_drawn(ndim: int, peak, first: np.ndarray, last: np.ndarray) -> bool:
    """
    Check if peak is within the visible region.
    
    Args:
        ndim: Number of dimensions
        peak: Peak instance to check
        first: First point of region in each dimension
        last: Last point of region in each dimension
        
    Returns:
        True if peak should be drawn
    """
    if peak.position is None:
        return False
        
    for i in range(ndim):
        p = peak.position[i] - 1  # Convert to 0-based
        if p < first[i] or p >= last[i]:
            return False
            
    return True


def _invert_color(color: np.ndarray) -> np.ndarray:
    """
    Invert RGB color.
    
    Args:
        color: RGB color array [r, g, b]
        
    Returns:
        Inverted color [1-r, 1-g, 1-b]
    """
    return 1.0 - color


def _depth_cue_peak(peak, xdim: int, ydim: int,
                   npoints: np.ndarray, center: np.ndarray, 
                   thickness: np.ndarray, tile: np.ndarray,
                   fg_color: np.ndarray, bg_color: np.ndarray,
                   drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Apply depth cueing to peak color based on position in 3D.
    
    Peaks further from the center plane are faded toward the background color
    to create a 3D depth effect.
    
    Args:
        peak: Peak instance
        xdim: X dimension index
        ydim: Y dimension index
        npoints: Number of points in each dimension
        center: Center position in each dimension
        thickness: Depth thickness in each dimension (0 for pseudo-3D)
        tile: Tile indices for aliasing
        fg_color: Foreground (peak) color
        bg_color: Background color
        drawing_funcs: Drawing function callbacks
        data: User data for callbacks
    """
    s = 1.0
    
    # Calculate depth factor for non-displayed dimensions
    for i in range(peak.ndim):
        if i != xdim and i != ydim and thickness[i] > 0:
            p = peak.position[i] + tile[i] * npoints[i]
            distance = abs(p - center[i])
            s *= 1.0 - min(1.0, distance / thickness[i])
    
    # s = 1 at center, 0 at edge
    # Invert so s = 0 at center, 1 at edge
    s = 1.0 - s
    s *= 0.5  # Scale to 0-0.5 range
    
    # Blend foreground and background colors
    color = (1 - s) * fg_color + s * bg_color
    
    set_draw_color = drawing_funcs.get('set_draw_color')
    if set_draw_color:
        set_draw_color(data, color)


def draw_win_peak_list(win_peak_list: WinPeakList,
                       xdim: int, ydim: int,
                       xpix: float, ypix: float,
                       xscale: float, yscale: float,
                       first: np.ndarray, last: np.ndarray,
                       draw_method: int,
                       intensity_max: float, volume_max: float,
                       bg_color: np.ndarray,
                       center: np.ndarray, thickness: np.ndarray, tile: np.ndarray,
                       drawing_funcs: Dict[str, Callable], data: Any) -> bool:
    """
    Draw all peaks in window peak list.
    
    Args:
        win_peak_list: Window peak list to render
        xdim: X dimension index
        ydim: Y dimension index  
        xpix: Pixel size in x
        ypix: Pixel size in y
        xscale: Scale factor for x
        yscale: Scale factor for y
        first: First point of region in each dimension
        last: Last point of region in each dimension
        draw_method: Drawing method (uniform, global, peaklist, linewidth)
        intensity_max: Maximum intensity for scaling
        volume_max: Maximum volume for scaling
        bg_color: Background color [r, g, b]
        center: Center position for depth cueing
        thickness: Depth thickness for depth cueing
        tile: Tile indices for aliasing
        drawing_funcs: Drawing function callbacks dictionary
        data: User data passed to callbacks
        
    Returns:
        True on success
        
    Note:
        Drawing functions should include:
        - set_draw_color(data, color)
        - draw methods from peak.draw_peak()
    """
    peak_list = win_peak_list.peak_list
    
    # Nothing to draw if both disabled
    if not win_peak_list.isSymbolDrawn and not win_peak_list.isTextDrawn:
        return True
        
    # Nothing to draw if empty
    if not hasattr(peak_list, 'peaks') or len(peak_list.peaks) == 0:
        return True
    
    # Invert background color for selection highlighting
    inverted_bg_color = _invert_color(bg_color)
    
    # Determine max values if using peak list method
    if draw_method == DRAW_PEAKLIST_METHOD:
        if hasattr(peak_list, 'determine_max'):
            intensity_max, volume_max = peak_list.determine_max()
    
    # Set initial color
    set_draw_color = drawing_funcs.get('set_draw_color')
    if set_draw_color and hasattr(peak_list, 'color'):
        set_draw_color(data, peak_list.color)
    
    # Draw each peak
    for peak in peak_list.peaks:
        if not _is_peak_drawn(peak_list.ndim, peak, first, last):
            continue
            
        # Determine foreground color (inverted for selected peaks with value axis)
        if win_peak_list.hasValueAxis and hasattr(peak, 'isSelected') and peak.isSelected:
            fg_color = inverted_bg_color
        else:
            fg_color = peak_list.color if hasattr(peak_list, 'color') else np.array([0.0, 0.0, 0.0])
        
        # Calculate scaling
        xsc = xscale
        ysc = yscale
        
        if draw_method == DRAW_LINE_WIDTH_METHOD:
            # Scale by line width
            if hasattr(peak, 'line_width'):
                xsc = xscale * peak.line_width[xdim]
                ysc = yscale * peak.line_width[ydim]
        elif draw_method != DRAW_UNIFORM_METHOD:
            # Scale by intensity/volume
            if hasattr(peak_list, 'determine_peak_scale'):
                scale = peak_list.determine_peak_scale(peak, intensity_max, volume_max)
                xsc = scale * xscale
                ysc = scale * yscale
        
        # Apply color (depth cue for non-value axis, direct for value axis)
        if win_peak_list.hasValueAxis:
            if set_draw_color:
                set_draw_color(data, fg_color)
        else:
            _depth_cue_peak(peak, xdim, ydim,
                          peak_list.npoints if hasattr(peak_list, 'npoints') else np.zeros(peak_list.ndim, dtype=int),
                          center, thickness, tile,
                          fg_color, bg_color, drawing_funcs, data)
        
        # Draw the peak
        if hasattr(peak, 'draw'):
            peak.draw(xdim, ydim, first, last,
                     xpix, ypix, xsc, ysc,
                     peak_list.symbol if hasattr(peak_list, 'symbol') else 0,
                     win_peak_list.isSymbolDrawn,
                     win_peak_list.isTextDrawn,
                     win_peak_list.isTextPointerDrawn,
                     win_peak_list.hasValueAxis,
                     tile, drawing_funcs, data)
    
    return True


# C API compatibility functions
def new_win_peak_list(peak_list, hasValueAxis: bool = False) -> WinPeakList:
    """
    Create new window peak list (C API compatible).
    
    Args:
        peak_list: PeakList to wrap
        hasValueAxis: True for 1D with intensity axis
        
    Returns:
        New WinPeakList instance
    """
    return WinPeakList(peak_list, hasValueAxis)


def delete_win_peak_list(win_peak_list: WinPeakList) -> None:
    """
    Delete window peak list (C API compatible).
    
    Args:
        win_peak_list: Instance to delete
        
    Note:
        Python handles memory management automatically.
    """
    pass


def is_symbol_drawn_win_peak_list(win_peak_list: WinPeakList, 
                                  isSymbolDrawn: bool) -> None:
    """
    Set symbol drawing flag (C API compatible).
    
    Args:
        win_peak_list: Instance to modify
        isSymbolDrawn: Whether to draw symbols
    """
    win_peak_list.set_symbol_drawn(isSymbolDrawn)


def is_text_drawn_win_peak_list(win_peak_list: WinPeakList,
                                isTextDrawn: bool) -> None:
    """
    Set text drawing flag (C API compatible).
    
    Args:
        win_peak_list: Instance to modify
        isTextDrawn: Whether to draw text
    """
    win_peak_list.set_text_drawn(isTextDrawn)


def is_text_pointer_drawn_win_peak_list(win_peak_list: WinPeakList,
                                        isTextPointerDrawn: bool) -> None:
    """
    Set text pointer drawing flag (C API compatible).
    
    Args:
        win_peak_list: Instance to modify
        isTextPointerDrawn: Whether to draw pointers
    """
    win_peak_list.set_text_pointer_drawn(isTextPointerDrawn)
