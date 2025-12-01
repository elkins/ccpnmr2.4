"""
Numba-accelerated bond implementation for molecular connectivity.

This version uses numba.jit decorators for geometric calculations like
distance checking and depth parameter computation.
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
BOND_NCOLORS = 3
DEFAULT_BOND_WIDTH = 3.0
NORMAL_LINE_STYLE = 0
DASHED_LINE_STYLE = 1
NLINE_STYLES = 2
MAX_Z = 10.0
MIN_PARAM = 0.2
MAX_PARAM = 1.0
FIELD_DEPTH = -4.0
SMALL_D = 1.0e-3


# Numba-accelerated geometric functions
@jit(nopython=True)
def _calculate_depth_param(z_mid: float, depth: float) -> float:
    """Calculate depth parameter for color blending (numba-optimized)."""
    if z_mid > depth:
        dz = z_mid - depth
        if dz > MAX_Z:
            return MAX_PARAM
        return MIN_PARAM + (MAX_PARAM - MIN_PARAM) * dz / MAX_Z
    else:
        dz = depth - z_mid
        if dz > MAX_Z:
            return MIN_PARAM
        return MAX_PARAM - (MAX_PARAM - MIN_PARAM) * dz / MAX_Z


@jit(nopython=True)
def _perspective_transform(x: float, y: float, z: float, depth: float) -> tuple:
    """Apply perspective transformation (numba-optimized)."""
    denom = depth - z
    if abs(denom) < SMALL_D:
        return (x, y)
    scale = depth / denom
    return (x * scale, y * scale)


@jit(nopython=True)
def _line_segment_closest_point(x: float, y: float,
                                 x1: float, y1: float,
                                 x2: float, y2: float) -> tuple:
    """
    Find closest point on line segment to given point (numba-optimized).
    Returns (lambda, closest_x, closest_y, distance_squared)
    """
    # Vector from p1 to p2
    dx = x2 - x1
    dy = y2 - y1
    
    # Vector from p1 to point
    px = x - x1
    py = y - y1
    
    # Dot products
    dot_prod = px * dx + py * dy
    len_sq = dx * dx + dy * dy
    
    if len_sq < SMALL_D:
        # Degenerate case: p1 == p2
        dist_sq = px * px + py * py
        return (0.0, x1, y1, dist_sq)
    
    # Lambda parameter (0 = at p1, 1 = at p2)
    lam = dot_prod / len_sq
    
    # Clamp to [0, 1] for line segment
    if lam < 0.0:
        lam = 0.0
    elif lam > 1.0:
        lam = 1.0
    
    # Closest point
    cx = x1 + lam * dx
    cy = y1 + lam * dy
    
    # Distance squared
    dcx = x - cx
    dcy = y - cy
    dist_sq = dcx * dcx + dcy * dcy
    
    return (lam, cx, cy, dist_sq)


class Bond:
    """
    Molecular bond with numba-accelerated geometric operations.
    """
    
    def __init__(self, atom1, atom2, color: Optional[List[float]]):
        self.atom1 = atom1
        self.atom2 = atom2
        
        if color is not None:
            self.have_color = True
            self.color = list(color)
        else:
            self.have_color = False
            self.color = [0.0, 0.0, 0.0]
        
        self.line_width = -1.0  # Negative means use default
        self.line_style = NORMAL_LINE_STYLE
        self.annotation = ""
    
    def __repr__(self) -> str:
        return (f"Bond(atom1={self.atom1.symbol if hasattr(self.atom1, 'symbol') else 'Atom'}, "
                f"atom2={self.atom2.symbol if hasattr(self.atom2, 'symbol') else 'Atom'}, "
                f"color={self.color if self.have_color else 'auto'})")


# C-style API functions
def new_bond(atom1, atom2, color: Optional[List[float]]) -> Bond:
    """Create a new bond between two atoms."""
    return Bond(atom1, atom2, color)


def delete_bond(bond: Bond) -> None:
    """Delete bond (cleanup)."""
    pass


def set_color_bond(bond: Bond, color: Optional[List[float]]) -> None:
    """Set bond color (or clear to use atom colors)."""
    if color is None:
        bond.have_color = False
        bond.color = [0.0, 0.0, 0.0]
    else:
        bond.have_color = True
        bond.color = list(color)


def set_line_width_bond(bond: Bond, width: float) -> None:
    """Set bond line width."""
    bond.line_width = width


def set_line_style_bond(bond: Bond, style: int) -> None:
    """Set bond line style (normal or dashed)."""
    if 0 <= style < NLINE_STYLES:
        bond.line_style = style


def set_annotation_bond(bond: Bond, annotation: Optional[str]) -> bool:
    """Set bond annotation text."""
    if annotation is None:
        bond.annotation = ""
    else:
        bond.annotation = annotation
    return True


def get_other_atom_bond(bond: Bond, atom):
    """Get the other atom in the bond."""
    if atom == bond.atom1:
        return bond.atom2
    elif atom == bond.atom2:
        return bond.atom1
    else:
        return None


def get_depth_param_bond(bond: Bond, depth: float) -> float:
    """Get depth parameter for color blending (numba-accelerated)."""
    # Use midpoint of two atoms
    z1 = bond.atom1.x[2]
    z2 = bond.atom2.x[2]
    z_mid = (z1 + z2) / 2.0
    return _calculate_depth_param(z_mid, depth)


def draw_bond(bond: Bond, line_width: float, depth: float) -> None:
    """
    Draw bond (stub - requires drawing_funcs infrastructure).
    
    The C implementation renders:
    - Line from atom1 to atom2 with perspective projection
    - Bi-color gradient if no explicit color (blend atom colors)
    - Depth cueing (color blending based on z-position)
    - Line style (solid or dashed)
    - Annotation text at bond midpoint
    """
    raise NotImplementedError("draw_bond requires drawing_funcs infrastructure")


def within_xy_tol_bond(bond: Bond, x: float, y: float, 
                       tol: float, depth: float, z_out: List[float]) -> bool:
    """
    Check if point is within tolerance of bond line (numba-accelerated).
    
    Args:
        bond: The bond to check
        x, y: Point coordinates (screen space)
        tol: Distance tolerance
        depth: Camera depth for perspective
        z_out: Output list to store z-coordinate [z]
    
    Returns:
        True if point is within tolerance of bond line
    """
    # Get atom positions
    x1, y1, z1 = bond.atom1.x
    x2, y2, z2 = bond.atom2.x
    
    # Check if behind camera
    if z1 > 0.0 or z2 > 0.0:
        return False
    
    # Apply perspective transform
    xs1, ys1 = _perspective_transform(x1, y1, z1, depth)
    xs2, ys2 = _perspective_transform(x2, y2, z2, depth)
    
    # Find closest point on line segment
    lam, cx, cy, dist_sq = _line_segment_closest_point(x, y, xs1, ys1, xs2, ys2)
    
    # Check tolerance
    tol_sq = tol * tol
    if dist_sq > tol_sq:
        return False
    
    # Calculate z at closest point
    z_closest = z1 + lam * (z2 - z1)
    z_out[0] = z_closest
    
    return True
