"""
Numba-accelerated contour tracing implementation.

IMPORTANT: This is a simplified standalone implementation created for performance
comparison purposes (Python vs Numba vs Cython). It is NOT a wrapper around
the existing C implementation at ccpnmr2.4/c/ccpnmr/analysis/contour_file.c.

See contour.py for rationale on why a simplified implementation was created
instead of wrapping the existing C code.

Uses numba JIT compilation for the hot path numerical algorithms:
- Marching squares with @jit
- Edge interpolation with @jit  
- Distance calculations with @jit
"""

from typing import List, Tuple, Optional
import math

try:
    from numba import jit
    import numpy as np
    NUMBA_AVAILABLE = True
except ImportError:
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
    NUMBA_AVAILABLE = False
    import array

# Marching squares lookup table (same as pure Python)
MARCHING_SQUARES_CASES = [
    [],              # 0000
    [(3, 0)],        # 0001
    [(0, 1)],        # 0010
    [(3, 1)],        # 0011
    [(1, 2)],        # 0100
    [(3, 0), (1, 2)], # 0101
    [(0, 2)],        # 0110
    [(3, 2)],        # 0111
    [(2, 3)],        # 1000
    [(0, 2)],        # 1001
    [(0, 1), (2, 3)], # 1010
    [(1, 2)],        # 1011
    [(1, 3)],        # 1100
    [(0, 1)],        # 1101
    [(0, 3)],        # 1110
    [],              # 1111
]


@jit(nopython=True)
def interpolate_edge_numba(v1: float, v2: float, level: float) -> float:
    """Linear interpolation (numba-optimized)."""
    if abs(v2 - v1) < 1e-10:
        return 0.5
    return (level - v1) / (v2 - v1)


@jit(nopython=True)
def get_case_index(v00: float, v10: float, v11: float, v01: float, level: float) -> int:
    """Determine marching squares case (numba-optimized)."""
    case_idx = 0
    if v00 >= level:
        case_idx |= 1
    if v10 >= level:
        case_idx |= 2
    if v11 >= level:
        case_idx |= 4
    if v01 >= level:
        case_idx |= 8
    return case_idx


@jit(nopython=True)
def get_edge_coords(x: int, y: int, edge: int, t: float) -> tuple:
    """Get edge coordinates (numba-optimized)."""
    if edge == 0:  # Bottom
        return (x + t, y)
    elif edge == 1:  # Right
        return (x + 1, y + t)
    elif edge == 2:  # Top
        return (x + t, y + 1)
    else:  # Left (edge == 3)
        return (x, y + t)


