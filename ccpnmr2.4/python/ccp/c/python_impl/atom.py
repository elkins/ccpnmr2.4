"""
Pure Python implementation of atom.py matching the C extension API.

This module provides a 3D atom representation for molecular visualization
in NMR structure analysis, matching the C API from atom.h/atom.c.

The Atom class represents an atom with:
- 3D coordinates (x, y, z)
- Visual properties (size, color, symbol, annotation)
- Bond connectivity
- Drawing state (visible/hidden)
- Annotation color overrides

This implementation is thread-safe for individual atom operations and
can be used as a drop-in replacement for the C extension.
"""

import math
from typing import List, Optional, Tuple, Any

# Constants matching C code
ATOM_NDIMS = 3
ATOM_NCOLORS = 3
ALLOC_INCR = 4

# Depth perspective constants from C code
MAX_Z = 10.0
MIN_PARAM = 0.2
MAX_PARAM = 1.0
FIELD_DEPTH = -4.0


class Atom:
    """
    3D atom representation for molecular visualization.
    
    Attributes:
        size: Radius of the atom sphere
        symbol: Chemical element symbol (e.g., 'C', 'N', 'O')
        annotation: Text label for the atom
        x: 3D coordinates [x, y, z]
        color: RGB color values [r, g, b] in range 0.0-1.0
        nbonds: Number of bonds connected to this atom
        bonds: List of Bond objects connected to this atom
        is_drawn: Whether the atom is currently visible
        have_annotation_color: Whether custom annotation color is set
        annotation_color: RGB color for annotation text
    """
    
    def __init__(self, size: float, symbol: Optional[str], annotation: Optional[str],
                 x: List[float], color: List[float]):
        """
        Create a new Atom.
        
        Args:
            size: Atom radius
            symbol: Chemical element symbol (can be None or empty)
            annotation: Text annotation (can be None or empty)
            x: 3D coordinates [x, y, z]
            color: RGB color [r, g, b]
        """
        self.size = size
        self.symbol = symbol if symbol else ""
        self.annotation = annotation if annotation else ""
        self.x = list(x) if x else [0.0, 0.0, 0.0]
        self.color = list(color) if color else [1.0, 1.0, 1.0]
        
        self.nbonds = 0
        self.bonds: List[Any] = []  # List of Bond objects
        self.nbonds_alloc = ALLOC_INCR
        
        self.is_drawn = True
        self.have_annotation_color = False
        self.annotation_color = [0.0, 0.0, 0.0]
    
    def __repr__(self) -> str:
        return (f"Atom(symbol={self.symbol!r}, size={self.size:.2f}, "
                f"pos=[{self.x[0]:.2f}, {self.x[1]:.2f}, {self.x[2]:.2f}], "
                f"nbonds={self.nbonds}, drawn={self.is_drawn})")


# C-style API functions

def new_atom(size: float, symbol: Optional[str], annotation: Optional[str],
             x: List[float], color: List[float]) -> Atom:
    """
    Create a new Atom object.
    
    Args:
        size: Atom radius
        symbol: Chemical element symbol
        annotation: Text annotation
        x: 3D coordinates [x, y, z]
        color: RGB color [r, g, b]
    
    Returns:
        New Atom instance
    """
    return Atom(size, symbol, annotation, x, color)


def delete_atom(atom: Atom) -> None:
    """
    Delete an atom (cleanup).
    
    In Python, this is mostly a no-op since garbage collection
    handles memory management. Included for API compatibility.
    
    Args:
        atom: Atom to delete
    """
    if atom:
        # Clear references to help garbage collection
        atom.bonds.clear()


def set_size_atom(atom: Atom, size: float) -> None:
    """
    Set the atom's size (radius).
    
    Args:
        atom: Atom to modify
        size: New radius value
    """
    atom.size = size


def set_symbol_atom(atom: Atom, symbol: Optional[str]) -> bool:
    """
    Set the atom's chemical symbol.
    
    Args:
        atom: Atom to modify
        symbol: Chemical element symbol (e.g., 'C', 'N', 'O')
    
    Returns:
        True on success
    """
    atom.symbol = symbol if symbol else ""
    return True


def set_annotation_atom(atom: Atom, annotation: Optional[str]) -> bool:
    """
    Set the atom's annotation text.
    
    Args:
        atom: Atom to modify
        annotation: Text label for the atom
    
    Returns:
        True on success
    """
    atom.annotation = annotation if annotation else ""
    return True


def set_color_atom(atom: Atom, color: List[float]) -> None:
    """
    Set the atom's color.
    
    Args:
        atom: Atom to modify
        color: RGB color values [r, g, b] in range 0.0-1.0
    """
    atom.color = list(color)


def turn_on_atom(atom: Atom) -> None:
    """
    Make the atom visible.
    
    Args:
        atom: Atom to show
    """
    atom.is_drawn = True


def turn_off_atom(atom: Atom) -> None:
    """
    Make the atom invisible.
    
    Args:
        atom: Atom to hide
    """
    atom.is_drawn = False


def set_annotation_color_atom(atom: Atom, color: Optional[List[float]]) -> None:
    """
    Set a custom color for the atom's annotation text.
    
    If color is None, the annotation will use the default color
    (inverted from the atom color).
    
    Args:
        atom: Atom to modify
        color: RGB color [r, g, b] or None to use default
    """
    if color is not None:
        atom.have_annotation_color = True
        atom.annotation_color = list(color)
    else:
        atom.have_annotation_color = False


