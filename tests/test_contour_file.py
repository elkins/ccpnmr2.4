"""
Tests for contour_file module - Contour caching and rendering

Tests cover:
- Contour file creation and validation
- Cache management
- Component handling
- Region drawing setup
- Block coordinate calculations
- C API compatibility
"""

import unittest
import sys
import os
import numpy as np

# Add path to python implementations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                '../ccpnmr2.4/python'))

from ccpnmr.analysis.python_impl.contour_file import (
    ContourFile,
    new_contour_file, delete_contour_file, region_contour_file
)
from ccpnmr.analysis.python_impl.contour_levels import ContourLevels


class MockBlockFile:
    """Mock block file for testing"""
    def __init__(self, ndim: int, points: np.ndarray, block_size: np.ndarray):
        self.ndim = ndim
        self.points = np.array(points, dtype=np.int32)
        self.block_size = np.array(block_size, dtype=np.int32)


class MockStoreFile:
    """Mock store file for testing"""
    def __init__(self, ndim: int, npoints: np.ndarray, block_size: np.ndarray,
                 first: np.ndarray, last: np.ndarray, 
                 have_neg: bool = True, have_pos: bool = True):
        self.ndim = ndim
        self.npoints = np.array(npoints, dtype=np.int32)
        self.block_size = np.array(block_size, dtype=np.int32)
        self.first = np.array(first, dtype=np.int32)
        self.last = np.array(last, dtype=np.int32)
        self.have_neg = have_neg
        self.have_pos = have_pos


class TestContourFileCreation(unittest.TestCase):
    """Test contour file creation and validation"""
    
    def test_create_with_block_file(self):
        """Test creating with block file"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        self.assertEqual(cf.xdim, 0)
        self.assertEqual(cf.ydim, 1)
        self.assertEqual(cf.block_file, block_file)
        self.assertIsNone(cf.store_file)
    
    def test_create_with_store_file(self):
        """Test creating with store file"""
        store_file = MockStoreFile(3, [128, 256, 512], [32, 32, 32],
                                   [0, 0, 0], [128, 256, 512])
        cf = ContourFile(0, 1, store_file=store_file)
        
        self.assertEqual(cf.xdim, 0)
        self.assertEqual(cf.ydim, 1)
        self.assertIsNone(cf.block_file)
        self.assertEqual(cf.store_file, store_file)
    
    def test_error_both_files(self):
        """Test error when both block and store files specified"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        store_file = MockStoreFile(3, [128, 256, 512], [32, 32, 32],
                                   [0, 0, 0], [128, 256, 512])
        
        with self.assertRaises(ValueError) as cm:
            ContourFile(0, 1, block_file=block_file, store_file=store_file)
        
        self.assertIn("both", str(cm.exception))
    
    def test_error_neither_file(self):
        """Test error when neither file specified"""
        with self.assertRaises(ValueError) as cm:
            ContourFile(0, 1)
        
        self.assertIn("neither", str(cm.exception))
    
    def test_error_xdim_negative(self):
        """Test error with negative xdim"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        
        with self.assertRaises(ValueError) as cm:
            ContourFile(-1, 1, block_file=block_file)
        
        self.assertIn("xdim", str(cm.exception))
    
    def test_error_xdim_too_large(self):
        """Test error with xdim >= ndim"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        
        with self.assertRaises(ValueError) as cm:
            ContourFile(3, 1, block_file=block_file)
        
        self.assertIn("xdim", str(cm.exception))
    
    def test_error_ydim_negative(self):
        """Test error with negative ydim"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        
        with self.assertRaises(ValueError) as cm:
            ContourFile(0, -1, block_file=block_file)
        
        self.assertIn("ydim", str(cm.exception))
    
    def test_error_ydim_too_large(self):
        """Test error with ydim >= ndim"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        
        with self.assertRaises(ValueError) as cm:
            ContourFile(0, 3, block_file=block_file)
        
        self.assertIn("ydim", str(cm.exception))
    
    def test_error_same_dimensions(self):
        """Test error when xdim == ydim"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        
        with self.assertRaises(ValueError) as cm:
            ContourFile(1, 1, block_file=block_file)
        
        self.assertIn("xdim = ydim", str(cm.exception))
    
    def test_transposed_flag(self):
        """Test transposed flag"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file, transposed=True)
        
        self.assertTrue(cf.transposed)


