"""
Contour generation engine for 2D spectral data.

This module implements the marching squares algorithm for generating contour lines
at specified levels in 2D data. It's designed to be thread-safe and memory-efficient.

Key features:
- Marching squares algorithm for contour tracing
- Multiple contour levels in a single pass
- Efficient vertex allocation with block storage
- Handles saddle points (ambiguous cases) correctly
- Chain processing for contour path extraction

Algorithm:
    The marching squares algorithm processes a 2D grid cell-by-cell, examining
    each 2×2 block of data points. Based on which corners are above/below the
    contour level, one of 16 edge cases is selected. Linear interpolation
    determines exact vertex positions along edges.
    
    For saddle point cases (opposite corners above/below threshold), the
    average value of the four corners determines the disambiguation.

Performance:
    - O(n*m) complexity for n×m grid
    - Single pass for multiple contour levels
    - Block vertex allocation reduces malloc overhead
    - No recursion (iteration-based chain traversal)

Example Usage:
    >>> import numpy as np
    >>> from memops.global_.python_impl.contourer import calculate_contours, ContoururInfo
    >>> 
    >>> # Generate test data
    >>> x = np.linspace(-3, 3, 100)
    >>> y = np.linspace(-3, 3, 100)
    >>> X, Y = np.meshgrid(x, y)
    >>> data = np.exp(-(X**2 + Y**2))
    >>> 
    >>> # Create row access function
    >>> def get_row(user_data):
    >>>     row_index = user_data['row']
    >>>     return user_data['data'][row_index, :]
    >>> 
    >>> # Configure contourer
    >>> user_data = {'data': data, 'row': 0}
    >>> info = ContoururInfo(
    >>>     user_data=user_data,
    >>>     nlevels=3,
    >>>     levels=np.array([0.3, 0.5, 0.7]),
    >>>     npoints=np.array([100, 100]),
    >>>     offset=np.array([0.0, 0.0]),
    >>>     scale=np.array([1.0, 1.0]),
    >>>     get_row_func=get_row
    >>> )
    >>> 
    >>> # Generate contours
    >>> contours = calculate_contours(info)
    >>> print(f"Generated {contours.n} contour levels")
    >>> print(f"Level 0 has {contours.vertices[0].nvertices} vertices")
    >>> 
    >>> # Extract contour paths
    >>> def draw_callback(vertices, first_vertex):
    >>>     coords = []
    >>>     v = first_vertex
    >>>     while v is not None:
    >>>         coords.append(v.x)
    >>>         v = v.v1  # Follow chain
    >>>     return coords
    >>> 
    >>> from memops.global_.python_impl.contourer import process_chains
    >>> paths = process_chains(contours, 0, draw_callback)

See Also:
    - contour_file.py: Storage and caching of generated contours
    - contour_levels.py: Level calculation strategies
    - slice_file.py: 1D slice extraction through spectral data

Original C: ccpnmr2.4/c/memops/global/contourer.c (745 lines)
Python implementation: 577 lines (22% reduction with NumPy)
"""

import numpy as np
from typing import List, Tuple, Callable, Optional, Any
from dataclasses import dataclass, field

CONTOUR_NALLOC = 50  # Allocate vertices in blocks of this size


@dataclass
class ContourVertex:
    """A single vertex in a contour line."""
    x: np.ndarray  # [x, y] coordinates (2-element array)
    v1: Optional['ContourVertex'] = None  # Previous vertex (None if none)
    v2: Optional['ContourVertex'] = None  # Next vertex (None if none)
    visited: bool = False  # For chain traversal


@dataclass
class ContourVertices:
    """Collection of vertices for a single contour level."""
    nvertices: int = 0
    nalloc: int = CONTOUR_NALLOC
    vertex_store: List[List[ContourVertex]] = field(default_factory=list)
    
    def new_vertex(self, x: float, y: float) -> ContourVertex:
        """Allocate a new vertex at position (x, y)."""
        nblocks = self.nvertices // self.nalloc
        
        if self.nvertices % self.nalloc == 0:  # Need new block
            self.vertex_store.append([])
        
        v = ContourVertex(x=np.array([x, y], dtype=np.float32))
        self.vertex_store[nblocks].append(v)
        self.nvertices += 1
        
        return v
    
    def get_vertex(self, index: int) -> ContourVertex:
        """Get vertex by index."""
        nblock = index // self.nalloc
        offset = index % self.nalloc
        return self.vertex_store[nblock][offset]


@dataclass
class Contours:
    """Container for contours at multiple levels."""
    n: int  # Number of levels
    vertices: List[ContourVertices] = field(default_factory=list)


