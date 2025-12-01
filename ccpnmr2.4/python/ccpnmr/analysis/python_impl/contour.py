"""
Pure Python contour tracing implementation (marching squares algorithm).

IMPORTANT: This is a simplified standalone implementation created for performance
comparison purposes (Python vs Numba vs Cython). It is NOT a wrapper around
the existing C implementation at ccpnmr2.4/c/ccpnmr/analysis/contour_file.c.

Why simplified implementation?
- The original C contour_file.c (~700 lines) has many dependencies:
  block_file, store_file, contour_data, hash_table, drawing_funcs, mem_cache
- This implementation extracts only the computational hot path (marching squares)
- Allows fair performance comparison without complex file I/O and caching overhead
- Focuses on the algorithm that benefits most from optimization

This is a simplified version focusing on the core computational algorithms:
- Marching squares contour tracing
- Bilinear interpolation for contour positions
- Polyline generation from grid data

Note: Full contour_file.c requires many dependencies (block_file, store_file,
hash_table, drawing_funcs, etc.). This implementation focuses on the hot path:
the numerical algorithms that would benefit most from optimization.
"""

from typing import List, Tuple, Optional
import math

# Marching squares lookup table
# Each case defines line segments connecting edge midpoints
# Edges: 0=bottom, 1=right, 2=top, 3=left
# Format: (start_edge, end_edge) pairs for each configuration
MARCHING_SQUARES_CASES = [
    [],              # 0000: no contour
    [(3, 0)],        # 0001: bottom-left corner
    [(0, 1)],        # 0010: bottom-right corner
    [(3, 1)],        # 0011: bottom edge
    [(1, 2)],        # 0100: top-right corner
    [(3, 0), (1, 2)], # 0101: ambiguous case (saddle)
    [(0, 2)],        # 0110: right edge
    [(3, 2)],        # 0111: left edge
    [(2, 3)],        # 1000: top-left corner
    [(0, 2)],        # 1001: left edge  
    [(0, 1), (2, 3)], # 1010: ambiguous case (saddle)
    [(1, 2)],        # 1011: top edge
    [(1, 3)],        # 1100: top edge
    [(0, 1)],        # 1101: right edge
    [(0, 3)],        # 1110: left edge
    [],              # 1111: no contour
]


def interpolate_edge(v1: float, v2: float, level: float) -> float:
    """
    Linear interpolation to find where contour crosses edge.
    
    Args:
        v1: Value at edge start
        v2: Value at edge end
        level: Contour level
    
    Returns:
        Position along edge (0.0 to 1.0)
    """
    if abs(v2 - v1) < 1e-10:
        return 0.5
    return (level - v1) / (v2 - v1)


def get_edge_point(x: int, y: int, edge: int, grid: List[List[float]], 
                    level: float) -> Tuple[float, float]:
    """
    Get interpolated coordinates of contour crossing on edge.
    
    Args:
        x, y: Grid cell coordinates
        edge: Edge number (0=bottom, 1=right, 2=top, 3=left)
        grid: 2D grid of values
        level: Contour level
    
    Returns:
        (x_pos, y_pos) interpolated coordinates
    """
    if edge == 0:  # Bottom edge
        v1, v2 = grid[y][x], grid[y][x + 1]
        t = interpolate_edge(v1, v2, level)
        return (x + t, y)
    elif edge == 1:  # Right edge
        v1, v2 = grid[y][x + 1], grid[y + 1][x + 1]
        t = interpolate_edge(v1, v2, level)
        return (x + 1, y + t)
    elif edge == 2:  # Top edge
        v1, v2 = grid[y + 1][x], grid[y + 1][x + 1]
        t = interpolate_edge(v1, v2, level)
        return (x + t, y + 1)
    else:  # edge == 3, Left edge
        v1, v2 = grid[y][x], grid[y + 1][x]
        t = interpolate_edge(v1, v2, level)
        return (x, y + t)


def trace_contours(grid: List[List[float]], level: float) -> List[List[Tuple[float, float]]]:
    """
    Trace contours in 2D grid at specified level using marching squares.
    
    Args:
        grid: 2D grid of values (rows x cols)
        level: Contour level to trace
    
    Returns:
        List of polylines, each polyline is a list of (x, y) points
    """
    if not grid or not grid[0]:
        return []
    
    height = len(grid)
    width = len(grid[0])
    
    if height < 2 or width < 2:
        return []
    
    polylines = []
    
    # Process each grid cell
    for y in range(height - 1):
        for x in range(width - 1):
            # Get corner values
            v00 = grid[y][x]
            v10 = grid[y][x + 1]
            v01 = grid[y + 1][x]
            v11 = grid[y + 1][x + 1]
            
            # Determine case index (which corners are above level)
            case_idx = 0
            if v00 >= level:
                case_idx |= 1
            if v10 >= level:
                case_idx |= 2
            if v11 >= level:
                case_idx |= 4
            if v01 >= level:
                case_idx |= 8
            
            # Get line segments for this case
            segments = MARCHING_SQUARES_CASES[case_idx]
            
            # Generate polylines for each segment
            for start_edge, end_edge in segments:
                p1 = get_edge_point(x, y, start_edge, grid, level)
                p2 = get_edge_point(x, y, end_edge, grid, level)
                polylines.append([p1, p2])
    
    return polylines


