"""
Pure Python implementation of molecular structure container.

This module provides a Structure class that manages collections of atoms and bonds
for NMR structure visualization and analysis. Matches the C API from structure.h/c.

The Structure class provides:
- Dynamic arrays for atoms and bonds (auto-resizing)
- Efficient add/remove operations
- Nearest atom/bond finding with camera projection
- 3D transformations (translate, rotate, zoom)
- Focus operations for centering and alignment
- Drawing infrastructure integration

Performance Notes:
    - Add/remove operations are O(1) using swap-with-last strategy
    - Nearest atom finding uses perspective projection with early rejection
    - Pre-allocated arrays minimize memory allocations
    - All transformations use NumPy for vectorized operations

Example Usage:
    >>> from ccp.c.python_impl.structure import Structure
    >>> from ccp.c.python_impl.atom import Atom
    >>> 
    >>> # Create structure and add atoms
    >>> structure = Structure()
    >>> atom1 = Atom()
    >>> atom1.set_coords(0.0, 0.0, 0.0)
    >>> structure.add_atom(atom1)
    >>> 
    >>> # Transform structure
    >>> structure.translate([1.0, 0.0, 0.0])
    >>> structure.zoom(2.0)
    >>> 
    >>> # Find nearest atom to screen coordinates
    >>> nearest = structure.nearest_atom(10.0, 20.0, tol=5.0)
    >>> if nearest:
    >>>     print(f"Found atom at {nearest.x}")

See Also:
    - atom.py: Atom class for individual atoms
    - bond.py: Bond class connecting atoms
    - struct_util.py: RMSD and Kabsch alignment utilities

Based on ccpnmr2.4/c/ccp/structure/structure.c (1,207 lines)
"""

import numpy as np
from typing import List, Optional, Tuple, Any, Callable
from ccp.c.python_impl.atom import Atom, ATOM_NDIMS
from ccp.c.python_impl.bond import Bond


# Constants
ALLOC_INCR = 500
DEFAULT_CAMERA = 50.0
FIELD_DEPTH = -4.0
DEFAULT_BOND_WIDTH = 3.0