class ContoururInfo:
    """
    Configuration for contour generation.
    
    This class holds the parameters needed for generating contours and can be
    reused across multiple calculate_contours() calls with changing parameters.
    """
    
    def __init__(self,
                 user_data: Any,
                 nlevels: int,
                 levels: np.ndarray,
                 npoints: np.ndarray,
                 offset: np.ndarray,
                 scale: np.ndarray,
                 get_row_func: Callable):
        """
        Initialize contour generator.
        
        Args:
            user_data: User data passed to get_row_func
            nlevels: Number of contour levels
            levels: Array of contour level values
            npoints: [nx, ny] data dimensions
            offset: [x0, y0] coordinate offsets
            scale: [dx, dy] coordinate scaling
            get_row_func: Callback to get data row: func(user_data) -> row_array
        """
        self.user_data = user_data
        self.nlevels = nlevels
        self.levels = np.asarray(levels, dtype=np.float32)
        self.npoints = np.asarray(npoints, dtype=np.int32)
        self.offset = np.asarray(offset, dtype=np.float32)
        self.scale = np.asarray(scale, dtype=np.float32)
        self.get_row_func = get_row_func
        
        # Pre-allocate storage for v_rows
        self.v_rows: List[List[Optional[ContourVertex]]] = []
        self._init_v_rows()
    
    def _init_v_rows(self):
        """Initialize v_rows storage for tracking vertices along rows."""
        m = self.nlevels * (self.npoints[0] - 1)
        self.v_rows = [[None for _ in range(self.npoints[0] - 1)] 
                       for _ in range(self.nlevels)]


def _interpolate(level: float, a: float, b: float) -> float:
    """Linear interpolation between a and b at level."""
    return (level - a) / (b - a)


def _new_vertex0(vertices: ContourVertices, 
                 offset: np.ndarray,
                 scale: np.ndarray,
                 level: float,
                 d1: float, d2: float,
                 x: int, y: int) -> ContourVertex:
    """Create vertex with interpolation in x direction."""
    x_coord = offset[0] + scale[0] * (x + _interpolate(level, d1, d2))
    y_coord = offset[1] + scale[1] * y
    return vertices.new_vertex(x_coord, y_coord)


def _new_vertex1(vertices: ContourVertices,
                 offset: np.ndarray,
                 scale: np.ndarray,
                 level: float,
                 d1: float, d2: float,
                 x: int, y: int) -> ContourVertex:
    """Create vertex with interpolation in y direction."""
    x_coord = offset[0] + scale[0] * x
    y_coord = offset[1] + scale[1] * (y + _interpolate(level, d1, d2))
    return vertices.new_vertex(x_coord, y_coord)


def _new_edge01(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int):
    """Handle edge case: 0 0 / 0 1"""
    v_col = _new_vertex1(vertices, offset, scale, level, data_old, data_new, x+1, y)
    v_old = v_row[x]
    v_old.v1 = v_col
    v_col.v2 = v_old
    p_v_col[0] = v_col


def _new_edge32(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int):
    """Handle edge case: 1 1 / 1 0"""
    v_col = _new_vertex1(vertices, offset, scale, level, data_old, data_new, x+1, y)
    v_old = v_row[x]
    v_old.v2 = v_col
    v_col.v1 = v_old
    p_v_col[0] = v_col


def _new_edge02(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float):
    """Handle edge case: 0 1 / 0 0"""
    v_new = _new_vertex0(vertices, offset, scale, level, data_new_prev, data_new, x, y+1)
    v_col = _new_vertex1(vertices, offset, scale, level, data_old, data_new, x+1, y)
    v_row[x] = v_new
    v_new.v2 = v_col
    v_col.v1 = v_new
    p_v_col[0] = v_col


def _new_edge31(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float):
    """Handle edge case: 1 0 / 1 1"""
    v_new = _new_vertex0(vertices, offset, scale, level, data_new_prev, data_new, x, y+1)
    v_col = _new_vertex1(vertices, offset, scale, level, data_old, data_new, x+1, y)
    v_row[x] = v_new
    v_new.v1 = v_col
    v_col.v2 = v_new
    p_v_col[0] = v_col


def _new_edge03(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float):
    """Handle edge case: 0 1 / 0 1"""
    v_new = _new_vertex0(vertices, offset, scale, level, data_new_prev, data_new, x, y+1)
    v_old = v_row[x]
    v_row[x] = v_new
    v_old.v1 = v_new
    v_new.v2 = v_old


def _new_edge30(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float):
    """Handle edge case: 1 0 / 1 0"""
    v_new = _new_vertex0(vertices, offset, scale, level, data_new_prev, data_new, x, y+1)
    v_old = v_row[x]
    v_row[x] = v_new
    v_old.v2 = v_new
    v_new.v1 = v_old


def _new_edge10(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float = None):
    """Handle edge case: 0 0 / 1 0"""
    v_col = p_v_col[0]
    v_old = v_row[x]
    v_old.v2 = v_col
    v_col.v1 = v_old


