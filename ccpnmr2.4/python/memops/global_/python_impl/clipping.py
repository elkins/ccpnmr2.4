"""
Line and polyline clipping for window rendering.

Implements Cohen-Sutherland line clipping algorithm to efficiently render
only the visible portions of lines and polylines within a rectangular region.
"""

from typing import Callable, Dict, Any, Optional, Tuple
from enum import IntEnum
import numpy as np


class PolylineDrawn(IntEnum):
    """Polyline visibility status."""
    ALL_DRAWN = 0
    NONE_DRAWN = 1
    SOME_DRAWN = 2


def _polyline_drawn(vertices: np.ndarray, closed: bool,
                   xmin: float, ymin: float, 
                   xmax: float, ymax: float) -> PolylineDrawn:
    """
    Determine if polyline is fully visible, fully invisible, or partially visible.
    
    Uses conservative early rejection tests:
    - If all vertices in region → ALL_DRAWN
    - If all vertices on same side outside region → NONE_DRAWN
    - Otherwise → SOME_DRAWN (need detailed clipping)
    
    Args:
        vertices: Nx2 array of (x, y) coordinates
        closed: Whether polyline forms closed shape
        xmin, ymin: Minimum corner of clipping rectangle
        xmax, ymax: Maximum corner of clipping rectangle
        
    Returns:
        Polyline visibility status
    """
    n = len(vertices)
    if n == 0:
        return PolylineDrawn.NONE_DRAWN
    
    # Track whether any vertices violate each boundary
    xlow = True   # All vertices below xmin?
    xhigh = True  # All vertices above xmax?
    xmid = True   # All vertices between xmin and xmax?
    
    ylow = True   # All vertices below ymin?
    yhigh = True  # All vertices above ymax?
    ymid = True   # All vertices between ymin and ymax?
    
    for i in range(n):
        x, y = vertices[i]
        
        # X boundary tests
        if x > xmin:
            xlow = False
        if x < xmax:
            xhigh = False
        if x < xmin or x > xmax:
            xmid = False
            
        # Y boundary tests
        if y > ymin:
            ylow = False
        if y < ymax:
            yhigh = False
        if y < ymin or y > ymax:
            ymid = False
    
    # All vertices inside clipping region
    if xmid and ymid:
        return PolylineDrawn.ALL_DRAWN
    
    # All vertices on same side outside region
    if xhigh or xlow or yhigh or ylow:
        return PolylineDrawn.NONE_DRAWN
    
    # Some vertices might be visible, need detailed clipping
    return PolylineDrawn.SOME_DRAWN


def draw_clipped_line(x0: float, y0: float, x1: float, y1: float,
                     drawing_funcs: Dict[str, Callable], data: Any,
                     xmin: float, ymin: float, 
                     xmax: float, ymax: float) -> None:
    """
    Draw line segment clipped to rectangular region.
    
    Implements Cohen-Sutherland line clipping algorithm:
    1. Quick rejection if line entirely outside region
    2. Quick acceptance if line entirely inside region
    3. Clip line endpoints to region boundaries for partial overlap
    
    The algorithm computes intersection points with the four region boundaries
    and selects the appropriate segment to draw.
    
    Args:
        x0, y0: First endpoint of line
        x1, y1: Second endpoint of line
        drawing_funcs: Dictionary of drawing callbacks
        data: User data for callbacks
        xmin, ymin: Minimum corner of clipping rectangle
        xmax, ymax: Maximum corner of clipping rectangle
    """
    xclipped = True
    yclipped = True
    
    # Quick rejection tests for X
    if x0 < x1:
        # Line goes left to right
        if x1 < xmin or x0 > xmax:
            return  # Completely outside
        if xmin < x0 and x1 < xmax:
            xclipped = False  # Completely inside in X
    else:
        # Line goes right to left
        if x0 < xmin or x1 > xmax:
            return  # Completely outside
        if xmin < x1 and x0 < xmax:
            xclipped = False  # Completely inside in X
    
    # Quick rejection tests for Y
    if y0 < y1:
        # Line goes bottom to top
        if y1 < ymin or y0 > ymax:
            return  # Completely outside
        if ymin < y0 and y1 < ymax:
            yclipped = False  # Completely inside in Y
    else:
        # Line goes top to bottom
        if y0 < ymin or y1 > ymax:
            return  # Completely outside
        if ymin < y1 and y0 < ymax:
            yclipped = False  # Completely inside in Y
    
    # If not clipped in either dimension, draw original line
    if not xclipped and not yclipped:
        draw_line = drawing_funcs.get('draw_line')
        if draw_line:
            draw_line(data, x0, y0, x1, y1)
        return
    
    # Need to clip - find intersection points with region boundaries
    xends = []
    yends = []
    
    # Avoid division by zero
    if abs(x0 - x1) > 1e-10:
        # Intersections with vertical boundaries (x = xmin, x = xmax)
        # Using parametric line equation: y = y0 + t*(y1-y0) where t = (x-x0)/(x1-x0)
        # At x = xmin: y = (xmin-x1)*y0/(x0-x1) + (x0-xmin)*y1/(x0-x1)
        d0 = (xmin - x1) * y0 / (x0 - x1) + (x0 - xmin) * y1 / (x0 - x1)
        if ymin < d0 < ymax:
            xends.append(xmin)
            yends.append(d0)
        
        d1 = (xmax - x1) * y0 / (x0 - x1) + (x0 - xmax) * y1 / (x0 - x1)
        if ymin < d1 < ymax:
            xends.append(xmax)
            yends.append(d1)
    
    if abs(y0 - y1) > 1e-10:
        # Intersections with horizontal boundaries (y = ymin, y = ymax)
        # At y = ymin: x = (ymin-y1)*x0/(y0-y1) + (y0-ymin)*x1/(y0-y1)
        c0 = (ymin - y1) * x0 / (y0 - y1) + (y0 - ymin) * x1 / (y0 - y1)
        if xmin < c0 < xmax:
            xends.append(c0)
            yends.append(ymin)
        
        c1 = (ymax - y1) * x0 / (y0 - y1) + (y0 - ymax) * x1 / (y0 - y1)
        if xmin < c1 < xmax:
            xends.append(c1)
            yends.append(ymax)
    
    # Should have exactly 2 intersection points
    if len(xends) != 2:
        return
    
    # Add original endpoints
    xends.extend([x0, x1])
    yends.extend([y0, y1])
    
    # Find the middle two points when sorted by (x, y)
    # These define the visible line segment
    # Sort all 4 points by x coordinate (then by y for ties)
    indices = list(range(4))
    indices.sort(key=lambda i: (xends[i], yends[i]))
    
    # The middle two indices (1 and 2 after sorting) define the clipped segment
    ind0 = indices[1]
    ind1 = indices[2]
    
    # Draw the clipped line segment
    draw_line = drawing_funcs.get('draw_line')
    if draw_line:
        draw_line(data, xends[ind0], yends[ind0], xends[ind1], yends[ind1])


