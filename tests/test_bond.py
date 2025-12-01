"""
Unit tests for bond.py (pure Python or C extension via wrapper).

These tests are implementation-agnostic - they work identically whether
the underlying implementation is pure Python or a C extension, as long
as the API matches the expected interface.

Run with:
    python3 tests/test_bond.py
    python3 -m unittest tests.test_bond
    python3 -m unittest tests.test_bond.TestBondBasics
"""

import unittest
import sys
import os
import importlib.util

# Import the wrapper module (tries pure Python first, then C extension)
# Handle the ccpnmr2.4 directory name with dots
wrapper_path = os.path.join(os.path.dirname(__file__), 
                           '..', 'ccpnmr2.4', 'c', 'ccp', 'structure', 'py_bond.py')
wrapper_path = os.path.abspath(wrapper_path)

spec = importlib.util.spec_from_file_location("py_bond", wrapper_path)
py_bond = importlib.util.module_from_spec(spec)
spec.loader.exec_module(py_bond)

# Also need atom for testing
atom_wrapper_path = os.path.join(os.path.dirname(__file__), 
                                '..', 'ccpnmr2.4', 'c', 'ccp', 'structure', 'py_atom.py')
atom_wrapper_path = os.path.abspath(atom_wrapper_path)

atom_spec = importlib.util.spec_from_file_location("py_atom", atom_wrapper_path)
py_atom = importlib.util.module_from_spec(atom_spec)
atom_spec.loader.exec_module(py_atom)