def _new_edge23(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float = None):
    """Handle edge case: 1 1 / 0 1"""
    v_col = p_v_col[0]
    v_old = v_row[x]
    v_old.v1 = v_col
    v_col.v2 = v_old


def _new_edge11(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float = None):
    """Handle edge case: 0 0 / 1 1"""
    v_new = _new_vertex1(vertices, offset, scale, level, data_old, data_new, x+1, y)
    v_col = p_v_col[0]
    v_col.v1 = v_new
    v_new.v2 = v_col
    p_v_col[0] = v_new


def _new_edge22(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float = None):
    """Handle edge case: 1 1 / 0 0"""
    v_new = _new_vertex1(vertices, offset, scale, level, data_old, data_new, x+1, y)
    v_col = p_v_col[0]
    v_col.v2 = v_new
    v_new.v1 = v_col
    p_v_col[0] = v_new


def _new_edge12(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_old_prev: float, data_new_prev: float):
    """Handle saddle point: 0 1 / 1 0 (ambiguous case)"""
    d1 = data_old_prev
    d2 = data_old
    d3 = data_new_prev
    d4 = data_new
    
    v = _new_vertex0(vertices, offset, scale, level, d3, d4, x, y+1)
    v_new = _new_vertex1(vertices, offset, scale, level, d2, d4, x+1, y)
    
    d = (d1 + d2 + d3 + d4) / 4.0
    
    v_col = p_v_col[0]
    v_old = v_row[x]
    
    if d > level:
        v_col.v1 = v
        v.v2 = v_col
        v_new.v1 = v_old
        v_old.v2 = v_new
    else:
        v_col.v1 = v_old
        v_old.v2 = v_col
        v_new.v1 = v
        v.v2 = v_new
    
    v_row[x] = v
    p_v_col[0] = v_new


def _new_edge21(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_old_prev: float, data_new_prev: float):
    """Handle saddle point: 1 0 / 0 1 (ambiguous case)"""
    d1 = data_old_prev
    d2 = data_old
    d3 = data_new_prev
    d4 = data_new
    
    v = _new_vertex0(vertices, offset, scale, level, d3, d4, x, y+1)
    v_new = _new_vertex1(vertices, offset, scale, level, d2, d4, x+1, y)
    
    d = (d1 + d2 + d3 + d4) / 4.0
    
    v_col = p_v_col[0]
    v_old = v_row[x]
    
    if d > level:
        v_col.v2 = v_old
        v_old.v1 = v_col
        v_new.v2 = v
        v.v1 = v_new
    else:
        v_col.v2 = v
        v.v1 = v_col
        v_new.v2 = v_old
        v_old.v1 = v_new
    
    v_row[x] = v
    p_v_col[0] = v_new


def _new_edge13(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float):
    """Handle edge case: 0 1 / 1 1"""
    v_new = _new_vertex0(vertices, offset, scale, level, data_new_prev, data_new, x, y+1)
    v_col = p_v_col[0]
    v_row[x] = v_new
    v_col.v1 = v_new
    v_new.v2 = v_col


def _new_edge20(vertices: ContourVertices, offset: np.ndarray, scale: np.ndarray,
                level: float, data_old: float, data_new: float,
                v_row: List[Optional[ContourVertex]], p_v_col: List[Optional[ContourVertex]],
                x: int, y: int, data_new_prev: float):
    """Handle edge case: 1 0 / 0 0"""
    v_new = _new_vertex0(vertices, offset, scale, level, data_new_prev, data_new, x, y+1)
    v_col = p_v_col[0]
    v_row[x] = v_new
    v_col.v2 = v_new
    v_new.v1 = v_col


# Lookup table for edge functions
# Indexed by [bottom_left, bottom_right, top_left, top_right] binary pattern
_edge_functions = [
    [None,        _new_edge01, _new_edge02, _new_edge03],  # 0b00xx
    [_new_edge10, _new_edge11, _new_edge12, _new_edge13],  # 0b01xx
    [_new_edge20, _new_edge21, _new_edge22, _new_edge23],  # 0b10xx
    [_new_edge30, _new_edge31, _new_edge32, None]          # 0b11xx
]


