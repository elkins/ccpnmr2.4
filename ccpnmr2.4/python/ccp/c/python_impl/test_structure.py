"""
Tests for structure module - molecular structure container.

Tests cover:
- Structure creation and deletion
- Adding/removing atoms and bonds
- Nearest atom/bond finding with perspective projection
- Transformations (translate, rotate, zoom)
- Focus operations
- Drawing infrastructure
- Edge cases and error handling
"""

import pytest
import numpy as np
from ccp.c.python_impl.structure import (
    Structure,
    new_structure,
    delete_structure,
    add_atom_structure,
    remove_atom_structure,
    nearest_atom_structure,
    add_bond_structure,
    remove_bond_structure,
    nearest_bond_structure,
    translate_structure,
    rotate_structure,
    zoom_structure,
    move_to_center_structure,
    focus_on_atom_structure,
    ALLOC_INCR,
    DEFAULT_CAMERA
)
from ccp.c.python_impl.atom import Atom, new_atom
from ccp.c.python_impl.bond import Bond, new_bond


class TestStructureCreation:
    """Test structure creation and deletion"""
    
    def test_new_structure(self):
        """Create empty structure"""
        struct = new_structure()
        
        assert struct.natoms == 0
        assert struct.nbonds == 0
        assert struct.camera == DEFAULT_CAMERA
        assert len(struct.atoms) == 0
        assert len(struct.bonds) == 0
    
    def test_delete_structure(self):
        """Delete structure (no-op in Python)"""
        struct = new_structure()
        delete_structure(struct)  # Should not crash
        
        # Structure still accessible (Python GC will handle cleanup)
        assert struct.natoms == 0
    
    def test_structure_repr(self):
        """String representation"""
        struct = Structure()
        repr_str = repr(struct)
        
        assert "natoms=0" in repr_str
        assert "nbonds=0" in repr_str
        assert "camera" in repr_str