class TestBondBasics(unittest.TestCase):
    """Test basic bond creation and properties."""
    
    def test_bond_creation_with_color(self):
        """Test creating a bond with explicit color."""
        atom1 = py_atom.new_atom(1.0, 'C', 'C1', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        atom2 = py_atom.new_atom(1.0, 'N', 'N1', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, [1.0, 0.0, 0.0])
        
        self.assertIsNotNone(bond)
        self.assertEqual(bond.atom1, atom1)
        self.assertEqual(bond.atom2, atom2)
        self.assertTrue(bond.have_color)
        self.assertEqual(bond.color, [1.0, 0.0, 0.0])
    
    def test_bond_creation_without_color(self):
        """Test creating a bond without explicit color (uses atom colors)."""
        atom1 = py_atom.new_atom(1.0, 'C', 'C1', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        atom2 = py_atom.new_atom(1.0, 'N', 'N1', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        self.assertIsNotNone(bond)
        self.assertFalse(bond.have_color)
    
    def test_initial_properties(self):
        """Test initial bond properties."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        self.assertEqual(bond.line_width, -1.0)  # Default (negative)
        self.assertEqual(bond.line_style, py_bond.NORMAL_LINE_STYLE)
        self.assertEqual(bond.annotation, '')


class TestBondProperties(unittest.TestCase):
    """Test setting and modifying bond properties."""
    
    def setUp(self):
        """Create test atoms and bond for each test."""
        self.atom1 = py_atom.new_atom(1.0, 'C', 'C1', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        self.atom2 = py_atom.new_atom(1.0, 'N', 'N1', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        self.bond = py_bond.new_bond(self.atom1, self.atom2, None)
    
    def test_set_color(self):
        """Test setting bond color."""
        py_bond.set_color_bond(self.bond, [0.5, 0.5, 0.5])
        self.assertTrue(self.bond.have_color)
        self.assertEqual(self.bond.color, [0.5, 0.5, 0.5])
    
    def test_clear_color(self):
        """Test clearing bond color (use atom colors)."""
        py_bond.set_color_bond(self.bond, [0.5, 0.5, 0.5])
        self.assertTrue(self.bond.have_color)
        py_bond.set_color_bond(self.bond, None)
        self.assertFalse(self.bond.have_color)
    
    def test_set_line_width(self):
        """Test setting line width."""
        py_bond.set_line_width_bond(self.bond, 5.0)
        self.assertEqual(self.bond.line_width, 5.0)
    
    def test_set_line_width_negative(self):
        """Test setting negative line width (uses default)."""
        py_bond.set_line_width_bond(self.bond, -2.0)
        self.assertEqual(self.bond.line_width, -2.0)
    
    def test_set_line_style_normal(self):
        """Test setting normal line style."""
        py_bond.set_line_style_bond(self.bond, py_bond.NORMAL_LINE_STYLE)
        self.assertEqual(self.bond.line_style, py_bond.NORMAL_LINE_STYLE)
    
    def test_set_line_style_dashed(self):
        """Test setting dashed line style."""
        py_bond.set_line_style_bond(self.bond, py_bond.DASHED_LINE_STYLE)
        self.assertEqual(self.bond.line_style, py_bond.DASHED_LINE_STYLE)
    
    def test_set_line_style_invalid(self):
        """Test that invalid line styles are rejected."""
        original_style = self.bond.line_style
        py_bond.set_line_style_bond(self.bond, 999)  # Invalid
        self.assertEqual(self.bond.line_style, original_style)
    
    def test_set_annotation(self):
        """Test setting annotation text."""
        result = py_bond.set_annotation_bond(self.bond, 'C-N bond')
        self.assertTrue(result)
        self.assertEqual(self.bond.annotation, 'C-N bond')
    
    def test_set_annotation_empty(self):
        """Test setting empty annotation."""
        py_bond.set_annotation_bond(self.bond, '')
        self.assertEqual(self.bond.annotation, '')
    
    def test_set_annotation_none(self):
        """Test setting None annotation."""
        py_bond.set_annotation_bond(self.bond, None)
        self.assertEqual(self.bond.annotation, '')


class TestBondAtomQueries(unittest.TestCase):
    """Test querying atoms in bonds."""
    
    def test_get_other_atom_from_atom1(self):
        """Test getting other atom when given atom1."""
        atom1 = py_atom.new_atom(1.0, 'C', 'C1', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', 'N1', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        other = py_bond.get_other_atom_bond(bond, atom1)
        self.assertEqual(other, atom2)
    
    def test_get_other_atom_from_atom2(self):
        """Test getting other atom when given atom2."""
        atom1 = py_atom.new_atom(1.0, 'C', 'C1', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', 'N1', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        other = py_bond.get_other_atom_bond(bond, atom2)
        self.assertEqual(other, atom1)
    
    def test_get_other_atom_not_in_bond(self):
        """Test getting other atom with atom not in bond."""
        atom1 = py_atom.new_atom(1.0, 'C', 'C1', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', 'N1', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
        atom3 = py_atom.new_atom(1.0, 'O', 'O1', [3.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        other = py_bond.get_other_atom_bond(bond, atom3)
        self.assertIsNone(other)


class TestBondDepthParam(unittest.TestCase):
    """Test depth parameter calculation."""
    
    def test_depth_param_at_depth(self):
        """Test depth parameter at reference depth."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 5.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [1.5, 0.0, 5.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        param = py_bond.get_depth_param_bond(bond, 5.0)
        # At z=depth, param should be 0.6 (midpoint of 0.2 and 1.0)
        self.assertAlmostEqual(param, 0.6)
    
    def test_depth_param_far_forward(self):
        """Test depth parameter far in front."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 20.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [1.5, 0.0, 20.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        param = py_bond.get_depth_param_bond(bond, 0.0)
        # Far forward should give MAX_PARAM (1.0)
        self.assertAlmostEqual(param, 1.0)
    
    def test_depth_param_far_back(self):
        """Test depth parameter far behind."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, -20.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [1.5, 0.0, -20.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        param = py_bond.get_depth_param_bond(bond, 0.0)
        # Far back should give MIN_PARAM (0.2)
        self.assertAlmostEqual(param, 0.2)
    
    def test_depth_param_uses_midpoint(self):
        """Test that depth uses midpoint of two atoms."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [1.5, 0.0, 10.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        # Midpoint z is 5.0
        param = py_bond.get_depth_param_bond(bond, 5.0)
        self.assertAlmostEqual(param, 0.6)


class TestBondDistanceCheck(unittest.TestCase):
    """Test distance checking functions."""
    
    def test_within_xy_tol_on_bond(self):
        """Test point on the bond line."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, -5.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [10.0, 0.0, -5.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        z_out = [0.0]
        # Point on the line (midpoint in projected space)
        result = py_bond.within_xy_tol_bond(bond, 0.0, 0.0, 2.0, 0.0, z_out)
        self.assertTrue(result)
    
    def test_within_xy_tol_off_bond(self):
        """Test point far from bond line."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, -5.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [10.0, 0.0, -5.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        z_out = [0.0]
        # Point far from the line
        result = py_bond.within_xy_tol_bond(bond, 0.0, 100.0, 2.0, 0.0, z_out)
        self.assertFalse(result)
    
    def test_within_xy_tol_behind_camera(self):
        """Test that points behind camera return False."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, 5.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [10.0, 0.0, 5.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        z_out = [0.0]
        # Atoms at z=5, camera at z=0, so atoms are behind camera
        result = py_bond.within_xy_tol_bond(bond, 0.0, 0.0, 2.0, 0.0, z_out)
        self.assertFalse(result)
    
    def test_within_xy_tol_z_output(self):
        """Test that z_out is set correctly."""
        atom1 = py_atom.new_atom(1.0, 'C', '', [0.0, 0.0, -5.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', '', [10.0, 0.0, -10.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        z_out = [0.0]
        py_bond.within_xy_tol_bond(bond, 0.0, 0.0, 10.0, 0.0, z_out)
        # z_out should be set to something between -5 and -10
        self.assertTrue(-10.0 <= z_out[0] <= -5.0)


class TestBondIntegration(unittest.TestCase):
    """Test bonds working with atoms."""
    
    def test_bond_connects_atoms(self):
        """Test that bond properly connects two atoms."""
        atom1 = py_atom.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [0.5, 0.5, 0.5])
        atom2 = py_atom.new_atom(1.0, 'C', 'CB', [1.5, 0.0, 0.0], [0.5, 0.5, 0.5])
        
        # Create bond
        bond = py_bond.new_bond(atom1, atom2, [1.0, 1.0, 0.0])
        
        # Verify connectivity
        self.assertEqual(bond.atom1, atom1)
        self.assertEqual(bond.atom2, atom2)
        self.assertEqual(py_bond.get_other_atom_bond(bond, atom1), atom2)
        self.assertEqual(py_bond.get_other_atom_bond(bond, atom2), atom1)
    
    def test_bond_uses_atom_positions(self):
        """Test that bond depth calculation uses atom positions."""
        atom1 = py_atom.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 3.0], [1.0, 0.0, 0.0])
        atom2 = py_atom.new_atom(1.0, 'N', 'N', [1.5, 0.0, 7.0], [0.0, 0.0, 1.0])
        bond = py_bond.new_bond(atom1, atom2, None)
        
        # Depth param should use midpoint (z=5.0)
        param = py_bond.get_depth_param_bond(bond, 5.0)
        self.assertAlmostEqual(param, 0.6)
    
    def test_multiple_bonds_per_atom(self):
        """Test creating multiple bonds from same atom."""
        central = py_atom.new_atom(1.0, 'C', 'C', [0.0, 0.0, 0.0], [0.5, 0.5, 0.5])
        atom1 = py_atom.new_atom(1.0, 'H', 'H1', [1.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        atom2 = py_atom.new_atom(1.0, 'H', 'H2', [-1.0, 0.0, 0.0], [1.0, 1.0, 1.0])
        atom3 = py_atom.new_atom(1.0, 'H', 'H3', [0.0, 1.0, 0.0], [1.0, 1.0, 1.0])
        
        bond1 = py_bond.new_bond(central, atom1, None)
        bond2 = py_bond.new_bond(central, atom2, None)
        bond3 = py_bond.new_bond(central, atom3, None)
        
        # All bonds should be independent
        self.assertIsNotNone(bond1)
        self.assertIsNotNone(bond2)
        self.assertIsNotNone(bond3)
        
        # Each should connect to central
        self.assertEqual(py_bond.get_other_atom_bond(bond1, central), atom1)
        self.assertEqual(py_bond.get_other_atom_bond(bond2, central), atom2)
        self.assertEqual(py_bond.get_other_atom_bond(bond3, central), atom3)


class TestBondConstants(unittest.TestCase):
    """Test module constants."""
    
    def test_bond_ncolors(self):
        """Test BOND_NCOLORS constant."""
        self.assertEqual(py_bond.BOND_NCOLORS, 3)
    
    def test_default_bond_width(self):
        """Test DEFAULT_BOND_WIDTH constant."""
        self.assertEqual(py_bond.DEFAULT_BOND_WIDTH, 3.0)
    
    def test_line_style_constants(self):
        """Test line style constants."""
        self.assertEqual(py_bond.NORMAL_LINE_STYLE, 0)
        self.assertEqual(py_bond.DASHED_LINE_STYLE, 1)
        self.assertEqual(py_bond.NLINE_STYLES, 2)
    
    def test_depth_constants(self):
        """Test depth-related constants."""
        self.assertEqual(py_bond.MAX_Z, 10.0)
        self.assertEqual(py_bond.MIN_PARAM, 0.2)
        self.assertEqual(py_bond.MAX_PARAM, 1.0)
        self.assertEqual(py_bond.FIELD_DEPTH, -4.0)


class TestBondAPICompatibility(unittest.TestCase):
    """Test that all C API functions exist."""
    
    def test_all_functions_exist(self):
        """Verify all expected C-style API functions are present."""
        expected_functions = [
            'new_bond', 'delete_bond', 'set_color_bond', 'set_line_width_bond',
            'set_line_style_bond', 'set_annotation_bond', 'get_other_atom_bond',
            'draw_bond', 'within_xy_tol_bond', 'get_depth_param_bond'
        ]
        for func_name in expected_functions:
            self.assertTrue(hasattr(py_bond, func_name),
                          f"Function {func_name} not found")
            self.assertTrue(callable(getattr(py_bond, func_name)),
                          f"{func_name} is not callable")
    
    def test_bond_class_exists(self):
        """Verify Bond class exists."""
        self.assertTrue(hasattr(py_bond, 'Bond'))


if __name__ == '__main__':
    unittest.main()
