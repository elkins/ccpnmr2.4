"""
Pure Python implementation of bond.py matching the C extension API.

This module provides a molecular bond representation connecting two atoms
for NMR structure analysis, matching the C API from bond.h/bond.c.

The Bond class represents a bond between two atoms with:
- Two connected atoms
- Visual properties (color, line width, line style)
- Text annotation
- Drawing capabilities

This implementation is compatible with the atom module and can be used
as a drop-in replacement for the C extension.
"""

from typing import Optional, List, Any

# Constants matching C code
BOND_NCOLORS = 3
DEFAULT_BOND_WIDTH = 3.0

# Line style constants (from drawing_funcs.h)
NORMAL_LINE_STYLE = 0
DASHED_LINE_STYLE = 1
NLINE_STYLES = 2

# Depth perspective constants from C code
MAX_Z = 10.0
MIN_PARAM = 0.2
MAX_PARAM = 1.0
FIELD_DEPTH = -4.0
SMALL_D = 1.0e-3


class Bond:
    """
    Molecular bond between two atoms.
    
    Attributes:
        atom1: First atom in the bond
        atom2: Second atom in the bond
        have_color: Whether custom bond color is set
        color: RGB color values [r, g, b] in range 0.0-1.0
        line_width: Width of bond line in drawing
        line_style: Style of line (normal, dashed, etc.)
        annotation: Text label for the bond
    """
    
    def __init__(self, atom1: Any, atom2: Any, color: Optional[List[float]]):
        """
        Create a new Bond.
        
        Args:
            atom1: First atom
            atom2: Second atom
            color: RGB color [r, g, b] or None to use atom colors
        """
        self.atom1 = atom1
        self.atom2 = atom2
        self.have_color = False
        self.color = [0.0, 0.0, 0.0]
        self.line_width = -1.0  # Negative means use default
        self.line_style = NORMAL_LINE_STYLE
        self.annotation = ""
        
        # Set color after initialization
        if color is not None:
            self.have_color = True
            self.color = list(color)
    
    def __repr__(self) -> str:
        color_str = f"color={self.color}" if self.have_color else "atom colors"
        return (f"Bond(atom1={self.atom1.symbol if hasattr(self.atom1, 'symbol') else 'Atom'}, "
                f"atom2={self.atom2.symbol if hasattr(self.atom2, 'symbol') else 'Atom'}, "
                f"{color_str}, width={self.line_width:.1f})")


# C-style API functions

def new_bond(atom1: Any, atom2: Any, color: Optional[List[float]]) -> Bond:
    """
    Create a new Bond object.
    
    Args:
        atom1: First atom in the bond
        atom2: Second atom in the bond
        color: RGB color [r, g, b] or None to use atom colors
    
    Returns:
        New Bond instance
    """
    return Bond(atom1, atom2, color)


def delete_bond(bond: Bond) -> None:
    """
    Delete a bond (cleanup).
    
    In Python, this is mostly a no-op since garbage collection
    handles memory management. Included for API compatibility.
    
    Args:
        bond: Bond to delete
    """
    if bond:
        # Clear references to help garbage collection
        bond.atom1 = None
        bond.atom2 = None


def set_color_bond(bond: Bond, color: Optional[List[float]]) -> None:
    """
    Set the bond's color.
    
    If color is None, the bond will be drawn with a gradient
    using the two atom colors (half from each atom).
    
    Args:
        bond: Bond to modify
        color: RGB color [r, g, b] or None to use atom colors
    """
    if color is not None:
        bond.have_color = True
        bond.color = list(color)
    else:
        bond.have_color = False


def set_line_width_bond(bond: Bond, line_width: float) -> None:
    """
    Set the bond's line width.
    
    Args:
        bond: Bond to modify
        line_width: Width of bond line (negative uses default)
    """
    bond.line_width = line_width


def set_line_style_bond(bond: Bond, line_style: int) -> None:
    """
    Set the bond's line style.
    
    Args:
        bond: Bond to modify
        line_style: Style (0=normal, 1=dashed, etc.)
    """
    if 0 <= line_style < NLINE_STYLES:
        bond.line_style = line_style


def set_annotation_bond(bond: Bond, annotation: Optional[str]) -> bool:
    """
    Set the bond's annotation text.
    
    Args:
        bond: Bond to modify
        annotation: Text label for the bond
    
    Returns:
        True on success
    """
    bond.annotation = annotation if annotation else ""
    return True


