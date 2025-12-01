"""
Numba-accelerated 3D atom implementation for molecular visualization.

This version uses numba.jit decorators for numerical operations like
geometric transformations, which can provide significant speedups.
"""

from typing import Optional, List
import math

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
ATOM_NDIMS = 3
ATOM_NCOLORS = 3
MAX_Z = 10.0
MIN_PARAM = 0.2
MAX_PARAM = 1.0
FIELD_DEPTH = -4.0


# Numba-accelerated geometric functions
@jit(nopython=True)
def _translate_coords(x: float, y: float, z: float, 
                      dx: float, dy: float, dz: float) -> tuple:
    """Translate 3D coordinates (numba-optimized)."""
    return (x + dx, y + dy, z + dz)


@jit(nopython=True)
def _rotate_coords(x: float, y: float, z: float,
                   ox: float, oy: float, oz: float,
                   m00: float, m01: float, m02: float,
                   m10: float, m11: float, m12: float,
                   m20: float, m21: float, m22: float) -> tuple:
    """Rotate 3D coordinates around origin (numba-optimized)."""
    # Translate to origin
    rx = x - ox
    ry = y - oy
    rz = z - oz
    
    # Apply rotation matrix
    nx = m00 * rx + m01 * ry + m02 * rz
    ny = m10 * rx + m11 * ry + m12 * rz
    nz = m20 * rx + m21 * ry + m22 * rz
    
    # Translate back
    return (nx + ox, ny + oy, nz + oz)


@jit(nopython=True)
def _zoom_coords(x: float, y: float, z: float, factor: float) -> tuple:
    """Zoom 3D coordinates from origin (numba-optimized)."""
    return (x * factor, y * factor, z * factor)


