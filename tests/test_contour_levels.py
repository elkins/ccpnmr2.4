"""
Tests for contour_levels module - Contour level management

Tests cover:
- Contour level creation and ordering
- Copy operations
- Equality comparisons
- Negative/positive level detection
- Level retrieval
- C API compatibility
"""

import unittest
import sys
import os
import numpy as np

# Add path to python implementations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                '../ccpnmr2.4/python'))

from ccpnmr.analysis.python_impl.contour_levels import (
    ContourLevels,
    new_contour_levels, delete_contour_levels, copy_contour_levels,
    equal_contour_levels, have_neg_contour_levels, have_pos_contour_levels
)


class TestContourLevelsCreation(unittest.TestCase):
    """Test contour level creation and ordering"""
    
    def test_create_positive_only(self):
        """Test creating contour levels with only positive values"""
        levels = np.array([1.0, 2.0, 3.0, 4.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 4)
        np.testing.assert_array_equal(cl.levels, [1.0, 2.0, 3.0, 4.0])
    
    def test_create_negative_only(self):
        """Test creating contour levels with only negative values"""
        levels = np.array([-4.0, -3.0, -2.0, -1.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 4)
        # All negative, order preserved
        np.testing.assert_array_equal(cl.levels, [-4.0, -3.0, -2.0, -1.0])
    
    def test_create_mixed_ordered(self):
        """Test creating with mixed negative and positive (properly ordered)"""
        levels = np.array([-2.0, -1.0, 1.0, 2.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 4)
        # Should maintain: negative first, then positive
        np.testing.assert_array_equal(cl.levels, [-2.0, -1.0, 1.0, 2.0])
    
    def test_create_mixed_unordered(self):
        """Test that negative levels are sorted before positive"""
        levels = np.array([2.0, -1.0, 3.0, -2.0, 1.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 5)
        # Negative first [-1.0, -2.0], then positive [2.0, 3.0, 1.0]
        negative = cl.levels[cl.levels < 0]
        positive = cl.levels[cl.levels >= 0]
        
        # Check we have 2 negative and 3 positive
        self.assertEqual(len(negative), 2)
        self.assertEqual(len(positive), 3)
        
        # Check all negative come before positive
        first_negative = np.where(cl.levels < 0)[0]
        first_positive = np.where(cl.levels >= 0)[0]
        if len(first_negative) > 0 and len(first_positive) > 0:
            self.assertLess(first_negative[-1], first_positive[0])
    
    def test_create_with_zero(self):
        """Test creating with zero value (should be in positive group)"""
        levels = np.array([-1.0, 0.0, 1.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 3)
        # -1.0 first, then 0.0 and 1.0
        self.assertEqual(cl.levels[0], -1.0)
        self.assertIn(0.0, cl.levels[1:])
        self.assertIn(1.0, cl.levels[1:])
    
    def test_create_empty(self):
        """Test creating with empty array"""
        levels = np.array([])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 0)
        self.assertEqual(len(cl.levels), 0)
    
    def test_create_single_positive(self):
        """Test creating with single positive level"""
        levels = np.array([5.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 1)
        np.testing.assert_array_equal(cl.levels, [5.0])
    
    def test_create_single_negative(self):
        """Test creating with single negative level"""
        levels = np.array([-5.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 1)
        np.testing.assert_array_equal(cl.levels, [-5.0])


class TestContourLevelsCopy(unittest.TestCase):
    """Test copying contour levels"""
    
    def test_copy_simple(self):
        """Test copying contour levels"""
        levels = np.array([1.0, 2.0, 3.0])
        cl1 = ContourLevels(levels)
        cl2 = cl1.copy()
        
        self.assertEqual(cl1.nlevels, cl2.nlevels)
        np.testing.assert_array_equal(cl1.levels, cl2.levels)
    
    def test_copy_independence(self):
        """Test that copy is independent of original"""
        levels = np.array([1.0, 2.0, 3.0])
        cl1 = ContourLevels(levels)
        cl2 = cl1.copy()
        
        # Modify copy
        cl2.levels[0] = 999.0
        
        # Original should be unchanged
        self.assertEqual(cl1.levels[0], 1.0)
    
    def test_copy_mixed(self):
        """Test copying mixed negative/positive"""
        levels = np.array([-2.0, -1.0, 1.0, 2.0])
        cl1 = ContourLevels(levels)
        cl2 = cl1.copy()
        
        np.testing.assert_array_equal(cl1.levels, cl2.levels)


class TestContourLevelsEquality(unittest.TestCase):
    """Test equality comparisons"""
    
    def test_equal_same_values(self):
        """Test equality with same values"""
        levels1 = np.array([1.0, 2.0, 3.0])
        levels2 = np.array([1.0, 2.0, 3.0])
        
        cl1 = ContourLevels(levels1)
        cl2 = ContourLevels(levels2)
        
        self.assertTrue(cl1 == cl2)
    
    def test_equal_different_values(self):
        """Test inequality with different values"""
        levels1 = np.array([1.0, 2.0, 3.0])
        levels2 = np.array([1.0, 2.0, 4.0])
        
        cl1 = ContourLevels(levels1)
        cl2 = ContourLevels(levels2)
        
        self.assertFalse(cl1 == cl2)
    
    def test_equal_different_lengths(self):
        """Test inequality with different lengths"""
        levels1 = np.array([1.0, 2.0, 3.0])
        levels2 = np.array([1.0, 2.0])
        
        cl1 = ContourLevels(levels1)
        cl2 = ContourLevels(levels2)
        
        self.assertFalse(cl1 == cl2)
    
    def test_equal_empty(self):
        """Test equality of empty contour levels"""
        cl1 = ContourLevels(np.array([]))
        cl2 = ContourLevels(np.array([]))
        
        self.assertTrue(cl1 == cl2)
    
    def test_equal_not_contour_levels(self):
        """Test equality with non-ContourLevels object"""
        cl = ContourLevels(np.array([1.0, 2.0]))
        
        self.assertFalse(cl == [1.0, 2.0])
        self.assertFalse(cl == None)


class TestContourLevelsNegativePositive(unittest.TestCase):
    """Test negative/positive level detection"""
    
    def test_have_neg_true(self):
        """Test detecting negative levels when present"""
        levels = np.array([-1.0, 1.0, 2.0])
        cl = ContourLevels(levels)
        
        self.assertTrue(cl.have_neg_contour_levels())
    
    def test_have_neg_false(self):
        """Test detecting no negative levels"""
        levels = np.array([1.0, 2.0, 3.0])
        cl = ContourLevels(levels)
        
        self.assertFalse(cl.have_neg_contour_levels())
    
    def test_have_neg_only_negative(self):
        """Test with only negative levels"""
        levels = np.array([-3.0, -2.0, -1.0])
        cl = ContourLevels(levels)
        
        self.assertTrue(cl.have_neg_contour_levels())
    
    def test_have_pos_true(self):
        """Test detecting positive levels when present"""
        levels = np.array([-1.0, 1.0, 2.0])
        cl = ContourLevels(levels)
        
        self.assertTrue(cl.have_pos_contour_levels())
    
    def test_have_pos_false(self):
        """Test detecting no positive levels"""
        levels = np.array([-3.0, -2.0, -1.0])
        cl = ContourLevels(levels)
        
        self.assertFalse(cl.have_pos_contour_levels())
    
    def test_have_pos_only_positive(self):
        """Test with only positive levels"""
        levels = np.array([1.0, 2.0, 3.0])
        cl = ContourLevels(levels)
        
        self.assertTrue(cl.have_pos_contour_levels())
    
    def test_have_pos_with_zero(self):
        """Test that zero counts as positive"""
        levels = np.array([0.0])
        cl = ContourLevels(levels)
        
        self.assertTrue(cl.have_pos_contour_levels())
        self.assertFalse(cl.have_neg_contour_levels())
    
    def test_both_neg_and_pos(self):
        """Test with both negative and positive"""
        levels = np.array([-2.0, -1.0, 1.0, 2.0])
        cl = ContourLevels(levels)
        
        self.assertTrue(cl.have_neg_contour_levels())
        self.assertTrue(cl.have_pos_contour_levels())


class TestContourLevelsRetrieval(unittest.TestCase):
    """Test retrieving negative and positive levels"""
    
    def test_get_negative_levels(self):
        """Test getting only negative levels"""
        levels = np.array([-2.0, -1.0, 1.0, 2.0])
        cl = ContourLevels(levels)
        
        negative = cl.get_negative_levels()
        
        self.assertEqual(len(negative), 2)
        self.assertTrue(np.all(negative < 0))
        np.testing.assert_array_equal(np.sort(negative), [-2.0, -1.0])
    
    def test_get_positive_levels(self):
        """Test getting only positive levels"""
        levels = np.array([-2.0, -1.0, 1.0, 2.0])
        cl = ContourLevels(levels)
        
        positive = cl.get_positive_levels()
        
        self.assertEqual(len(positive), 2)
        self.assertTrue(np.all(positive >= 0))
        np.testing.assert_array_equal(np.sort(positive), [1.0, 2.0])
    
    def test_get_negative_empty(self):
        """Test getting negative levels when none exist"""
        levels = np.array([1.0, 2.0, 3.0])
        cl = ContourLevels(levels)
        
        negative = cl.get_negative_levels()
        
        self.assertEqual(len(negative), 0)
    
    def test_get_positive_empty(self):
        """Test getting positive levels when none exist"""
        levels = np.array([-3.0, -2.0, -1.0])
        cl = ContourLevels(levels)
        
        positive = cl.get_positive_levels()
        
        self.assertEqual(len(positive), 0)


class TestCAPICompatibility(unittest.TestCase):
    """Test C API compatibility functions"""
    
    def test_new_contour_levels(self):
        """Test new_contour_levels function"""
        levels = np.array([1.0, 2.0, 3.0])
        cl = new_contour_levels(levels)
        
        self.assertIsInstance(cl, ContourLevels)
        self.assertEqual(cl.nlevels, 3)
    
    def test_copy_contour_levels(self):
        """Test copy_contour_levels function"""
        levels = np.array([1.0, 2.0, 3.0])
        cl1 = new_contour_levels(levels)
        cl2 = copy_contour_levels(cl1)
        
        self.assertEqual(cl1.nlevels, cl2.nlevels)
        np.testing.assert_array_equal(cl1.levels, cl2.levels)
    
    def test_equal_contour_levels(self):
        """Test equal_contour_levels function"""
        levels1 = np.array([1.0, 2.0, 3.0])
        levels2 = np.array([1.0, 2.0, 3.0])
        levels3 = np.array([1.0, 2.0, 4.0])
        
        cl1 = new_contour_levels(levels1)
        cl2 = new_contour_levels(levels2)
        cl3 = new_contour_levels(levels3)
        
        self.assertTrue(equal_contour_levels(cl1, cl2))
        self.assertFalse(equal_contour_levels(cl1, cl3))
    
    def test_have_neg_contour_levels(self):
        """Test have_neg_contour_levels function"""
        levels_neg = np.array([-1.0, 1.0])
        levels_pos = np.array([1.0, 2.0])
        
        cl_neg = new_contour_levels(levels_neg)
        cl_pos = new_contour_levels(levels_pos)
        
        self.assertTrue(have_neg_contour_levels(cl_neg))
        self.assertFalse(have_neg_contour_levels(cl_pos))
    
    def test_have_pos_contour_levels(self):
        """Test have_pos_contour_levels function"""
        levels_pos = np.array([-1.0, 1.0])
        levels_neg = np.array([-2.0, -1.0])
        
        cl_pos = new_contour_levels(levels_pos)
        cl_neg = new_contour_levels(levels_neg)
        
        self.assertTrue(have_pos_contour_levels(cl_pos))
        self.assertFalse(have_pos_contour_levels(cl_neg))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special values"""
    
    def test_very_small_values(self):
        """Test with very small values"""
        levels = np.array([1e-10, -1e-10, 1e-9])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 3)
        self.assertTrue(cl.have_neg_contour_levels())
        self.assertTrue(cl.have_pos_contour_levels())
    
    def test_very_large_values(self):
        """Test with very large values"""
        levels = np.array([1e10, -1e10, 1e9])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 3)
    
    def test_duplicate_values(self):
        """Test with duplicate values"""
        levels = np.array([1.0, 1.0, 2.0, 2.0])
        cl = ContourLevels(levels)
        
        self.assertEqual(cl.nlevels, 4)
        # Duplicates are preserved
        self.assertEqual(np.count_nonzero(cl.levels == 1.0), 2)
        self.assertEqual(np.count_nonzero(cl.levels == 2.0), 2)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestContourLevelsCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestContourLevelsCopy))
    suite.addTests(loader.loadTestsFromTestCase(TestContourLevelsEquality))
    suite.addTests(loader.loadTestsFromTestCase(TestContourLevelsNegativePositive))
    suite.addTests(loader.loadTestsFromTestCase(TestContourLevelsRetrieval))
    suite.addTests(loader.loadTestsFromTestCase(TestCAPICompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