class TestContourFileCache(unittest.TestCase):
    """Test contour caching functionality"""
    
    def test_initial_cache_empty(self):
        """Test that cache is initially empty"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        self.assertEqual(len(cf.contour_table), 0)
    
    def test_clear_cache(self):
        """Test clearing cache"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        # Add some mock data to cache
        cf.contour_table[(0, 0, 0)] = "mock_data"
        cf.contour_table[(1, 0, 0)] = "mock_data2"
        
        self.assertEqual(len(cf.contour_table), 2)
        
        cf.clear_cache()
        
        self.assertEqual(len(cf.contour_table), 0)
    
    def test_clearing_flag(self):
        """Test that clearing flag is set during clear"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        self.assertFalse(cf.clearing)
        
        # Clearing flag is temporary during clear_cache
        cf.clear_cache()
        
        self.assertFalse(cf.clearing)


class TestContourFileComponents(unittest.TestCase):
    """Test component handling"""
    
    def test_initial_no_components(self):
        """Test initial state has no components"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        self.assertEqual(cf.ncomponents, 0)
        self.assertIsNone(cf.components)
    
    def test_set_components(self):
        """Test setting components"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        components = np.array([0, 2, 5])
        cf._set_components(3, components)
        
        self.assertEqual(cf.ncomponents, 3)
        np.testing.assert_array_equal(cf.components, [0, 2, 5])
    
    def test_equal_components_both_none(self):
        """Test equal components when both None"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        self.assertTrue(cf._equal_components(0, None))
    
    def test_equal_components_matching(self):
        """Test equal components when matching"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        components1 = np.array([0, 2, 5])
        cf._set_components(3, components1)
        
        components2 = np.array([0, 2, 5])
        self.assertTrue(cf._equal_components(3, components2))
    
    def test_equal_components_different(self):
        """Test unequal components"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        components1 = np.array([0, 2, 5])
        cf._set_components(3, components1)
        
        components2 = np.array([0, 2, 6])
        self.assertFalse(cf._equal_components(3, components2))
    
    def test_equal_components_different_lengths(self):
        """Test unequal components with different lengths"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        components1 = np.array([0, 2, 5])
        cf._set_components(3, components1)
        
        components2 = np.array([0, 2])
        self.assertFalse(cf._equal_components(2, components2))


class TestContourFileLevels(unittest.TestCase):
    """Test contour level handling"""
    
    def test_initial_no_levels(self):
        """Test initial state has no contour levels"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        self.assertIsNone(cf.contour_levels)
    
    def test_set_contour_levels(self):
        """Test setting contour levels"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        levels = ContourLevels(np.array([1.0, 2.0, 3.0]))
        cf.contour_levels = levels
        
        self.assertEqual(cf.contour_levels, levels)


class TestIndexConversion(unittest.TestCase):
    """Test index/array conversion"""
    
    def test_index_to_array_1d(self):
        """Test converting 1D index"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        shape = np.array([5])
        result = cf._index_to_array(3, shape)
        
        np.testing.assert_array_equal(result, [3])
    
    def test_index_to_array_2d(self):
        """Test converting 2D index"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        shape = np.array([3, 4])
        # Index 5 = row 1, col 1 (in row-major order)
        result = cf._index_to_array(5, shape)
        
        self.assertEqual(len(result), 2)
    
    def test_index_to_array_3d(self):
        """Test converting 3D index"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        shape = np.array([2, 3, 4])
        result = cf._index_to_array(0, shape)
        
        np.testing.assert_array_equal(result, [0, 0, 0])


class TestRegionContourFile(unittest.TestCase):
    """Test region contour drawing"""
    
    def test_region_basic(self):
        """Test basic region contour (no actual drawing)"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        first = np.array([0, 0, 0])
        last = np.array([64, 64, 64])
        levels = ContourLevels(np.array([1.0, 2.0]))
        
        # Should not raise error
        result = cf.region_contour_file(first, last, contour_levels=levels)
        self.assertTrue(result)
    
    def test_region_error_negative_first(self):
        """Test error with negative first coordinate"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        first = np.array([-1, 0, 0])
        last = np.array([64, 64, 64])
        levels = ContourLevels(np.array([1.0]))
        
        with self.assertRaises(ValueError):
            cf.region_contour_file(first, last, contour_levels=levels)
    
    def test_region_error_last_too_large(self):
        """Test error with last > points"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        first = np.array([0, 0, 0])
        last = np.array([200, 64, 64])  # 200 > 128
        levels = ContourLevels(np.array([1.0]))
        
        with self.assertRaises(ValueError):
            cf.region_contour_file(first, last, contour_levels=levels)
    
    def test_region_error_first_geq_last(self):
        """Test error when first >= last"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = ContourFile(0, 1, block_file=block_file)
        
        first = np.array([64, 0, 0])
        last = np.array([64, 64, 64])  # first[0] == last[0]
        levels = ContourLevels(np.array([1.0]))
        
        with self.assertRaises(ValueError):
            cf.region_contour_file(first, last, contour_levels=levels)


class TestCAPICompatibility(unittest.TestCase):
    """Test C API compatibility functions"""
    
    def test_new_contour_file(self):
        """Test new_contour_file function"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = new_contour_file(0, 1, block_file=block_file)
        
        self.assertIsInstance(cf, ContourFile)
        self.assertEqual(cf.xdim, 0)
        self.assertEqual(cf.ydim, 1)
    
    def test_delete_contour_file(self):
        """Test delete_contour_file function"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = new_contour_file(0, 1, block_file=block_file)
        
        # Should not raise error
        delete_contour_file(cf)
    
    def test_region_contour_file_function(self):
        """Test region_contour_file function"""
        block_file = MockBlockFile(3, [128, 256, 512], [32, 32, 32])
        cf = new_contour_file(0, 1, block_file=block_file)
        
        first = np.array([0, 0, 0])
        last = np.array([64, 64, 64])
        levels = ContourLevels(np.array([1.0, 2.0]))
        
        result = region_contour_file(cf, first, last, contour_levels=levels)
        self.assertTrue(result)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestContourFileCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestContourFileCache))
    suite.addTests(loader.loadTestsFromTestCase(TestContourFileComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestContourFileLevels))
    suite.addTests(loader.loadTestsFromTestCase(TestIndexConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestRegionContourFile))
    suite.addTests(loader.loadTestsFromTestCase(TestCAPICompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