@jit(nopython=True)
def _distance_squared(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate squared distance between two 2D points (numba-optimized)."""
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy


@jit(nopython=True)
def _calculate_depth_param(z: float, depth: float) -> float:
    """Calculate depth parameter for color blending (numba-optimized)."""
    if z > depth:
        dz = z - depth
        if dz > MAX_Z:
            return MAX_PARAM
        return MIN_PARAM + (MAX_PARAM - MIN_PARAM) * dz / MAX_Z
    else:
        dz = depth - z
        if dz > MAX_Z:
            return MIN_PARAM
        return MAX_PARAM - (MAX_PARAM - MIN_PARAM) * dz / MAX_Z


@jit(nopython=True)
def _inverted_grey(r: float, g: float, b: float) -> tuple:
    """Calculate inverted grey color (numba-optimized)."""
    grey = 1.0 - (r + g + b) / 3.0
    return (grey, grey, grey)


class Atom:
    """
    3D atom representation with numba-accelerated geometric operations.
    """
    
    def __init__(self, size: float, symbol: Optional[str], annotation: Optional[str],
                 x: List[float], color: List[float]):
        self.size = size
        self.symbol = symbol if symbol else ""
        self.annotation = annotation if annotation else ""
        self.x = list(x) if isinstance(x, (list, tuple)) else [x[0], x[1], x[2]]
        self.color = list(color) if isinstance(color, (list, tuple)) else [color[0], color[1], color[2]]
        self.nbonds = 0
        self.bonds = []
        self.is_drawn = True
        self.have_annotation_color = False
        self.annotation_color = [0.0, 0.0, 0.0]
    
    def __repr__(self) -> str:
        return (f"Atom(symbol='{self.symbol}', size={self.size:.2f}, "
                f"pos=[{self.x[0]:.2f}, {self.x[1]:.2f}, {self.x[2]:.2f}], "
                f"nbonds={self.nbonds}, drawn={self.is_drawn})")


# C-style API functions
def new_atom(size: float, symbol: str, annotation: str,
             x: List[float], color: List[float]) -> Atom:
    """Create a new atom."""
    return Atom(size, symbol, annotation, x, color)


def delete_atom(atom: Atom) -> None:
    """Delete atom (cleanup)."""
    atom.bonds.clear()
    atom.nbonds = 0


def set_atom_size(atom: Atom, size: float) -> None:
    """Set atom size."""
    atom.size = size


def set_atom_symbol(atom: Atom, symbol: str) -> bool:
    """Set atom symbol."""
    if symbol is None:
        atom.symbol = ""
    else:
        atom.symbol = symbol
    return True


def set_atom_annotation(atom: Atom, annotation: str) -> bool:
    """Set atom annotation."""
    if annotation is None:
        atom.annotation = ""
    else:
        atom.annotation = annotation
    return True


def set_atom_color(atom: Atom, color: List[float]) -> None:
    """Set atom color."""
    atom.color = list(color)


def set_atom_annotation_color(atom: Atom, color: Optional[List[float]]) -> None:
    """Set custom annotation color."""
    if color is None:
        atom.have_annotation_color = False
        atom.annotation_color = [0.0, 0.0, 0.0]
    else:
        atom.have_annotation_color = True
        atom.annotation_color = list(color)


def show_atom(atom: Atom) -> None:
    """Make atom visible."""
    atom.is_drawn = True


def hide_atom(atom: Atom) -> None:
    """Make atom invisible."""
    atom.is_drawn = False


def toggle_atom(atom: Atom) -> None:
    """Toggle atom visibility."""
    atom.is_drawn = not atom.is_drawn


def add_bond_atom(atom: Atom, bond) -> bool:
    """Add bond to atom's bond list."""
    atom.bonds.append(bond)
    atom.nbonds += 1
    return True


def remove_bond_atom(atom: Atom, bond) -> bool:
    """Remove bond from atom's bond list."""
    try:
        # Search from end (C code does this assuming recent bonds removed first)
        for i in range(len(atom.bonds) - 1, -1, -1):
            if atom.bonds[i] == bond:
                # Fill gap with last element (order doesn't matter)
                atom.bonds[i] = atom.bonds[-1]
                atom.bonds.pop()
                atom.nbonds -= 1
                return True
        return False
    except (ValueError, IndexError):
        return False


def translate_atom(atom: Atom, delta: List[float]) -> None:
    """Translate atom position (numba-accelerated)."""
    nx, ny, nz = _translate_coords(atom.x[0], atom.x[1], atom.x[2],
                                    delta[0], delta[1], delta[2])
    atom.x = [nx, ny, nz]


def rotate_atom(atom: Atom, origin: List[float], matrix: List[List[float]]) -> None:
    """Rotate atom around origin (numba-accelerated)."""
    nx, ny, nz = _rotate_coords(
        atom.x[0], atom.x[1], atom.x[2],
        origin[0], origin[1], origin[2],
        matrix[0][0], matrix[0][1], matrix[0][2],
        matrix[1][0], matrix[1][1], matrix[1][2],
        matrix[2][0], matrix[2][1], matrix[2][2]
    )
    atom.x = [nx, ny, nz]


def zoom_atom(atom: Atom, factor: float) -> None:
    """Zoom atom from origin (numba-accelerated)."""
    nx, ny, nz = _zoom_coords(atom.x[0], atom.x[1], atom.x[2], factor)
    atom.x = [nx, ny, nz]


def set_coords_atom(atom: Atom, x: List[float]) -> None:
    """Set atom coordinates directly."""
    atom.x = list(x)


def draw_atom(atom: Atom, x_screen: float, y_screen: float, 
              param: float, grey: List[float]) -> None:
    """
    Draw atom (stub - requires drawing_funcs infrastructure).
    
    The C implementation uses drawing primitives to render the atom as:
    - Multiple concentric circles for 3D sphere effect
    - Depth-based color blending (param controls foreground/background)
    - Annotation text if present
    - Grey color for depth cueing
    """
    raise NotImplementedError("draw_atom requires drawing_funcs infrastructure")


def within_xy_tol_atom(atom: Atom, x: float, y: float, tol: float) -> bool:
    """Check if point is within tolerance of atom (2D) - numba-accelerated."""
    dist_sq = _distance_squared(atom.x[0], atom.x[1], x, y)
    tol_sq = tol * tol
    return dist_sq <= tol_sq


def get_depth_param_atom(atom: Atom, depth: float) -> float:
    """Get depth parameter for color blending (numba-accelerated)."""
    return _calculate_depth_param(atom.x[2], depth)


def inverted_grey_color(color: List[float]) -> List[float]:
    """Calculate inverted grey color (numba-accelerated)."""
    gr, gg, gb = _inverted_grey(color[0], color[1], color[2])
    return [gr, gg, gb]