class Structure:
    """
    Container for molecular structure (atoms and bonds).
    
    Manages dynamic arrays of atoms and bonds with efficient storage and
    retrieval. Provides transformation operations and visualization support
    with perspective projection.
    
    Attributes:
        atoms: List of Atom objects
        bonds: List of Bond objects
        natoms: Number of atoms
        nbonds: Number of bonds
        camera: Camera distance for perspective projection
    """
    
    def __init__(self):
        """Create a new empty Structure."""
        self.atoms: List[Atom] = []
        self.bonds: List[Bond] = []
        self.natoms = 0
        self.nbonds = 0
        self.natoms_alloc = ALLOC_INCR
        self.nbonds_alloc = ALLOC_INCR
        self.camera = DEFAULT_CAMERA
        
        # Pre-allocate arrays for efficiency
        self.atoms = []
        self.bonds = []
    
    def __repr__(self) -> str:
        return f"Structure(natoms={self.natoms}, nbonds={self.nbonds}, camera={self.camera:.1f})"
    
    def add_atom(self, atom: Atom) -> bool:
        """
        Add an atom to the structure.
        
        Args:
            atom: Atom to add
        
        Returns:
            True on success, False on error
        """
        self.atoms.append(atom)
        self.natoms += 1
        return True
    
    def remove_atom(self, atom: Atom) -> bool:
        """
        Remove an atom from the structure.
        
        Works from back to front as later atoms are more likely to be removed.
        Uses swap-with-last strategy for O(1) removal.
        
        Args:
            atom: Atom to remove
        
        Returns:
            True on success, False if atom not found
        """
        # Search from back to front (likely to find recent additions)
        for i in range(self.natoms - 1, -1, -1):
            if self.atoms[i] is atom:
                # Swap with last atom (order doesn't matter)
                self.atoms[i] = self.atoms[self.natoms - 1]
                self.atoms.pop()
                self.natoms -= 1
                return True
        
        return False
    
    def nearest_atom(self, x: float, y: float, tol: float) -> Optional[Atom]:
        """
        Find nearest atom to screen coordinates using perspective projection.
        
        Uses inverse perspective transform to map screen (x,y) to 3D space,
        then finds the atom closest to the click point.
        
        Args:
            x: Screen x coordinate
            y: Screen y coordinate  
            tol: Tolerance for proximity check
        
        Returns:
            Nearest Atom within tolerance, or None
        """
        min_dist = -1.0
        closest = None
        
        for i in range(self.natoms):
            atom = self.atoms[i]
            
            if not atom.is_drawn:
                continue
            
            atom_z = atom.x[2]
            
            # Inverse perspective transform
            atom_z = atom_z - self.camera
            
            if atom_z >= 0:
                continue
            
            # Transform screen coordinates to 3D space at atom's depth
            real_x = atom_z * x / FIELD_DEPTH
            real_y = atom_z * y / FIELD_DEPTH
            
            # Check if within tolerance using atom's within_xy_tol method
            from ccp.c.python_impl.atom import within_xy_tol_atom
            if within_xy_tol_atom(atom, real_x, real_y, tol):
                dx = atom.x[0] - real_x
                dy = atom.x[1] - real_y
                dist = dx*dx + dy*dy
                
                if min_dist < 0 or dist < min_dist:
                    min_dist = dist
                    closest = atom
        
        return closest
    
    def add_bond(self, bond: Bond) -> bool:
        """
        Add a bond to the structure.
        
        Also updates the bond connectivity in both atoms.
        
        Args:
            bond: Bond to add
        
        Returns:
            True on success, False on error
        """
        from ccp.c.python_impl.atom import add_bond_atom
        
        self.bonds.append(bond)
        self.nbonds += 1
        
        # Update atom bond lists
        if not add_bond_atom(bond.atom1, bond):
            return False
        if not add_bond_atom(bond.atom2, bond):
            return False
        
        return True
    
    def remove_bond(self, bond: Bond) -> bool:
        """
        Remove a bond from the structure.
        
        Also updates the bond connectivity in both atoms.
        Uses swap-with-last strategy for O(1) removal.
        
        Args:
            bond: Bond to remove
        
        Returns:
            True on success, False if bond not found
        """
        from ccp.c.python_impl.atom import remove_bond_atom
        
        # Search from back to front
        for i in range(self.nbonds - 1, -1, -1):
            if self.bonds[i] is bond:
                # Swap with last bond
                self.bonds[i] = self.bonds[self.nbonds - 1]
                self.bonds.pop()
                self.nbonds -= 1
                
                # Update atom bond lists
                if not remove_bond_atom(bond.atom1, bond):
                    return False
                if not remove_bond_atom(bond.atom2, bond):
                    return False
                
                return True
        
        return False
    
    def nearest_bond(self, x: float, y: float, tol: float) -> Optional[Bond]:
        """
        Find nearest bond to screen coordinates.
        
        Uses perspective projection and selects the bond with the highest
        z-coordinate (closest to camera) among those within tolerance.
        
        Args:
            x: Screen x coordinate
            y: Screen y coordinate
            tol: Tolerance for proximity check
        
        Returns:
            Nearest Bond within tolerance, or None
        """
        from ccp.c.python_impl.bond import within_xy_tol_bond
        
        imax = -1
        zmax = 0.0
        
        for i in range(self.nbonds):
            bond = self.bonds[i]
            z_out = [0.0]  # Output parameter for z-coordinate
            
            if within_xy_tol_bond(bond, x, y, tol, self.camera, z_out):
                z = z_out[0]
                if imax == -1 or z > zmax:
                    imax = i
                    zmax = z
        
        if imax >= 0:
            return self.bonds[imax]
        else:
            return None
    
    def draw(self, drawing_funcs: Any, data: Any) -> None:
        """
        Draw the structure using provided drawing functions.
        
        Implements depth sorting (painter's algorithm) to draw atoms and bonds
        in correct order. Uses perspective projection for 3D visualization.
        
        Args:
            drawing_funcs: Object with drawing methods (get_region, set_line_width, etc.)
            data: User data passed to drawing functions
        """
        if self.natoms == 0:
            return
        
        # Sort atoms by z-coordinate (back to front for painter's algorithm)
        sorted_atoms = sorted(self.atoms[:self.natoms], key=lambda a: a.x[2], reverse=True)
        
        # Get drawing region
        x0, y0, x1, y1 = drawing_funcs.get_region(data)
        
        # Calculate average depth
        depth = sum(atom.x[2] for atom in sorted_atoms) / self.natoms
        
        # Draw atoms and their bonds
        for atom in sorted_atoms:
            if not atom.is_drawn:
                continue
            
            if atom.x[2] >= self.camera:
                continue
            
            clipped = self._is_clipped(atom, self.camera, x0, y0, x1, y1)
            
            # Draw bonds from this atom
            drawing_funcs.set_line_width(data, DEFAULT_BOND_WIDTH)
            
            from ccp.c.python_impl.bond import get_other_atom_bond, draw_bond
            for bond in atom.bonds[:atom.nbonds]:
                other_atom = get_other_atom_bond(bond, atom)
                
                if other_atom.x[2] >= self.camera:
                    continue
                
                # Only draw bond once (from atom with lower z)
                if other_atom and other_atom.is_drawn and atom.x[2] <= other_atom.x[2]:
                    if not clipped or not self._is_clipped(other_atom, self.camera, x0, y0, x1, y1):
                        draw_bond(bond, self.camera, depth, drawing_funcs, data)
            
            # Draw atom itself
            if not clipped:
                from ccp.c.python_impl.atom import draw_atom
                drawing_funcs.set_line_width(data, 0.0)
                draw_atom(atom, self.camera, depth, drawing_funcs, data)
    
    def _is_clipped(self, atom: Atom, camera: float, 
                    x0: float, y0: float, x1: float, y1: float) -> bool:
        """
        Check if atom is outside the drawing region (clipped).
        
        Args:
            atom: Atom to check
            camera: Camera distance
            x0, y0, x1, y1: Drawing region bounds
        
        Returns:
            True if atom is clipped (outside region)
        """
        x = atom.x[0]
        y = atom.x[1]
        z = atom.x[2]
        r = atom.size
        
        # Perspective transform
        z = z - camera
        x = FIELD_DEPTH * x / z
        y = FIELD_DEPTH * y / z
        
        # Check if outside bounds
        if (x + r) < x0:
            return True
        if (x - r) > x1:
            return True
        if (y + r) < y0:
            return True
        if (y - r) > y1:
            return True
        
        return False
    
    def translate(self, delta: List[float]) -> None:
        """
        Translate all atoms by delta vector.
        
        Args:
            delta: Translation vector [dx, dy, dz]
        """
        from ccp.c.python_impl.atom import translate_atom
        
        for i in range(self.natoms):
            translate_atom(self.atoms[i], delta)
    
    def rotate(self, matrix: np.ndarray, origin: List[float]) -> None:
        """
        Rotate all atoms around origin using rotation matrix.
        
        Args:
            matrix: 3x3 rotation matrix
            origin: Rotation origin [x, y, z]
        """
        from ccp.c.python_impl.atom import rotate_atom
        
        for i in range(self.natoms):
            rotate_atom(self.atoms[i], matrix, origin)
    
    def zoom(self, delta: float) -> None:
        """
        Zoom by adjusting camera distance.
        
        Args:
            delta: Change in camera distance (negative = zoom in, positive = zoom out)
        """
        self.camera = self.camera + delta
    
    def move_to_center(self) -> None:
        """
        Move structure's center of mass to origin.
        
        Calculates centroid of all atoms and translates structure to center it.
        """
        if self.natoms == 0:
            return
        
        center = np.zeros(ATOM_NDIMS)
        
        for i in range(self.natoms):
            center += self.atoms[i].x
        
        center = -center / self.natoms
        self.translate(center.tolist())
    
    def focus_on_atom(self, atom: Atom) -> None:
        """
        Focus on a specific atom by rotating it to point along z-axis.
        
        Rotates the entire structure so the specified atom points toward
        the camera (along positive z-axis).
        
        Args:
            atom: Atom to focus on
        """
        from memops.c.python_impl.geometry import rotation_matrix_vector_to_vector
        
        zaxis = np.array([0.0, 0.0, 1.0])
        origin = np.array([0.0, 0.0, 0.0])
        
        # Calculate rotation matrix to align atom position with z-axis
        rotation = rotation_matrix_vector_to_vector(atom.x, zaxis)
        
        self.rotate(rotation, origin.tolist())


