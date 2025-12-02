"""
Peak Symbol Drawing

Python implementation of symbol.c for drawing NMR peak symbols.

Provides five symbol types for marking peak positions in NMR spectra:
- CROSS: Diagonal X symbol
- PLUS: Vertical and horizontal + symbol  
- CIRCLE: Hollow ellipse
- DISK: Filled ellipse
- BOX: Hollow rectangle

Symbols can be drawn with aliasing (dashed lines) to indicate peaks
that wrap around due to spectral aliasing.

Original C implementation: ccpnmr2.4/c/ccpnmr/analysis/symbol.c (120 lines)
"""

from enum import IntEnum
from typing import Any, Dict, Callable, Optional


# Symbol type constants (matching C definitions)
class SymbolType(IntEnum):
    """Peak symbol types for spectrum display."""
    CROSS = 0   # Diagonal X
    PLUS = 1    # Vertical/horizontal +
    CIRCLE = 2  # Hollow ellipse
    DISK = 3    # Filled ellipse
    BOX = 4     # Hollow rectangle


# Default symbol
DEFAULT_SYMBOL = SymbolType.CROSS

# Line style constants
NORMAL_LINE_STYLE = 0
DASHED_LINE_STYLE = 1


def draw_cross(x: float, y: float, xscale: float, yscale: float,
               drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Draw a cross (X) symbol.
    
    Args:
        x: Center x coordinate
        y: Center y coordinate
        xscale: Horizontal scale factor
        yscale: Vertical scale factor
        drawing_funcs: Dictionary of drawing callback functions
        data: User data passed to callbacks
    """
    r = 1.0
    dx = r * xscale
    dy = r * yscale
    
    draw_line = drawing_funcs.get('draw_line')
    if draw_line:
        # Diagonal lines forming X
        draw_line(data, x - dx, y - dy, x + dx, y + dy)
        draw_line(data, x - dx, y + dy, x + dx, y - dy)


def draw_plus(x: float, y: float, xscale: float, yscale: float,
              drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Draw a plus (+) symbol.
    
    Args:
        x: Center x coordinate
        y: Center y coordinate
        xscale: Horizontal scale factor
        yscale: Vertical scale factor
        drawing_funcs: Dictionary of drawing callback functions
        data: User data passed to callbacks
    """
    r = 1.0
    dx = r * xscale
    dy = r * yscale
    
    draw_line = drawing_funcs.get('draw_line')
    if draw_line:
        # Vertical and horizontal lines forming +
        draw_line(data, x, y - dy, x, y + dy)      # Vertical
        draw_line(data, x - dx, y, x + dx, y)      # Horizontal


def draw_circle(x: float, y: float, xscale: float, yscale: float,
                drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Draw a hollow circle/ellipse symbol.
    
    Args:
        x: Center x coordinate
        y: Center y coordinate
        xscale: Horizontal scale factor
        yscale: Vertical scale factor
        drawing_funcs: Dictionary of drawing callback functions
        data: User data passed to callbacks
    """
    r = 1.0
    dx = r * xscale
    dy = r * yscale
    
    # Use ellipse for anisotropic scaling
    draw_ellipse = drawing_funcs.get('draw_ellipse')
    if draw_ellipse:
        draw_ellipse(data, x, y, dx, dy)


def draw_disk(x: float, y: float, xscale: float, yscale: float,
              drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Draw a filled disk/ellipse symbol.
    
    Args:
        x: Center x coordinate
        y: Center y coordinate
        xscale: Horizontal scale factor
        yscale: Vertical scale factor
        drawing_funcs: Dictionary of drawing callback functions
        data: User data passed to callbacks
    """
    r = 1.0
    dx = r * xscale
    dy = r * yscale
    
    # Use filled ellipse for anisotropic scaling
    fill_ellipse = drawing_funcs.get('fill_ellipse')
    if fill_ellipse:
        fill_ellipse(data, x, y, dx, dy)


def draw_box(x: float, y: float, xscale: float, yscale: float,
             drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Draw a hollow box/rectangle symbol.
    
    Args:
        x: Center x coordinate
        y: Center y coordinate
        xscale: Horizontal scale factor
        yscale: Vertical scale factor
        drawing_funcs: Dictionary of drawing callback functions
        data: User data passed to callbacks
    """
    r = 1.0
    dx = r * xscale
    dy = r * yscale
    
    draw_line = drawing_funcs.get('draw_line')
    if draw_line:
        # Four lines forming rectangle
        draw_line(data, x - dx, y - dy, x + dx, y - dy)  # Bottom
        draw_line(data, x + dx, y - dy, x + dx, y + dy)  # Right
        draw_line(data, x + dx, y + dy, x - dx, y + dy)  # Top
        draw_line(data, x - dx, y + dy, x - dx, y - dy)  # Left


def draw_symbol(symbol: int, x: float, y: float, 
                xscale: float, yscale: float, isAliased: bool,
                drawing_funcs: Dict[str, Callable], data: Any) -> None:
    """
    Draw a peak symbol at the specified position.
    
    Args:
        symbol: Symbol type (0-4, see SymbolType)
        x: Center x coordinate
        y: Center y coordinate
        xscale: Horizontal scale factor
        yscale: Vertical scale factor
        isAliased: If True, draw with dashed line style
        drawing_funcs: Dictionary of drawing callback functions:
            - 'draw_line': Function(data, x1, y1, x2, y2)
            - 'draw_ellipse': Function(data, x, y, rx, ry)
            - 'fill_ellipse': Function(data, x, y, rx, ry)
            - 'set_line_style': Function(data, style)
        data: User data passed to all callbacks
        
    Note:
        If isAliased is True, symbols are drawn with dashed lines to
        indicate peaks that wrap around due to spectral aliasing.
    """
    # Set line style for aliased peaks
    if isAliased:
        set_line_style = drawing_funcs.get('set_line_style')
        if set_line_style:
            set_line_style(data, DASHED_LINE_STYLE)
    
    # Draw the appropriate symbol
    if symbol == SymbolType.CROSS:
        draw_cross(x, y, xscale, yscale, drawing_funcs, data)
    elif symbol == SymbolType.PLUS:
        draw_plus(x, y, xscale, yscale, drawing_funcs, data)
    elif symbol == SymbolType.CIRCLE:
        draw_circle(x, y, xscale, yscale, drawing_funcs, data)
    elif symbol == SymbolType.DISK:
        draw_disk(x, y, xscale, yscale, drawing_funcs, data)
    elif symbol == SymbolType.BOX:
        draw_box(x, y, xscale, yscale, drawing_funcs, data)
    
    # Restore normal line style
    if isAliased:
        set_line_style = drawing_funcs.get('set_line_style')
        if set_line_style:
            set_line_style(data, NORMAL_LINE_STYLE)


# Convenience constants for external use
CROSS_SYMBOL = SymbolType.CROSS
PLUS_SYMBOL = SymbolType.PLUS
CIRCLE_SYMBOL = SymbolType.CIRCLE
DISK_SYMBOL = SymbolType.DISK
BOX_SYMBOL = SymbolType.BOX
NUMBER_SYMBOLS = 5