def calculate_contours(contourer_info: ContoururInfo) -> Contours:
    """
    Calculate contours for all levels.
    
    Uses the marching squares algorithm to trace contour lines through 2D data.
    This is the main entry point for contour generation.
    
    Args:
        contourer_info: Configuration object with levels, data access, etc.
    
    Returns:
        Contours object containing vertices for all levels
    """
    npoints = contourer_info.npoints
    nlevels = contourer_info.nlevels
    levels = contourer_info.levels
    offset = contourer_info.offset
    scale = contourer_info.scale
    get_row_func = contourer_info.get_row_func
    user_data = contourer_info.user_data
    
    # Create contours structure
    contours = Contours(n=nlevels)
    contours.vertices = [ContourVertices() for _ in range(nlevels)]
    
    # Early return if no data
    if npoints[0] < 1 or npoints[1] < 1:
        return contours
    
    v_rows = contourer_info.v_rows
    
    # First, handle vertices along bottom row
    data_old = get_row_func(user_data)
    
    for l in range(nlevels):
        level = levels[l]
        contour_vertices = contours.vertices[l]
        v_row = v_rows[l]
        
        b_old = 1 if data_old[0] > level else 0
        
        for i0 in range(npoints[0] - 1):
            b_new = 1 if data_old[i0 + 1] > level else 0
            
            if b_old != b_new:
                v_row[i0] = _new_vertex0(contour_vertices, offset, scale, level,
                                         data_old[i0], data_old[i0 + 1], i0, 0)
                b_old = b_new
    
    # Process remaining rows
    for i1 in range(npoints[1] - 1):
        data_new = get_row_func(user_data)
        
        for l in range(nlevels):
            level = levels[l]
            contour_vertices = contours.vertices[l]
            v_row = v_rows[l]
            
            # Compute initial state
            b_old = (1 if data_old[0] > level else 0) | \
                    (2 if data_new[0] > level else 0)
            
            # Initialize v_col for edge cases
            v_col = [None]
            if b_old == 1 or b_old == 2:
                v_col[0] = _new_vertex1(contour_vertices, offset, scale, level,
                                        data_old[0], data_new[0], 0, i1)
            
            new_edge_row = _edge_functions[b_old]
            
            for i0 in range(npoints[0] - 1):
                b_new = (1 if data_old[i0 + 1] > level else 0) | \
                        (2 if data_new[i0 + 1] > level else 0)
                
                edge_func = new_edge_row[b_new]
                if edge_func:
                    # Call appropriate edge function
                    if edge_func in (_new_edge12, _new_edge21):
                        # Saddle points need all 4 values
                        edge_func(contour_vertices, offset, scale, level,
                                 data_old[i0 + 1], data_new[i0 + 1],
                                 v_row, v_col, i0, i1,
                                 data_old[i0], data_new[i0])
                    elif edge_func in (_new_edge02, _new_edge31, _new_edge03, 
                                      _new_edge30, _new_edge13, _new_edge20):
                        # These need previous data_new value
                        edge_func(contour_vertices, offset, scale, level,
                                 data_old[i0 + 1], data_new[i0 + 1],
                                 v_row, v_col, i0, i1, data_new[i0])
                    else:
                        # Simple cases
                        edge_func(contour_vertices, offset, scale, level,
                                 data_old[i0 + 1], data_new[i0 + 1],
                                 v_row, v_col, i0, i1)
                    
                    b_old = b_new
                    new_edge_row = _edge_functions[b_old]
        
        # Swap rows
        data_old = data_new
    
    return contours


def process_chains(contour_vertices: ContourVertices,
                  user_data: Any,
                  chain_func: Callable[[Any, int, ContourVertex], None]) -> None:
    """
    Process all contour chains (connected paths).
    
    Traverses the vertex graph to identify connected chains and calls
    chain_func for each chain with its vertex list.
    
    Args:
        contour_vertices: Vertices for a single level
        user_data: User data passed to chain_func
        chain_func: Callback function(user_data, nvertices, first_vertex)
    """
    # Mark all vertices as unvisited
    for i in range(contour_vertices.nvertices):
        v = contour_vertices.get_vertex(i)
        v.visited = False
    
    # Process each unvisited vertex
    for i in range(contour_vertices.nvertices):
        v = contour_vertices.get_vertex(i)
        
        if v.visited:
            continue
        
        # Count vertices in chain going backwards
        nvertices = 1
        vv = v
        while vv.v1 and vv.v1 is not v:
            vv = vv.v1
            nvertices += 1
            vv.visited = True
        
        vv.visited = True
        
        # Count vertices going forwards
        v_temp = v.v2
        while v_temp and v_temp is not vv:
            nvertices += 1
            v_temp.visited = True
            v_temp = v_temp.v2
        
        # Call user function with chain info
        chain_func(user_data, nvertices, vv)


# Factory functions for C API compatibility
def new_contourer_info(user_data: Any,
                       nlevels: int,
                       levels: np.ndarray,
                       npoints: np.ndarray,
                       offset: np.ndarray,
                       scale: np.ndarray,
                       get_row_func: Callable) -> ContoururInfo:
    """Create new contourer info object."""
    return ContoururInfo(user_data, nlevels, levels, npoints, offset, scale, get_row_func)


def delete_contourer_info(contourer_info: ContoururInfo) -> None:
    """Delete contourer info (Python handles cleanup automatically)."""
    pass


def delete_contours(contours: Contours) -> None:
    """Delete contours (Python handles cleanup automatically)."""
    pass