def draw_clipped_polyline(vertices: np.ndarray, closed: bool,
                         drawing_funcs: Dict[str, Callable], data: Any,
                         xmin: float, ymin: float, 
                         xmax: float, ymax: float) -> None:
    """
    Draw polyline clipped to rectangular region.
    
    Strategy:
    1. Check if entire polyline is visible (draw as-is)
    2. Check if entire polyline is invisible (skip)
    3. Otherwise, clip each line segment individually
    
    Args:
        vertices: Nx2 array of (x, y) coordinates
        closed: Whether to connect last point back to first
        drawing_funcs: Dictionary of drawing callbacks
        data: User data for callbacks
        xmin, ymin: Minimum corner of clipping rectangle
        xmax, ymax: Maximum corner of clipping rectangle
    """
    drawn = _polyline_drawn(vertices, closed, xmin, ymin, xmax, ymax)
    
    if drawn == PolylineDrawn.ALL_DRAWN:
        # Entire polyline visible - draw as-is
        draw_polyline = drawing_funcs.get('draw_polyline')
        if draw_polyline:
            draw_polyline(data, vertices, closed)
    
    elif drawn == PolylineDrawn.SOME_DRAWN:
        # Some segments may be visible - clip each segment
        draw_clipped_line_func = drawing_funcs.get('draw_clipped_line')
        if not draw_clipped_line_func:
            return
            
        n = len(vertices)
        
        # Draw all segments
        for i in range(n - 1):
            x0, y0 = vertices[i]
            x1, y1 = vertices[i + 1]
            draw_clipped_line_func(data, x0, y0, x1, y1)
        
        # Close the polyline if requested
        if closed and n > 0:
            x0, y0 = vertices[n - 1]
            x1, y1 = vertices[0]
            draw_clipped_line_func(data, x0, y0, x1, y1)
    
    # If NONE_DRAWN, do nothing


# Mock polyline class for testing
class Polyline:
    """Simple polyline structure."""
    def __init__(self, vertices: np.ndarray, closed: bool = False):
        self.vertices = vertices
        self.closed = closed
        self.nvertices = len(vertices)


def draw_clipped_polyline_capi(polyline: Polyline,
                              drawing_funcs: Dict[str, Callable], data: Any,
                              xmin: float, ymin: float,
                              xmax: float, ymax: float) -> None:
    """
    C API compatibility wrapper for draw_clipped_polyline.
    
    Takes a Polyline object instead of raw vertices array.
    
    Args:
        polyline: Polyline object with vertices and closed attributes
        drawing_funcs: Dictionary of drawing callbacks
        data: User data for callbacks
        xmin, ymin: Minimum corner of clipping rectangle
        xmax, ymax: Maximum corner of clipping rectangle
    """
    draw_clipped_polyline(polyline.vertices, polyline.closed,
                        drawing_funcs, data,
                        xmin, ymin, xmax, ymax)
