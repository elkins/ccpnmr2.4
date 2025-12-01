# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""
Cython-optimized contour tracing implementation.

NOTE: This is a simplified standalone implementation created for performance
comparison purposes (Python vs Numba vs Cython). It is NOT a wrapper around
the existing C implementation at ccpnmr2.4/c/ccpnmr/analysis/contour_file.c.

See contour.py for rationale on why a simplified implementation was created
instead of wrapping the existing C code.

Uses Cython's static typing and C-level performance for:
- Marching squares contour tracing
- Edge interpolation
- Distance calculations
"""

from libc.math cimport sqrt, fabs
from typing import List, Tuple

cdef double interpolate_edge_c(double v1, double v2, double level) nogil:
    """Linear interpolation (C-optimized)."""
    if fabs(v2 - v1) < 1e-10:
        return 0.5
    return (level - v1) / (v2 - v1)


cdef int get_case_index_c(double v00, double v10, double v11, double v01, double level) nogil:
    """Determine marching squares case (C-optimized)."""
    cdef int case_idx = 0
    if v00 >= level:
        case_idx |= 1
    if v10 >= level:
        case_idx |= 2
    if v11 >= level:
        case_idx |= 4
    if v01 >= level:
        case_idx |= 8
    return case_idx


cdef void get_edge_coords_c(int x, int y, int edge, double t, double* px, double* py) nogil:
    """Get edge coordinates (C-optimized)."""
    if edge == 0:  # Bottom
        px[0] = x + t
        py[0] = y
    elif edge == 1:  # Right
        px[0] = x + 1
        py[0] = y + t
    elif edge == 2:  # Top
        px[0] = x + t
        py[0] = y + 1
    else:  # Left (edge == 3)
        px[0] = x
        py[0] = y + t


cdef double distance_squared_c(double x1, double y1, double x2, double y2) nogil:
    """Calculate squared distance (C-optimized)."""
    cdef double dx = x2 - x1
    cdef double dy = y2 - y1
    return dx * dx + dy * dy


def trace_contours_cython(double[:, :] grid, double level):
    """
    Trace contours using Cython-optimized marching squares.
    
    Args:
        grid: 2D memoryview of grid data
        level: Contour level
    
    Returns:
        List of line segments as (x1, y1, x2, y2) tuples
    """
    cdef int height = grid.shape[0]
    cdef int width = grid.shape[1]
    cdef int x, y, case_idx, edge_start, edge_end
    cdef double v00, v10, v01, v11
    cdef double t_start, t_end
    cdef double x1, y1, x2, y2
    
    segments = []
    
    # Process each grid cell
    for y in range(height - 1):
        for x in range(width - 1):
            # Get corner values
            v00 = grid[y, x]
            v10 = grid[y, x + 1]
            v01 = grid[y + 1, x]
            v11 = grid[y + 1, x + 1]
            
            # Determine case
            case_idx = get_case_index_c(v00, v10, v11, v01, level)
            
            # Process segments for this case
            if case_idx == 1:  # [(3, 0)]
                t_start = interpolate_edge_c(v00, v01, level)
                t_end = interpolate_edge_c(v00, v10, level)
                get_edge_coords_c(x, y, 3, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 0, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 2:  # [(0, 1)]
                t_start = interpolate_edge_c(v00, v10, level)
                t_end = interpolate_edge_c(v10, v11, level)
                get_edge_coords_c(x, y, 0, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 1, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 3:  # [(3, 1)]
                t_start = interpolate_edge_c(v00, v01, level)
                t_end = interpolate_edge_c(v10, v11, level)
                get_edge_coords_c(x, y, 3, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 1, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 4:  # [(1, 2)]
                t_start = interpolate_edge_c(v10, v11, level)
                t_end = interpolate_edge_c(v01, v11, level)
                get_edge_coords_c(x, y, 1, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 2, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 6:  # [(0, 2)]
                t_start = interpolate_edge_c(v00, v10, level)
                t_end = interpolate_edge_c(v01, v11, level)
                get_edge_coords_c(x, y, 0, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 2, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 7:  # [(3, 2)]
                t_start = interpolate_edge_c(v00, v01, level)
                t_end = interpolate_edge_c(v01, v11, level)
                get_edge_coords_c(x, y, 3, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 2, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 8:  # [(2, 3)]
                t_start = interpolate_edge_c(v01, v11, level)
                t_end = interpolate_edge_c(v00, v01, level)
                get_edge_coords_c(x, y, 2, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 3, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 9:  # [(0, 2)]
                t_start = interpolate_edge_c(v00, v10, level)
                t_end = interpolate_edge_c(v01, v11, level)
                get_edge_coords_c(x, y, 0, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 2, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 11:  # [(1, 2)]
                t_start = interpolate_edge_c(v10, v11, level)
                t_end = interpolate_edge_c(v01, v11, level)
                get_edge_coords_c(x, y, 1, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 2, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 12:  # [(1, 3)]
                t_start = interpolate_edge_c(v10, v11, level)
                t_end = interpolate_edge_c(v00, v01, level)
                get_edge_coords_c(x, y, 1, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 3, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 13:  # [(0, 1)]
                t_start = interpolate_edge_c(v00, v10, level)
                t_end = interpolate_edge_c(v10, v11, level)
                get_edge_coords_c(x, y, 0, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 1, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
            
            elif case_idx == 14:  # [(0, 3)]
                t_start = interpolate_edge_c(v00, v10, level)
                t_end = interpolate_edge_c(v00, v01, level)
                get_edge_coords_c(x, y, 0, t_start, &x1, &y1)
                get_edge_coords_c(x, y, 3, t_end, &x2, &y2)
                segments.append([(x1, y1), (x2, y2)])
    
    return segments


cdef class ContourTracer:
    """Cython-optimized contour tracer."""
    
    cdef int width
    cdef int height
    cdef double[:, :] grid
    
    def __init__(self, int width, int height):
        """Initialize contour tracer."""
        self.width = width
        self.height = height
        import numpy as np
        self.grid = np.zeros((height, width), dtype=np.float64)
    
    def set_data(self, data):
        """Set grid data."""
        import numpy as np
        self.grid = np.array(data, dtype=np.float64)
    
    def trace_level(self, double level, bint merge=False):
        """Trace contours at specified level."""
        return trace_contours_cython(self.grid, level)
    
    def trace_levels(self, levels, bint merge=False):
        """Trace contours at multiple levels."""
        result = {}
        for level in levels:
            result[level] = self.trace_level(level, merge)
        return result


# C-style API
def new_contour_tracer(int width, int height):
    """Create new contour tracer."""
    return ContourTracer(width, height)


def delete_contour_tracer(tracer):
    """Delete contour tracer."""
    pass


def set_contour_data(tracer, data):
    """Set grid data."""
    try:
        tracer.set_data(data)
        return True
    except Exception:
        return False


def trace_contour_level(tracer, double level, bint merge=False):
    """Trace contours at specified level."""
    return tracer.trace_level(level, merge)


def trace_contour_levels(tracer, levels, bint merge=False):
    """Trace contours at multiple levels."""
    return tracer.trace_levels(levels, merge)