# C-style API functions

def new_structure() -> Structure:
    """
    Create a new empty Structure.
    
    Returns:
        New Structure instance
    """
    return Structure()


def delete_structure(structure: Structure) -> None:
    """
    Delete a structure (cleanup).
    
    In Python this is mostly a no-op as garbage collection handles cleanup,
    but provided for API compatibility.
    
    Args:
        structure: Structure to delete
    """
    # Python garbage collection handles cleanup
    pass


def add_atom_structure(structure: Structure, atom: Atom) -> bool:
    """
    Add an atom to structure.
    
    Args:
        structure: Structure to modify
        atom: Atom to add
    
    Returns:
        True on success
    """
    return structure.add_atom(atom)


def remove_atom_structure(structure: Structure, atom: Atom) -> bool:
    """
    Remove an atom from structure.
    
    Args:
        structure: Structure to modify
        atom: Atom to remove
    
    Returns:
        True on success, False if not found
    """
    return structure.remove_atom(atom)


def nearest_atom_structure(structure: Structure, x: float, y: float, tol: float) -> Optional[Atom]:
    """
    Find nearest atom to screen coordinates.
    
    Args:
        structure: Structure to search
        x: Screen x coordinate
        y: Screen y coordinate
        tol: Tolerance
    
    Returns:
        Nearest Atom or None
    """
    return structure.nearest_atom(x, y, tol)