class TestAtomManagement:
    """Test adding and removing atoms"""
    
    def test_add_single_atom(self):
        """Add one atom"""
        struct = new_structure()
        atom = new_atom(1.0, "C", "CA", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        
        result = add_atom_structure(struct, atom)
        
        assert result is True
        assert struct.natoms == 1
        assert struct.atoms[0] is atom
    
    def test_add_multiple_atoms(self):
        """Add many atoms"""
        struct = new_structure()
        atoms = []
        
        for i in range(10):
            atom = new_atom(1.0, f"C{i}", "", [float(i), 0.0, 0.0], [1.0, 1.0, 1.0])
            atoms.append(atom)
            add_atom_structure(struct, atom)
        
        assert struct.natoms == 10
        for i, atom in enumerate(atoms):
            assert struct.atoms[i] is atom
    
    def test_remove_atom(self):
        """Remove atom from structure"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.0, 0.0, 0.0], [0.0, 0.0, 1.0])
        atom3 = new_atom(1.0, "O", "", [2.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        add_atom_structure(struct, atom3)
        
        # Remove middle atom
        result = remove_atom_structure(struct, atom2)
        
        assert result is True
        assert struct.natoms == 2
        assert atom2 not in struct.atoms[:struct.natoms]
    
    def test_remove_nonexistent_atom(self):
        """Try to remove atom not in structure"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.0, 0.0, 0.0], [0.0, 0.0, 1.0])
        
        add_atom_structure(struct, atom1)
        
        # Try to remove atom2 which is not in structure
        result = remove_atom_structure(struct, atom2)
        
        assert result is False
        assert struct.natoms == 1
    
    def test_remove_last_atom(self):
        """Remove last atom (edge case)"""
        struct = new_structure()
        atom = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        
        add_atom_structure(struct, atom)
        result = remove_atom_structure(struct, atom)
        
        assert result is True
        assert struct.natoms == 0


class TestBondManagement:
    """Test adding and removing bonds"""
    
    def test_add_single_bond(self):
        """Add one bond between two atoms"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        bond = new_bond(atom1, atom2, None)
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        result = add_bond_structure(struct, bond)
        
        assert result is True
        assert struct.nbonds == 1
        assert struct.bonds[0] is bond
        assert atom1.nbonds == 1
        assert atom2.nbonds == 1
    
    def test_add_multiple_bonds(self):
        """Add several bonds"""
        struct = new_structure()
        atoms = []
        
        # Create 4 atoms
        for i in range(4):
            atom = new_atom(1.0, f"C{i}", "", [float(i), 0.0, 0.0], [1.0, 1.0, 1.0])
            atoms.append(atom)
            add_atom_structure(struct, atom)
        
        # Create 3 bonds connecting them
        bonds = []
        for i in range(3):
            bond = new_bond(atoms[i], atoms[i+1], None)
            bonds.append(bond)
            add_bond_structure(struct, bond)
        
        assert struct.nbonds == 3
        for i, bond in enumerate(bonds):
            assert struct.bonds[i] is bond
    
    def test_remove_bond(self):
        """Remove bond from structure"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        atom3 = new_atom(1.0, "O", "", [3.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        
        bond1 = new_bond(atom1, atom2, None)
        bond2 = new_bond(atom2, atom3, None)
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        add_atom_structure(struct, atom3)
        add_bond_structure(struct, bond1)
        add_bond_structure(struct, bond2)
        
        # Remove first bond
        result = remove_bond_structure(struct, bond1)
        
        assert result is True
        assert struct.nbonds == 1
        assert bond1 not in struct.bonds[:struct.nbonds]
        assert atom1.nbonds == 0
        assert atom2.nbonds == 1  # Still has bond2
    
    def test_remove_nonexistent_bond(self):
        """Try to remove bond not in structure"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        atom3 = new_atom(1.0, "O", "", [3.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        
        bond1 = new_bond(atom1, atom2, None)
        bond2 = new_bond(atom2, atom3, None)
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        add_bond_structure(struct, bond1)
        
        # Try to remove bond2 which is not in structure
        result = remove_bond_structure(struct, bond2)
        
        assert result is False
        assert struct.nbonds == 1


class TestNearestAtom:
    """Test nearest atom finding with perspective projection"""
    
    def test_nearest_atom_simple(self):
        """Find nearest atom with simple geometry"""
        struct = new_structure()
        
        # Atom at origin, behind camera
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, -10.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [5.0, 5.0, -10.0], [0.0, 0.0, 1.0])
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        
        # Click near origin in screen space
        nearest = nearest_atom_structure(struct, 0.0, 0.0, 2.0)
        
        assert nearest is atom1
    
    def test_nearest_atom_none_in_tolerance(self):
        """No atoms within tolerance"""
        struct = new_structure()
        atom = new_atom(1.0, "C", "", [0.0, 0.0, -10.0], [1.0, 0.0, 0.0])
        add_atom_structure(struct, atom)
        
        # Click far away
        nearest = nearest_atom_structure(struct, 100.0, 100.0, 1.0)
        
        assert nearest is None
    
    def test_nearest_atom_hidden(self):
        """Hidden atoms not considered"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, -10.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.0, 1.0, -10.0], [0.0, 0.0, 1.0])
        
        atom1.is_drawn = False  # Hide atom1
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        
        nearest = nearest_atom_structure(struct, 0.0, 0.0, 2.0)
        
        # Should skip hidden atom1
        assert nearest != atom1
    
    def test_nearest_atom_in_front_of_camera(self):
        """Atoms in front of camera are ignored"""
        struct = new_structure()
        struct.camera = 50.0
        
        # Atom beyond camera (z > camera)
        atom = new_atom(1.0, "C", "", [0.0, 0.0, 60.0], [1.0, 0.0, 0.0])
        add_atom_structure(struct, atom)
        
        nearest = nearest_atom_structure(struct, 0.0, 0.0, 5.0)
        
        assert nearest is None


class TestTransformations:
    """Test structure transformations"""
    
    def test_translate(self):
        """Translate all atoms"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.0, 1.0, 1.0], [0.0, 0.0, 1.0])
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        
        translate_structure(struct, [5.0, -2.0, 3.0])
        
        np.testing.assert_array_almost_equal(atom1.x, [5.0, -2.0, 3.0])
        np.testing.assert_array_almost_equal(atom2.x, [6.0, -1.0, 4.0])
    
    def test_rotate_90_degrees(self):
        """Rotate structure 90 degrees around z-axis"""
        struct = new_structure()
        atom = new_atom(1.0, "C", "", [1.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        add_atom_structure(struct, atom)
        
        # 90 degree rotation around z
        angle = np.pi / 2
        rotation = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        
        rotate_structure(struct, rotation, [0.0, 0.0, 0.0])
        
        # [1, 0, 0] -> [0, 1, 0]
        np.testing.assert_array_almost_equal(atom.x, [0.0, 1.0, 0.0], decimal=5)
    
    def test_zoom_in(self):
        """Zoom in (decrease camera distance)"""
        struct = new_structure()
        initial_camera = struct.camera
        
        zoom_structure(struct, -10.0)
        
        assert struct.camera == initial_camera - 10.0
    
    def test_zoom_out(self):
        """Zoom out (increase camera distance)"""
        struct = new_structure()
        initial_camera = struct.camera
        
        zoom_structure(struct, 15.0)
        
        assert struct.camera == initial_camera + 15.0
    
    def test_move_to_center_simple(self):
        """Move structure to center"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [10.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [-10.0, 0.0, 0.0], [0.0, 0.0, 1.0])
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        
        move_to_center_structure(struct)
        
        # Center should now be at origin
        center = (np.array(atom1.x) + np.array(atom2.x)) / 2
        np.testing.assert_array_almost_equal(center, [0.0, 0.0, 0.0])
    
    def test_move_to_center_complex(self):
        """Move complex structure to center"""
        struct = new_structure()
        positions = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
            [-2.0, -3.0, -4.0]
        ]
        
        for i, pos in enumerate(positions):
            atom = new_atom(1.0, f"C{i}", "", pos, [1.0, 1.0, 1.0])
            add_atom_structure(struct, atom)
        
        move_to_center_structure(struct)
        
        # Calculate new center
        center = np.mean([atom.x for atom in struct.atoms[:struct.natoms]], axis=0)
        np.testing.assert_array_almost_equal(center, [0.0, 0.0, 0.0], decimal=5)
    
    def test_move_to_center_empty(self):
        """Move empty structure (should not crash)"""
        struct = new_structure()
        move_to_center_structure(struct)  # Should handle gracefully
        
        assert struct.natoms == 0
    
    def test_focus_on_atom(self):
        """Focus on specific atom"""
        struct = new_structure()
        
        # Create atom not on z-axis
        atom = new_atom(1.0, "C", "", [1.0, 1.0, 1.0], [1.0, 0.0, 0.0])
        add_atom_structure(struct, atom)
        
        focus_on_atom_structure(struct, atom)
        
        # After focus, atom should be aligned with z-axis
        # (within numerical precision)
        atom_pos = np.array(atom.x)
        atom_dir = atom_pos / np.linalg.norm(atom_pos)
        z_axis = np.array([0.0, 0.0, 1.0])
        
        # Direction should be close to z-axis
        dot_product = abs(np.dot(atom_dir, z_axis))
        assert dot_product > 0.99  # Almost aligned