def get_other_atom_bond(bond: Bond, atom: Any) -> Optional[Any]:
    """
    Get the other atom in a bond.
    
    Given one atom, returns the other atom in the bond.
    
    Args:
        bond: Bond to query
        atom: One of the atoms in the bond
    
    Returns:
        The other atom, or None if the given atom is not in this bond
    """
    if bond.atom1 is atom:
        return bond.atom2
    elif bond.atom2 is atom:
        return bond.atom1
    else:
        return None


def get_depth_param_bond(bond: Bond, depth: float) -> float:
    """
    Calculate depth-based blending parameter for color interpolation.
    
    Uses the midpoint z-coordinate of the two atoms relative to
    a depth plane for depth cueing.
    
    Args:
        bond: Bond to calculate parameter for
        depth: Reference depth plane
    
    Returns:
        Blending parameter (0.2 to 1.0)
    """
    z = 0.5 * (bond.atom1.x[2] + bond.atom2.x[2]) - depth
    z = max(-MAX_Z, min(MAX_Z, z))
    
    A = 0.5 * (MAX_PARAM + MIN_PARAM)
    B = 0.5 * (MAX_PARAM - MIN_PARAM) / MAX_Z
    
    return A + B * z


def draw_bond(bond: Bond, camera: float, depth: float,
              drawing_funcs: Any, data: Any) -> None:
    """
    Draw the bond using provided drawing functions.
    
    This is a stub implementation. Full drawing requires:
    - drawing_funcs object with methods: get_background, set_draw_color,
      set_line_width, set_line_style, draw_line, draw_text
    - Proper perspective transformation
    - Depth-based color blending
    
    The C code implements sophisticated 3D rendering with:
    - Perspective projection based on camera position
    - Depth cueing (color blending based on z-position)
    - Bi-color bonds (gradient from atom1 color to atom2 color)
    - Annotation text placement
    
    Args:
        bond: Bond to draw
        camera: Camera z-position for perspective
        depth: Depth plane for color blending
        drawing_funcs: Object with drawing methods
        data: Drawing context data
    """
    # Stub: Full implementation requires drawing_funcs module
    pass


def within_xy_tol_bond(bond: Bond, x: float, y: float, tol: float,
                       camera: float, z_out: List[float]) -> bool:
    """
    Check if a point (x, y) is within tolerance of the bond line.
    
    Uses perspective transformation and calculates the closest point
    on the bond line segment, then checks if the 2D distance is within
    tolerance.
    
    Args:
        bond: Bond to check
        x: X coordinate to test
        y: Y coordinate to test
        tol: Tolerance radius
        camera: Camera z-position for perspective
        z_out: Output list to store z-coordinate of closest point (modified in place)
    
    Returns:
        True if distance < tol, False otherwise
    """
    atom1 = bond.atom1
    atom2 = bond.atom2
    
    z1 = atom1.x[2]
    z2 = atom2.x[2]
    
    # Check if behind camera
    if z1 >= camera or z2 >= camera:
        return False
    
    # Perspective transform
    z1t = z1 - camera
    z2t = z2 - camera
    
    x1 = FIELD_DEPTH * atom1.x[0] / z1t
    y1 = FIELD_DEPTH * atom1.x[1] / z1t
    x2 = FIELD_DEPTH * atom2.x[0] / z2t
    y2 = FIELD_DEPTH * atom2.x[1] / z2t
    
    dx = x2 - x1
    dy = y2 - y1
    
    # Find closest point on line segment
    if abs(dx) < SMALL_D and abs(dy) < SMALL_D:
        # Points are on top of each other
        vx = x1
        vy = y1
        z_out[0] = max(z1, z2)
    else:
        # Project point onto line
        if abs(dx) > abs(dy):
            ax = -dy / dx
            py = -ax
            px = 1.0
            ay = 1.0
        else:
            py = 1.0
            ax = 1.0
            ay = -dx / dy
            px = -ay
        
        b = ax * x1 + ay * y1
        c = ax * x + ay * y
        
        det = ax * py - ay * px
        vx = (py * b - ay * c) / det
        vy = (-px * b + ax * c) / det
        
        # Calculate parameter along line segment
        lambda_val = (px * (vx - x1) + py * (vy - y1)) / (px * dx + py * dy)
        
        if lambda_val < 0:
            # Closest to atom1
            vx = x1
            vy = y1
            z_out[0] = z1
        elif lambda_val > 1:
            # Closest to atom2
            vx = x2
            vy = y2
            z_out[0] = z2
        else:
            # On the line segment
            z_out[0] = (1 - lambda_val) * z1 + lambda_val * z2
    
    # Check distance
    dx = x - vx
    dy = y - vy
    
    return (dx * dx + dy * dy) < (tol * tol)