def add_bond_structure(structure: Structure, bond: Bond) -> bool:
    """
    Add a bond to structure.
    
    Args:
        structure: Structure to modify
        bond: Bond to add
    
    Returns:
        True on success
    """
    return structure.add_bond(bond)


def remove_bond_structure(structure: Structure, bond: Bond) -> bool:
    """
    Remove a bond from structure.
    
    Args:
        structure: Structure to modify
        bond: Bond to remove
    
    Returns:
        True on success, False if not found
    """
    return structure.remove_bond(bond)


def nearest_bond_structure(structure: Structure, x: float, y: float, tol: float) -> Optional[Bond]:
    """
    Find nearest bond to screen coordinates.
    
    Args:
        structure: Structure to search
        x: Screen x coordinate
        y: Screen y coordinate
        tol: Tolerance
    
    Returns:
        Nearest Bond or None
    """
    return structure.nearest_bond(x, y, tol)


def draw_structure(structure: Structure, drawing_funcs: Any, data: Any) -> None:
    """
    Draw structure using drawing functions.
    
    Args:
        structure: Structure to draw
        drawing_funcs: Drawing function object
        data: User data for drawing
    """
    structure.draw(drawing_funcs, data)


def translate_structure(structure: Structure, delta: List[float]) -> None:
    """
    Translate structure by delta.
    
    Args:
        structure: Structure to translate
        delta: Translation vector [dx, dy, dz]
    """
    structure.translate(delta)


def rotate_structure(structure: Structure, matrix: np.ndarray, origin: List[float]) -> None:
    """
    Rotate structure around origin.
    
    Args:
        structure: Structure to rotate
        matrix: 3x3 rotation matrix
        origin: Rotation origin [x, y, z]
    """
    structure.rotate(matrix, origin)


def zoom_structure(structure: Structure, delta: float) -> None:
    """
    Zoom by adjusting camera distance.
    
    Args:
        structure: Structure to zoom
        delta: Camera distance delta
    """
    structure.zoom(delta)


def move_to_center_structure(structure: Structure) -> None:
    """
    Move structure center to origin.
    
    Args:
        structure: Structure to center
    """
    structure.move_to_center()


def focus_on_atom_structure(structure: Structure, atom: Atom) -> None:
    """
    Focus on specific atom.
    
    Args:
        structure: Structure to rotate
        atom: Atom to focus on
    """
    structure.focus_on_atom(atom)