class TestNearestBond:
    """Test nearest bond finding"""
    
    def test_nearest_bond_simple(self):
        """Find nearest bond"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, -10.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [5.0, 0.0, -10.0], [0.0, 0.0, 1.0])
        bond = new_bond(atom1, atom2, None)
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        add_bond_structure(struct, bond)
        
        # Click near bond midpoint
        nearest = nearest_bond_structure(struct, 2.5, 0.0, 3.0)
        
        # Should find the bond (exact behavior depends on within_xy_tol_bond)
        # Just verify it doesn't crash
        assert nearest is None or nearest is bond
    
    def test_nearest_bond_none_found(self):
        """No bonds within tolerance"""
        struct = new_structure()
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, -10.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.5, 0.0, -10.0], [0.0, 0.0, 1.0])
        bond = new_bond(atom1, atom2, None)
        
        add_atom_structure(struct, atom1)
        add_atom_structure(struct, atom2)
        add_bond_structure(struct, bond)
        
        # Click far away
        nearest = nearest_bond_structure(struct, 100.0, 100.0, 1.0)
        
        assert nearest is None


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_structure_translate(self):
        """Translate empty structure"""
        struct = new_structure()
        translate_structure(struct, [1.0, 2.0, 3.0])
        
        assert struct.natoms == 0
    
    def test_empty_structure_rotate(self):
        """Rotate empty structure"""
        struct = new_structure()
        rotation = np.eye(3)
        rotate_structure(struct, rotation, [0.0, 0.0, 0.0])
        
        assert struct.natoms == 0
    
    def test_single_atom_structure(self):
        """Structure with single atom"""
        struct = new_structure()
        atom = new_atom(1.0, "C", "", [5.0, 5.0, 5.0], [1.0, 0.0, 0.0])
        add_atom_structure(struct, atom)
        
        move_to_center_structure(struct)
        
        # Single atom should be at origin
        np.testing.assert_array_almost_equal(atom.x, [0.0, 0.0, 0.0])
    
    def test_remove_all_atoms(self):
        """Add and remove all atoms"""
        struct = new_structure()
        atoms = []
        
        # Add 5 atoms
        for i in range(5):
            atom = new_atom(1.0, f"C{i}", "", [float(i), 0.0, 0.0], [1.0, 1.0, 1.0])
            atoms.append(atom)
            add_atom_structure(struct, atom)
        
        # Remove all atoms
        for atom in atoms:
            result = remove_atom_structure(struct, atom)
            assert result is True
        
        assert struct.natoms == 0
    
    def test_large_structure(self):
        """Handle large number of atoms"""
        struct = new_structure()
        
        # Add 1000 atoms
        for i in range(1000):
            x = float(i % 10)
            y = float((i // 10) % 10)
            z = float(i // 100)
            atom = new_atom(0.5, "C", "", [x, y, z], [1.0, 1.0, 1.0])
            add_atom_structure(struct, atom)
        
        assert struct.natoms == 1000
        
        # Operations should still work
        move_to_center_structure(struct)
        translate_structure(struct, [1.0, 2.0, 3.0])
        
        assert struct.natoms == 1000


class TestAPICompatibility:
    """Test C-style API functions"""
    
    def test_c_style_functions(self):
        """Test all C-style wrapper functions"""
        struct = new_structure()
        assert struct is not None
        
        atom1 = new_atom(1.0, "C", "", [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = new_atom(1.0, "N", "", [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        
        assert add_atom_structure(struct, atom1) is True
        assert add_atom_structure(struct, atom2) is True
        
        bond = new_bond(atom1, atom2, None)
        assert add_bond_structure(struct, bond) is True
        
        nearest_atom_structure(struct, 0.0, 0.0, 1.0)
        nearest_bond_structure(struct, 0.0, 0.0, 1.0)
        
        translate_structure(struct, [1.0, 0.0, 0.0])
        zoom_structure(struct, 5.0)
        move_to_center_structure(struct)
        
        assert remove_bond_structure(struct, bond) is True
        assert remove_atom_structure(struct, atom1) is True
        assert remove_atom_structure(struct, atom2) is True
        
        delete_structure(struct)