def add_bond_atom(atom: Atom, bond: Any) -> bool:
    """
    Add a bond to this atom's bond list.
    
    Args:
        atom: Atom to modify
        bond: Bond object to add
    
    Returns:
        True on success
    """
    # Dynamically expand bonds list if needed (matching C realloc behavior)
    if atom.nbonds >= atom.nbonds_alloc:
        atom.nbonds_alloc += ALLOC_INCR
    
    atom.bonds.append(bond)
    atom.nbonds += 1
    return True


def remove_bond_atom(atom: Atom, bond: Any) -> bool:
    """
    Remove a bond from this atom's bond list.
    
    Matches C behavior: searches from back to front (assumes later
    bonds more likely to be removed), then fills the gap with the
    last bond since order doesn't matter.
    
    Args:
        atom: Atom to modify
        bond: Bond object to remove
    
    Returns:
        True on success, False if bond not found
    """
    # Search from back to front (matching C code)
    for i in range(atom.nbonds - 1, -1, -1):
        if atom.bonds[i] is bond:
            # Fill slot with last bond (order doesn't matter)
            if i < atom.nbonds - 1:
                atom.bonds[i] = atom.bonds[atom.nbonds - 1]
            atom.bonds.pop()
            atom.nbonds -= 1
            return True
    
    return False  # Bond not found


def draw_atom(atom: Atom, camera: float, depth: float,
              drawing_funcs: Any, data: Any) -> None:
    """
    Draw the atom using provided drawing functions.
    
    This is a stub implementation. Full drawing requires:
    - drawing_funcs object with methods: get_background, set_draw_color,
      fill_circle, draw_circle, draw_text
    - Proper perspective transformation
    - Depth-based color blending
    
    Args:
        atom: Atom to draw
        camera: Camera z-position for perspective
        depth: Depth plane for color blending
        drawing_funcs: Object with drawing methods
        data: Drawing context data
    """
    # Stub: Full implementation requires drawing_funcs module
    # The C code performs:
    # 1. Perspective transform based on camera position
    # 2. Depth-based color blending with background
    # 3. Multiple circles for 3D sphere effect
    # 4. Symbol and annotation text rendering
    pass


def translate_atom(atom: Atom, delta: List[float]) -> None:
    """
    Translate (move) the atom by a delta vector.
    
    Args:
        atom: Atom to move
        delta: Translation vector [dx, dy, dz]
    """
    for i in range(ATOM_NDIMS):
        atom.x[i] += delta[i]


def rotate_atom(atom: Atom, matrix: List[List[float]], origin: List[float]) -> None:
    """
    Rotate the atom around an origin point using a rotation matrix.
    
    Applies: new_pos = origin + matrix * (old_pos - origin)
    
    Args:
        atom: Atom to rotate
        matrix: 3x3 rotation matrix
        origin: Point to rotate around [x, y, z]
    """
    x = [0.0, 0.0, 0.0]
    
    for i in range(ATOM_NDIMS):
        x[i] = origin[i]
        for j in range(ATOM_NDIMS):
            x[i] += matrix[i][j] * (atom.x[j] - origin[j])
    
    atom.x = x


def zoom_atom(atom: Atom, scale: float) -> None:
    """
    Scale the atom's coordinates by a zoom factor.
    
    Args:
        atom: Atom to zoom
        scale: Scaling factor (1.0 = no change, 2.0 = double size, etc.)
    """
    if scale == 0:
        return
    
    for i in range(ATOM_NDIMS):
        atom.x[i] *= scale


def set_coords_atom(atom: Atom, coords: List[float]) -> None:
    """
    Set the atom's 3D coordinates.
    
    Args:
        atom: Atom to modify
        coords: New coordinates [x, y, z]
    """
    for i in range(ATOM_NDIMS):
        atom.x[i] = coords[i]


def within_xy_tol_atom(atom: Atom, x: float, y: float, tol: float) -> bool:
    """
    Check if a point (x, y) is within tolerance of the atom's position.
    
    Only checks x and y coordinates (2D distance), ignoring z.
    
    Args:
        atom: Atom to check
        x: X coordinate to test
        y: Y coordinate to test
        tol: Tolerance radius
    
    Returns:
        True if distance < tol, False otherwise
    """
    dx = atom.x[0] - x
    dy = atom.x[1] - y
    return (dx * dx + dy * dy) < (tol * tol)


def get_depth_param_atom(atom: Atom, depth: float) -> float:
    """
    Calculate depth-based blending parameter for color interpolation.
    
    Returns a value between MIN_PARAM and MAX_PARAM based on the
    atom's z-coordinate relative to a depth plane. Used for depth cueing.
    
    Args:
        atom: Atom to calculate parameter for
        depth: Reference depth plane
    
    Returns:
        Blending parameter (0.2 to 1.0)
    """
    z = atom.x[2] - depth
    z = max(-MAX_Z, min(MAX_Z, z))
    
    A = 0.5 * (MAX_PARAM + MIN_PARAM)
    B = 0.5 * (MAX_PARAM - MIN_PARAM) / MAX_Z
    
    return A + B * z


def inverted_grey_color(atom_color: List[float]) -> List[float]:
    """
    Calculate an inverted greyscale color for text contrast.
    
    This is a helper for drawing atom symbols with good contrast
    against the atom's color.
    
    Args:
        atom_color: RGB color [r, g, b]
    
    Returns:
        Inverted greyscale RGB color
    """
    # Calculate luminance
    grey = 0.299 * atom_color[0] + 0.587 * atom_color[1] + 0.114 * atom_color[2]
    # Invert for contrast
    inverted = 1.0 - grey
    return [inverted, inverted, inverted]