@jit(nopython=True)
def distance_squared(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate squared distance (numba-optimized)."""
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy


@jit(nopython=True)
def trace_contours_core(grid, level: float):
    """
    Core contour tracing with numba acceleration.
    Returns arrays of segment endpoints.
    """
    height, width = grid.shape
    
    if NUMBA_AVAILABLE:
        # Use numpy arrays for numba
        segments_x1 = []
        segments_y1 = []
        segments_x2 = []
        segments_y2 = []
    else:
        segments_x1 = []
        segments_y1 = []
        segments_x2 = []
        segments_y2 = []
    
    for y in range(height - 1):
        for x in range(width - 1):
            # Get corner values
            v00 = grid[y, x]
            v10 = grid[y, x + 1]
            v01 = grid[y + 1, x]
            v11 = grid[y + 1, x + 1]
            
            # Determine case
            case_idx = get_case_index(v00, v10, v11, v01, level)
            
            # Process segments for this case
            if case_idx == 1:  # [(3, 0)]
                t_start = interpolate_edge_numba(v00, v01, level)
                t_end = interpolate_edge_numba(v00, v10, level)
                p1 = get_edge_coords(x, y, 3, t_start)
                p2 = get_edge_coords(x, y, 0, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 2:  # [(0, 1)]
                t_start = interpolate_edge_numba(v00, v10, level)
                t_end = interpolate_edge_numba(v10, v11, level)
                p1 = get_edge_coords(x, y, 0, t_start)
                p2 = get_edge_coords(x, y, 1, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 3:  # [(3, 1)]
                t_start = interpolate_edge_numba(v00, v01, level)
                t_end = interpolate_edge_numba(v10, v11, level)
                p1 = get_edge_coords(x, y, 3, t_start)
                p2 = get_edge_coords(x, y, 1, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 4:  # [(1, 2)]
                t_start = interpolate_edge_numba(v10, v11, level)
                t_end = interpolate_edge_numba(v01, v11, level)
                p1 = get_edge_coords(x, y, 1, t_start)
                p2 = get_edge_coords(x, y, 2, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 6:  # [(0, 2)]
                t_start = interpolate_edge_numba(v00, v10, level)
                t_end = interpolate_edge_numba(v01, v11, level)
                p1 = get_edge_coords(x, y, 0, t_start)
                p2 = get_edge_coords(x, y, 2, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 7:  # [(3, 2)]
                t_start = interpolate_edge_numba(v00, v01, level)
                t_end = interpolate_edge_numba(v01, v11, level)
                p1 = get_edge_coords(x, y, 3, t_start)
                p2 = get_edge_coords(x, y, 2, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 8:  # [(2, 3)]
                t_start = interpolate_edge_numba(v01, v11, level)
                t_end = interpolate_edge_numba(v00, v01, level)
                p1 = get_edge_coords(x, y, 2, t_start)
                p2 = get_edge_coords(x, y, 3, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 9:  # [(0, 2)]
                t_start = interpolate_edge_numba(v00, v10, level)
                t_end = interpolate_edge_numba(v01, v11, level)
                p1 = get_edge_coords(x, y, 0, t_start)
                p2 = get_edge_coords(x, y, 2, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 11:  # [(1, 2)]
                t_start = interpolate_edge_numba(v10, v11, level)
                t_end = interpolate_edge_numba(v01, v11, level)
                p1 = get_edge_coords(x, y, 1, t_start)
                p2 = get_edge_coords(x, y, 2, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 12:  # [(1, 3)]
                t_start = interpolate_edge_numba(v10, v11, level)
                t_end = interpolate_edge_numba(v00, v01, level)
                p1 = get_edge_coords(x, y, 1, t_start)
                p2 = get_edge_coords(x, y, 3, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 13:  # [(0, 1)]
                t_start = interpolate_edge_numba(v00, v10, level)
                t_end = interpolate_edge_numba(v10, v11, level)
                p1 = get_edge_coords(x, y, 0, t_start)
                p2 = get_edge_coords(x, y, 1, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
            
            elif case_idx == 14:  # [(0, 3)]
                t_start = interpolate_edge_numba(v00, v10, level)
                t_end = interpolate_edge_numba(v00, v01, level)
                p1 = get_edge_coords(x, y, 0, t_start)
                p2 = get_edge_coords(x, y, 3, t_end)
                segments_x1.append(p1[0])
                segments_y1.append(p1[1])
                segments_x2.append(p2[0])
                segments_y2.append(p2[1])
    
    return segments_x1, segments_y1, segments_x2, segments_y2


class ContourTracer:
    """Numba-accelerated contour tracer."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        if NUMBA_AVAILABLE:
            self.grid = np.zeros((height, width), dtype=np.float64)
        else:
            self.grid = [[0.0 for _ in range(width)] for _ in range(height)]
    
    def set_data(self, data: List[List[float]]) -> None:
        """Set grid data."""
        if NUMBA_AVAILABLE:
            self.grid = np.array(data, dtype=np.float64)
        else:
            self.grid = [list(row) for row in data]
    
    def trace_level(self, level: float, merge: bool = False) -> List[List[Tuple[float, float]]]:
        """Trace contours at specified level (numba-accelerated)."""
        if NUMBA_AVAILABLE:
            x1, y1, x2, y2 = trace_contours_core(self.grid, level)
            polylines = [[(x1[i], y1[i]), (x2[i], y2[i])] for i in range(len(x1))]
        else:
            # Fallback to pure Python
            from .contour import trace_contours
            polylines = trace_contours(self.grid, level)
        
        return polylines
    
    def trace_levels(self, levels: List[float], merge: bool = False) -> dict:
        """Trace contours at multiple levels."""
        result = {}
        for level in levels:
            result[level] = self.trace_level(level, merge)
        return result


# C-style API
def new_contour_tracer(width: int, height: int) -> ContourTracer:
    """Create new contour tracer."""
    return ContourTracer(width, height)


def delete_contour_tracer(tracer: ContourTracer) -> None:
    """Delete contour tracer."""
    pass


def set_contour_data(tracer: ContourTracer, data: List[List[float]]) -> bool:
    """Set grid data."""
    try:
        tracer.set_data(data)
        return True
    except Exception:
        return False


def trace_contour_level(tracer: ContourTracer, level: float, 
                         merge: bool = False) -> List[List[Tuple[float, float]]]:
    """Trace contours at specified level."""
    return tracer.trace_level(level, merge)


def trace_contour_levels(tracer: ContourTracer, levels: List[float],
                          merge: bool = False) -> dict:
    """Trace contours at multiple levels."""
    return tracer.trace_levels(levels, merge)