def merge_polylines(polylines: List[List[Tuple[float, float]]], 
                     tolerance: float = 0.01) -> List[List[Tuple[float, float]]]:
    """
    Merge connected polyline segments into longer contours.
    
    Args:
        polylines: List of line segments
        tolerance: Distance tolerance for connecting endpoints
    
    Returns:
        List of merged polylines
    """
    if not polylines:
        return []
    
    # Convert to mutable lists
    segments = [list(seg) for seg in polylines]
    merged = []
    
    while segments:
        # Start new contour with first segment
        current = segments.pop(0)
        changed = True
        
        # Keep trying to extend current contour
        while changed:
            changed = False
            i = 0
            while i < len(segments):
                seg = segments[i]
                
                # Check if segment connects to start of current
                if _distance(seg[-1], current[0]) < tolerance:
                    current = seg[:-1] + current
                    segments.pop(i)
                    changed = True
                    continue
                
                # Check if segment connects to end of current
                elif _distance(seg[0], current[-1]) < tolerance:
                    current = current + seg[1:]
                    segments.pop(i)
                    changed = True
                    continue
                
                # Check if reversed segment connects to start
                elif _distance(seg[0], current[0]) < tolerance:
                    current = list(reversed(seg))[:-1] + current
                    segments.pop(i)
                    changed = True
                    continue
                
                # Check if reversed segment connects to end
                elif _distance(seg[-1], current[-1]) < tolerance:
                    current = current + list(reversed(seg))[1:]
                    segments.pop(i)
                    changed = True
                    continue
                
                i += 1
        
        merged.append(current)
    
    return merged


def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


class ContourTracer:
    """
    Simplified contour tracer focusing on computational hot paths.
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize contour tracer.
        
        Args:
            width: Grid width
            height: Grid height
        """
        self.width = width
        self.height = height
        self.grid = [[0.0 for _ in range(width)] for _ in range(height)]
    
    def set_data(self, data: List[List[float]]) -> None:
        """Set grid data."""
        if len(data) != self.height or len(data[0]) != self.width:
            raise ValueError(f"Data size mismatch: expected {self.height}x{self.width}")
        self.grid = [list(row) for row in data]
    
    def trace_level(self, level: float, merge: bool = True) -> List[List[Tuple[float, float]]]:
        """
        Trace contours at specified level.
        
        Args:
            level: Contour level
            merge: Whether to merge connected segments
        
        Returns:
            List of polylines
        """
        polylines = trace_contours(self.grid, level)
        
        if merge and polylines:
            polylines = merge_polylines(polylines)
        
        return polylines
    
    def trace_levels(self, levels: List[float], merge: bool = True) -> dict:
        """
        Trace contours at multiple levels.
        
        Args:
            levels: List of contour levels
            merge: Whether to merge connected segments
        
        Returns:
            Dictionary mapping level to list of polylines
        """
        result = {}
        for level in levels:
            result[level] = self.trace_level(level, merge)
        return result
    
    def count_vertices(self, polylines: List[List[Tuple[float, float]]]) -> int:
        """Count total vertices in polylines."""
        return sum(len(poly) for poly in polylines)


# C-style API functions
def new_contour_tracer(width: int, height: int) -> ContourTracer:
    """Create new contour tracer."""
    return ContourTracer(width, height)


def delete_contour_tracer(tracer: ContourTracer) -> None:
    """Delete contour tracer."""
    pass


def set_contour_data(tracer: ContourTracer, data: List[List[float]]) -> bool:
    """Set grid data for contour tracing."""
    try:
        tracer.set_data(data)
        return True
    except Exception:
        return False


def trace_contour_level(tracer: ContourTracer, level: float, 
                         merge: bool = True) -> List[List[Tuple[float, float]]]:
    """Trace contours at specified level."""
    return tracer.trace_level(level, merge)


def trace_contour_levels(tracer: ContourTracer, levels: List[float],
                          merge: bool = True) -> dict:
    """Trace contours at multiple levels."""
    return tracer.trace_levels(levels, merge)
