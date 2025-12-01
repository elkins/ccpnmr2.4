"""
Unit tests for atom.py (pure Python or C extension via wrapper).

These tests are implementation-agnostic - they work identically whether
the underlying implementation is pure Python or a C extension, as long
as the API matches the expected interface.

Run with:
    python3 tests/test_atom.py
    python3 -m unittest tests.test_atom
    python3 -m unittest tests.test_atom.TestAtomBasics
"""

import unittest
import sys
import os
import importlib.util

# Import the wrapper module (tries pure Python first, then C extension)
# Handle the ccpnmr2.4 directory name with dots
wrapper_path = os.path.join(os.path.dirname(__file__), 
                           '..', 'ccpnmr2.4', 'c', 'ccp', 'structure', 'py_atom.py')
wrapper_path = os.path.abspath(wrapper_path)

spec = importlib.util.spec_from_file_location("py_atom", wrapper_path)
py_atom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(py_atom)


class TestAtomBasics(unittest.TestCase):
    """Test basic atom creation and properties."""
    
    def test_atom_creation(self):
        """Test creating a basic atom."""
        atom = py_atom.new_atom(1.5, 'C', 'CA', [1.0, 2.0, 3.0], [0.5, 0.5, 0.5])
        self.assertIsNotNone(atom)
        self.assertEqual(atom.size, 1.5)
        self.assertEqual(atom.symbol, 'C')
        self.assertEqual(atom.annotation, 'CA')
        self.assertEqual(atom.x, [1.0, 2.0, 3.0])
        self.assertEqual(atom.color, [0.5, 0.5, 0.5])
    
    def test_atom_with_none_strings(self):
        """Test creating atom with None for symbol/annotation."""
        atom = py_atom.new_atom(1.0, None, None, [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        self.assertIsNotNone(atom)
        self.assertEqual(atom.symbol, '')
        self.assertEqual(atom.annotation, '')
    
    def test_atom_with_empty_strings(self):
        """Test creating atom with empty strings."""
        atom = py_atom.new_atom(1.0, '', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        self.assertIsNotNone(atom)
        self.assertEqual(atom.symbol, '')
        self.assertEqual(atom.annotation, '')
    
    def test_initial_state(self):
        """Test initial atom state."""
        atom = py_atom.new_atom(1.0, 'N', 'N1', [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
        self.assertTrue(atom.is_drawn)
        self.assertEqual(atom.nbonds, 0)
        self.assertFalse(atom.have_annotation_color)


class TestAtomProperties(unittest.TestCase):
    """Test setting and modifying atom properties."""
    
    def test_set_size(self):
        """Test setting atom size."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.set_size_atom(atom, 2.5)
        self.assertEqual(atom.size, 2.5)
    
    def test_set_symbol(self):
        """Test setting chemical symbol."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        result = py_atom.set_symbol_atom(atom, 'N')
        self.assertTrue(result)
        self.assertEqual(atom.symbol, 'N')
    
    def test_set_symbol_to_none(self):
        """Test setting symbol to None."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.set_symbol_atom(atom, None)
        self.assertEqual(atom.symbol, '')
    
    def test_set_annotation(self):
        """Test setting annotation text."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        result = py_atom.set_annotation_atom(atom, 'CA')
        self.assertTrue(result)
        self.assertEqual(atom.annotation, 'CA')
    
    def test_set_annotation_unicode(self):
        """Test setting annotation with unicode."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.set_annotation_atom(atom, 'Cα')
        self.assertEqual(atom.annotation, 'Cα')
    
    def test_set_color(self):
        """Test setting atom color."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.set_color_atom(atom, [1.0, 0.0, 0.0])
        self.assertEqual(atom.color, [1.0, 0.0, 0.0])


class TestAtomVisibility(unittest.TestCase):
    """Test atom visibility control."""
    
    def test_turn_off_atom(self):
        """Test hiding atom."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        self.assertTrue(atom.is_drawn)
        py_atom.turn_off_atom(atom)
        self.assertFalse(atom.is_drawn)
    
    def test_turn_on_atom(self):
        """Test showing atom."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.turn_off_atom(atom)
        self.assertFalse(atom.is_drawn)
        py_atom.turn_on_atom(atom)
        self.assertTrue(atom.is_drawn)
    
    def test_toggle_visibility(self):
        """Test toggling visibility multiple times."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        for i in range(3):
            py_atom.turn_off_atom(atom)
            self.assertFalse(atom.is_drawn)
            py_atom.turn_on_atom(atom)
            self.assertTrue(atom.is_drawn)


class TestAtomAnnotationColor(unittest.TestCase):
    """Test custom annotation colors."""
    
    def test_set_annotation_color(self):
        """Test setting custom annotation color."""
        atom = py_atom.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        self.assertFalse(atom.have_annotation_color)
        py_atom.set_annotation_color_atom(atom, [1.0, 0.0, 0.0])
        self.assertTrue(atom.have_annotation_color)
        self.assertEqual(atom.annotation_color, [1.0, 0.0, 0.0])
    
    def test_clear_annotation_color(self):
        """Test clearing annotation color (None means use default)."""
        atom = py_atom.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.set_annotation_color_atom(atom, [1.0, 0.0, 0.0])
        self.assertTrue(atom.have_annotation_color)
        py_atom.set_annotation_color_atom(atom, None)
        self.assertFalse(atom.have_annotation_color)
    
    def test_change_annotation_color(self):
        """Test changing annotation color."""
        atom = py_atom.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        py_atom.set_annotation_color_atom(atom, [1.0, 0.0, 0.0])
        self.assertEqual(atom.annotation_color, [1.0, 0.0, 0.0])
        py_atom.set_annotation_color_atom(atom, [0.0, 1.0, 0.0])
        self.assertEqual(atom.annotation_color, [0.0, 1.0, 0.0])


class MockBond:
    """Mock Bond object for testing."""
    def __init__(self, id_num):
        self.id = id_num


class TestAtomBonds(unittest.TestCase):
    """Test bond management."""
    
    def test_add_bond(self):
        """Test adding a bond."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        bond = MockBond(1)
        result = py_atom.add_bond_atom(atom, bond)
        self.assertTrue(result)
        self.assertEqual(atom.nbonds, 1)
        self.assertEqual(atom.bonds[0], bond)
    
    def test_add_multiple_bonds(self):
        """Test adding multiple bonds."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        bonds = [MockBond(i) for i in range(5)]
        for bond in bonds:
            py_atom.add_bond_atom(atom, bond)
        self.assertEqual(atom.nbonds, 5)
        for i, bond in enumerate(bonds):
            self.assertIn(bond, atom.bonds)
    
    def test_remove_bond(self):
        """Test removing a bond."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        bond = MockBond(1)
        py_atom.add_bond_atom(atom, bond)
        result = py_atom.remove_bond_atom(atom, bond)
        self.assertTrue(result)
        self.assertEqual(atom.nbonds, 0)
    
    def test_remove_bond_not_present(self):
        """Test removing a bond that isn't in the list."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        bond1 = MockBond(1)
        bond2 = MockBond(2)
        py_atom.add_bond_atom(atom, bond1)
        result = py_atom.remove_bond_atom(atom, bond2)
        self.assertFalse(result)
        self.assertEqual(atom.nbonds, 1)
    
    def test_remove_bond_from_middle(self):
        """Test removing bond from middle of list."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        bonds = [MockBond(i) for i in range(5)]
        for bond in bonds:
            py_atom.add_bond_atom(atom, bond)
        
        # Remove middle bond
        result = py_atom.remove_bond_atom(atom, bonds[2])
        self.assertTrue(result)
        self.assertEqual(atom.nbonds, 4)
        self.assertNotIn(bonds[2], atom.bonds)
    
    def test_bond_allocation_growth(self):
        """Test that bond list grows dynamically."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        # Add more bonds than initial allocation
        bonds = [MockBond(i) for i in range(10)]
        for bond in bonds:
            result = py_atom.add_bond_atom(atom, bond)
            self.assertTrue(result)
        self.assertEqual(atom.nbonds, 10)


class TestAtomTransformations(unittest.TestCase):
    """Test geometric transformations."""
    
    def test_translate_atom(self):
        """Test translating atom position."""
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        py_atom.translate_atom(atom, [1.0, -1.0, 0.5])
        self.assertAlmostEqual(atom.x[0], 2.0)
        self.assertAlmostEqual(atom.x[1], 1.0)
        self.assertAlmostEqual(atom.x[2], 3.5)
    
    def test_translate_atom_zero(self):
        """Test translating by zero vector."""
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        original_x = list(atom.x)
        py_atom.translate_atom(atom, [0.0, 0.0, 0.0])
        self.assertEqual(atom.x, original_x)
    
    def test_set_coords(self):
        """Test setting coordinates directly."""
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        py_atom.set_coords_atom(atom, [5.0, 6.0, 7.0])
        self.assertEqual(atom.x, [5.0, 6.0, 7.0])
    
    def test_zoom_atom(self):
        """Test zooming atom position."""
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        py_atom.zoom_atom(atom, 2.0)
        self.assertAlmostEqual(atom.x[0], 2.0)
        self.assertAlmostEqual(atom.x[1], 4.0)
        self.assertAlmostEqual(atom.x[2], 6.0)
    
    def test_zoom_atom_zero(self):
        """Test zooming by zero (no-op)."""
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        original_x = list(atom.x)
        py_atom.zoom_atom(atom, 0.0)
        self.assertEqual(atom.x, original_x)
    
    def test_rotate_atom_identity(self):
        """Test rotation with identity matrix."""
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 2.0, 3.0], [1.0, 1.0, 1.0])
        identity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        origin = [0.0, 0.0, 0.0]
        py_atom.rotate_atom(atom, identity, origin)
        self.assertAlmostEqual(atom.x[0], 1.0)
        self.assertAlmostEqual(atom.x[1], 2.0)
        self.assertAlmostEqual(atom.x[2], 3.0)
    
    def test_rotate_atom_90_degrees_z(self):
        """Test 90-degree rotation around z-axis."""
        import math
        atom = py_atom.new_atom(1.0, 'C', '', [1.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        # 90-degree rotation around z-axis
        cos90 = math.cos(math.pi / 2)
        sin90 = math.sin(math.pi / 2)
        rotation = [
            [cos90, -sin90, 0.0],
            [sin90, cos90, 0.0],
            [0.0, 0.0, 1.0]
        ]
        origin = [0.0, 0.0, 0.0]
        py_atom.rotate_atom(atom, rotation, origin)
        # After 90-degree rotation, [1,0,0] becomes [0,1,0]
        self.assertAlmostEqual(atom.x[0], 0.0, places=5)
        self.assertAlmostEqual(atom.x[1], 1.0, places=5)
        self.assertAlmostEqual(atom.x[2], 0.0, places=5)


class TestAtomDistanceCheck(unittest.TestCase):
    """Test distance checking functions."""
    
    def test_within_xy_tol_exact(self):
        """Test point exactly at atom position."""
        atom = py_atom.new_atom(1.0, 'C', '', [5.0, 5.0, 0.0], [1.0, 1.0, 1.0])
        result = py_atom.within_xy_tol_atom(atom, 5.0, 5.0, 1.0)
        self.assertTrue(result)
    
    def test_within_xy_tol_inside(self):
        """Test point within tolerance."""
        atom = py_atom.new_atom(1.0, 'C', '', [5.0, 5.0, 0.0], [1.0, 1.0, 1.0])
        result = py_atom.within_xy_tol_atom(atom, 5.5, 5.5, 1.0)
        self.assertTrue(result)
    
    def test_within_xy_tol_outside(self):
        """Test point outside tolerance."""
        atom = py_atom.new_atom(1.0, 'C', '', [5.0, 5.0, 0.0], [1.0, 1.0, 1.0])
        result = py_atom.within_xy_tol_atom(atom, 10.0, 10.0, 1.0)
        self.assertFalse(result)
    
    def test_within_xy_tol_boundary(self):
        """Test point at boundary of tolerance."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        # Point at exactly distance = tol (should be False, since we test < not <=)
        result = py_atom.within_xy_tol_atom(atom, 1.0, 0.0, 1.0)
        self.assertFalse(result)
        # Slightly inside
        result = py_atom.within_xy_tol_atom(atom, 0.99, 0.0, 1.0)
        self.assertTrue(result)
    
    def test_within_xy_tol_ignores_z(self):
        """Test that z coordinate is ignored."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 100.0], [1.0, 1.0, 1.0])
        result = py_atom.within_xy_tol_atom(atom, 0.5, 0.5, 1.0)
        self.assertTrue(result)


class TestAtomHelperFunctions(unittest.TestCase):
    """Test helper functions."""
    
    def test_get_depth_param_at_depth(self):
        """Test depth parameter at reference depth."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 5.0], [1.0, 1.0, 1.0])
        param = py_atom.get_depth_param_atom(atom, 5.0)
        # At z=depth, param should be 0.6 (midpoint of 0.2 and 1.0)
        self.assertAlmostEqual(param, 0.6)
    
    def test_get_depth_param_far_forward(self):
        """Test depth parameter far in front."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 20.0], [1.0, 1.0, 1.0])
        param = py_atom.get_depth_param_atom(atom, 0.0)
        # Far forward (z >> depth) should give MAX_PARAM (1.0)
        self.assertAlmostEqual(param, 1.0)
    
    def test_get_depth_param_far_back(self):
        """Test depth parameter far behind."""
        atom = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, -20.0], [1.0, 1.0, 1.0])
        param = py_atom.get_depth_param_atom(atom, 0.0)
        # Far back (z << depth) should give MIN_PARAM (0.2)
        self.assertAlmostEqual(param, 0.2)
    
    def test_inverted_grey_color_white(self):
        """Test inverted grey for white."""
        result = py_atom.inverted_grey_color([1.0, 1.0, 1.0])
        # White (luminance=1.0) inverts to black (0.0)
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)
    
    def test_inverted_grey_color_black(self):
        """Test inverted grey for black."""
        result = py_atom.inverted_grey_color([0.0, 0.0, 0.0])
        # Black (luminance=0.0) inverts to white (1.0)
        self.assertAlmostEqual(result[0], 1.0, places=5)
        self.assertAlmostEqual(result[1], 1.0, places=5)
        self.assertAlmostEqual(result[2], 1.0, places=5)
    
    def test_inverted_grey_color_red(self):
        """Test inverted grey for red."""
        result = py_atom.inverted_grey_color([1.0, 0.0, 0.0])
        # Red has luminance ~0.299, inverts to ~0.701
        expected = 1.0 - 0.299
        self.assertAlmostEqual(result[0], expected, places=3)
        self.assertAlmostEqual(result[1], expected, places=3)
        self.assertAlmostEqual(result[2], expected, places=3)


class TestAtomConstants(unittest.TestCase):
    """Test module constants."""
    
    def test_atom_ndims(self):
        """Test ATOM_NDIMS constant."""
        self.assertEqual(py_atom.ATOM_NDIMS, 3)
    
    def test_atom_ncolors(self):
        """Test ATOM_NCOLORS constant."""
        self.assertEqual(py_atom.ATOM_NCOLORS, 3)
    
    def test_depth_constants(self):
        """Test depth-related constants."""
        self.assertEqual(py_atom.MAX_Z, 10.0)
        self.assertEqual(py_atom.MIN_PARAM, 0.2)
        self.assertEqual(py_atom.MAX_PARAM, 1.0)
        self.assertEqual(py_atom.FIELD_DEPTH, -4.0)


class TestAtomAPICompatibility(unittest.TestCase):
    """Test that all C API functions exist."""
    
    def test_all_functions_exist(self):
        """Verify all expected C-style API functions are present."""
        expected_functions = [
            'new_atom', 'delete_atom', 'set_size_atom', 'set_symbol_atom',
            'set_annotation_atom', 'set_color_atom', 'turn_on_atom',
            'turn_off_atom', 'set_annotation_color_atom', 'add_bond_atom',
            'remove_bond_atom', 'draw_atom', 'translate_atom', 'rotate_atom',
            'zoom_atom', 'set_coords_atom', 'within_xy_tol_atom',
            'get_depth_param_atom', 'inverted_grey_color'
        ]
        for func_name in expected_functions:
            self.assertTrue(hasattr(py_atom, func_name),
                          f"Function {func_name} not found")
            self.assertTrue(callable(getattr(py_atom, func_name)),
                          f"{func_name} is not callable")
    
    def test_atom_class_exists(self):
        """Verify Atom class exists."""
        self.assertTrue(hasattr(py_atom, 'Atom'))


if __name__ == '__main__':
    unittest.main()
