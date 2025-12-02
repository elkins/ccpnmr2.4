"""
Tests for peak_list module - NMR peak collection management

Tests cover:
- Peak list creation and deletion
- Peak addition and removal
- Selection operations
- Peak search operations
- Region searches
- Nearest peak finding
- Peak picking algorithms
- Diagonal exclusions
- C API compatibility
"""

import unittest
import sys
import os
import numpy as np

# Add path to python implementations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                '../ccpnmr2.4/python'))

from ccpnmr.analysis.python_impl.peak_list import (
    PeakList, DiagonalExclusion,
    new_peak_list, delete_peak_list, is_selected_peak_list,
    set_color_peak_list, set_symbol_peak_list,
    add_peak_peak_list, remove_peak_peak_list,
    remove_selected_peak_list, unselect_selected_peak_list,
    search_region_peak_list, search_nearest_peak_list,
    determine_peak_scale, determine_peak_list_max
)
from ccpnmr.analysis.python_impl.peak import Peak


class MockBlockFile:
    """Mock block file for testing peak picking without actual data files"""
    
    def __init__(self, ndim: int, points: np.ndarray, 
                 data: np.ndarray = None, wrapped: np.ndarray = None):
        self.ndim = ndim
        self.points = np.array(points, dtype=np.int32)
        
        if data is None:
            # Create simple synthetic data with peaks
            shape = tuple(points)
            data = np.random.randn(*shape) * 0.1
            # Add a peak at center
            center = tuple(p // 2 for p in points)
            data[center] = 10.0
        
        self.data = data
        
        if wrapped is None:
            wrapped = np.zeros(ndim, dtype=bool)
        self.dim_wrapped = wrapped
    
    def get_point(self, point: np.ndarray) -> float:
        """Get intensity value at point"""
        idx = tuple(point.astype(int))
        return float(self.data[idx])
    
    def linewidth(self, find_maximum: bool, v: float, 
                 point: np.ndarray, dim: int) -> float:
        """Calculate linewidth at half-maximum"""
        # Simple mock implementation
        return 3.0  # Return constant linewidth


class TestPeakListBasics(unittest.TestCase):
    """Test basic peak list operations"""
    
    def test_create_1d_peak_list(self):
        """Test creating a 1D peak list"""
        npoints = np.array([1024])
        peak_list = PeakList(1, npoints)
        
        self.assertEqual(peak_list.ndim, 1)
        self.assertEqual(peak_list.npeaks, 0)
        np.testing.assert_array_equal(peak_list.npoints, npoints)
        np.testing.assert_array_equal(peak_list.color, [0, 0, 0])
    
    def test_create_2d_peak_list(self):
        """Test creating a 2D peak list"""
        npoints = np.array([512, 1024])
        peak_list = PeakList(2, npoints)
        
        self.assertEqual(peak_list.ndim, 2)
        self.assertEqual(peak_list.npeaks, 0)
        np.testing.assert_array_equal(peak_list.npoints, npoints)
    
    def test_create_3d_peak_list(self):
        """Test creating a 3D peak list"""
        npoints = np.array([128, 256, 512])
        peak_list = PeakList(3, npoints)
        
        self.assertEqual(peak_list.ndim, 3)
        self.assertEqual(peak_list.npeaks, 0)


class TestPeakListColor(unittest.TestCase):
    """Test peak list color operations"""
    
    def test_set_color(self):
        """Test setting peak list color"""
        peak_list = PeakList(2, np.array([512, 512]))
        color = np.array([1.0, 0.0, 0.0])  # Red
        
        peak_list.set_color_peak_list(color)
        np.testing.assert_array_equal(peak_list.color, color)
    
    def test_set_color_green(self):
        """Test setting green color"""
        peak_list = PeakList(2, np.array([512, 512]))
        color = np.array([0.0, 1.0, 0.0])
        
        peak_list.set_color_peak_list(color)
        np.testing.assert_array_almost_equal(peak_list.color, color)
    
    def test_color_copy(self):
        """Test that color is copied, not referenced"""
        peak_list = PeakList(2, np.array([512, 512]))
        color = np.array([0.5, 0.5, 0.5])
        
        peak_list.set_color_peak_list(color)
        color[0] = 1.0  # Modify original
        
        self.assertEqual(peak_list.color[0], 0.5)  # Should not change


class TestPeakListSymbol(unittest.TestCase):
    """Test peak list symbol operations"""
    
    def test_default_symbol(self):
        """Test default symbol is 0"""
        peak_list = PeakList(2, np.array([512, 512]))
        self.assertEqual(peak_list.symbol, 0)
    
    def test_set_symbol(self):
        """Test setting symbol"""
        peak_list = PeakList(2, np.array([512, 512]))
        result = peak_list.set_symbol_peak_list(3)
        
        self.assertTrue(result)
        self.assertEqual(peak_list.symbol, 3)


class TestPeakListAddRemove(unittest.TestCase):
    """Test adding and removing peaks"""
    
    def test_add_single_peak(self):
        """Test adding one peak"""
        peak_list = PeakList(2, np.array([512, 512]))
        peak = peak_list.add_peak_peak_list()
        
        self.assertIsNotNone(peak)
        self.assertEqual(peak_list.npeaks, 1)
        self.assertEqual(len(peak_list.peaks), 1)
        self.assertEqual(peak.ndim, 2)
    
    def test_add_multiple_peaks(self):
        """Test adding multiple peaks"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peaks = []
        for i in range(10):
            peak = peak_list.add_peak_peak_list()
            peaks.append(peak)
        
        self.assertEqual(peak_list.npeaks, 10)
        self.assertEqual(len(peak_list.peaks), 10)
    
    def test_add_many_peaks(self):
        """Test adding many peaks (test dynamic allocation)"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        for i in range(100):
            peak_list.add_peak_peak_list()
        
        self.assertEqual(peak_list.npeaks, 100)
    
    def test_remove_peak(self):
        """Test removing a specific peak"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak1 = peak_list.add_peak_peak_list()
        peak2 = peak_list.add_peak_peak_list()
        peak3 = peak_list.add_peak_peak_list()
        
        result = peak_list.remove_peak_peak_list(peak2)
        
        self.assertTrue(result)
        self.assertEqual(peak_list.npeaks, 2)
        self.assertIn(peak1, peak_list.peaks)
        self.assertNotIn(peak2, peak_list.peaks)
        self.assertIn(peak3, peak_list.peaks)
    
    def test_remove_nonexistent_peak(self):
        """Test removing a peak not in the list"""
        peak_list = PeakList(2, np.array([512, 512]))
        peak_list.add_peak_peak_list()
        
        other_peak = Peak(2)
        result = peak_list.remove_peak_peak_list(other_peak)
        
        self.assertFalse(result)
        self.assertEqual(peak_list.npeaks, 1)


class TestPeakListSelection(unittest.TestCase):
    """Test selection operations"""
    
    def test_select_all_peaks(self):
        """Test selecting all peaks"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        for i in range(5):
            peak_list.add_peak_peak_list()
        
        peak_list.is_selected_peak_list(True)
        
        for peak in peak_list.peaks:
            self.assertTrue(peak.get_is_selected())
    
    def test_unselect_all_peaks(self):
        """Test unselecting all peaks"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        for i in range(5):
            peak = peak_list.add_peak_peak_list()
            peak.set_is_selected(True)
        
        peak_list.is_selected_peak_list(False)
        
        for peak in peak_list.peaks:
            self.assertFalse(peak.get_is_selected())
    
    def test_unselect_selected(self):
        """Test unselect_selected_peak_list function"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peaks = []
        for i in range(5):
            peak = peak_list.add_peak_peak_list()
            peak.set_is_selected(i % 2 == 0)  # Select every other peak
            peaks.append(peak)
        
        peak_list.unselect_selected_peak_list()
        
        for peak in peak_list.peaks:
            self.assertFalse(peak.get_is_selected())
    
    def test_remove_selected_peaks(self):
        """Test removing selected peaks"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peaks = []
        for i in range(10):
            peak = peak_list.add_peak_peak_list()
            peak.set_is_selected(i % 2 == 0)  # Select every other peak
            peaks.append(peak)
        
        peak_list.remove_selected_peak_list()
        
        self.assertEqual(peak_list.npeaks, 5)  # Should have 5 remaining
        
        # Check that unselected peaks remain
        for i, peak in enumerate(peaks):
            if i % 2 == 0:
                self.assertNotIn(peak, peak_list.peaks)
            else:
                self.assertIn(peak, peak_list.peaks)


class TestSearchRegion(unittest.TestCase):
    """Test region search operations"""
    
    def test_search_empty_list(self):
        """Test searching in empty peak list"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        first = np.array([0.0, 0.0])
        last = np.array([100.0, 100.0])
        
        npeaks, indices = peak_list.search_region_peak_list(first, last)
        
        self.assertEqual(npeaks, 0)
        self.assertIsNone(indices)
    
    def test_search_region_finds_peaks(self):
        """Test finding peaks in a region"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        # Add peaks at different positions
        peak1 = peak_list.add_peak_peak_list()
        peak1.set_position(np.array([50.0, 50.0]))
        
        peak2 = peak_list.add_peak_peak_list()
        peak2.set_position(np.array([150.0, 150.0]))
        
        peak3 = peak_list.add_peak_peak_list()
        peak3.set_position(np.array([250.0, 250.0]))
        
        # Search region that should contain first two peaks
        first = np.array([0.0, 0.0])
        last = np.array([200.0, 200.0])
        
        npeaks, indices = peak_list.search_region_peak_list(first, last)
        
        self.assertEqual(npeaks, 2)
        self.assertEqual(len(indices), 2)
        np.testing.assert_array_equal(indices, [0, 1])
    
    def test_search_region_no_peaks(self):
        """Test searching region with no peaks"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak = peak_list.add_peak_peak_list()
        peak.set_position(np.array([300.0, 300.0]))
        
        first = np.array([0.0, 0.0])
        last = np.array([100.0, 100.0])
        
        npeaks, indices = peak_list.search_region_peak_list(first, last)
        
        self.assertEqual(npeaks, 0)
        self.assertIsNone(indices)


class TestSearchNearest(unittest.TestCase):
    """Test nearest peak search"""
    
    def test_search_nearest_empty_list(self):
        """Test searching nearest in empty list"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        first = np.array([0.0, 0.0])
        last = np.array([100.0, 100.0])
        
        index, d2 = peak_list.search_nearest_peak_list(
            0, 1, 1.0, 1.0, first, last
        )
        
        self.assertEqual(index, -1)
    
    def test_search_nearest_finds_peak(self):
        """Test finding nearest peak"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        # Add peaks
        peak1 = peak_list.add_peak_peak_list()
        peak1.set_position(np.array([100.0, 100.0]))
        peak1.set_intensity(1.0)
        
        peak2 = peak_list.add_peak_peak_list()
        peak2.set_position(np.array([200.0, 200.0]))
        peak2.set_intensity(1.0)
        
        # Search region closer to first peak
        first = np.array([95.0, 95.0])
        last = np.array([105.0, 105.0])
        
        index, d2 = peak_list.search_nearest_peak_list(
            0, 1, 1.0, 1.0, first, last
        )
        
        self.assertEqual(index, 0)  # Should find peak1
        self.assertGreaterEqual(d2, 0.0)


class TestDetermineMax(unittest.TestCase):
    """Test maximum intensity/volume determination"""
    
    def test_empty_list_max(self):
        """Test max values for empty list"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        intensity_max, volume_max = peak_list.determine_peak_list_max()
        
        self.assertEqual(intensity_max, 0.0)
        self.assertEqual(volume_max, 0.0)
    
    def test_determine_intensity_max(self):
        """Test finding maximum intensity"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        for i in range(5):
            peak = peak_list.add_peak_peak_list()
            peak.set_intensity(float(i + 1) * 10.0)
            peak.set_volume(0.0)
        
        intensity_max, volume_max = peak_list.determine_peak_list_max()
        
        self.assertEqual(intensity_max, 50.0)
        self.assertEqual(volume_max, 0.0)
    
    def test_determine_volume_max(self):
        """Test finding maximum volume"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        for i in range(5):
            peak = peak_list.add_peak_peak_list()
            peak.set_intensity(0.0)
            peak.set_volume(float(i + 1) * 100.0)
        
        intensity_max, volume_max = peak_list.determine_peak_list_max()
        
        self.assertEqual(intensity_max, 0.0)
        self.assertEqual(volume_max, 500.0)
    
    def test_determine_both_max(self):
        """Test finding both intensity and volume max"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak1 = peak_list.add_peak_peak_list()
        peak1.set_intensity(100.0)
        peak1.set_volume(50.0)
        
        peak2 = peak_list.add_peak_peak_list()
        peak2.set_intensity(50.0)
        peak2.set_volume(200.0)
        
        intensity_max, volume_max = peak_list.determine_peak_list_max()
        
        self.assertEqual(intensity_max, 100.0)
        self.assertEqual(volume_max, 200.0)
    
    def test_negative_values(self):
        """Test with negative intensity/volume (absolute values)"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak = peak_list.add_peak_peak_list()
        peak.set_intensity(-100.0)
        peak.set_volume(-200.0)
        
        intensity_max, volume_max = peak_list.determine_peak_list_max()
        
        self.assertEqual(intensity_max, 100.0)
        self.assertEqual(volume_max, 200.0)


class TestPeakScale(unittest.TestCase):
    """Test peak scale determination"""
    
    def test_peak_scale_zero_values(self):
        """Test scale with zero intensity/volume"""
        peak = Peak(2)
        peak.set_intensity(0.0)
        peak.set_volume(0.0)
        
        scale = PeakList._determine_peak_scale(peak, 100.0, 100.0)
        
        self.assertEqual(scale, 0.5)  # Arbitrary default
    
    def test_peak_scale_at_maximum(self):
        """Test scale at maximum"""
        peak = Peak(2)
        peak.set_volume(100.0)
        
        scale = PeakList._determine_peak_scale(peak, 50.0, 100.0)
        
        self.assertEqual(scale, 1.0)
    
    def test_peak_scale_above_maximum(self):
        """Test scale above maximum"""
        peak = Peak(2)
        peak.set_volume(150.0)
        
        scale = PeakList._determine_peak_scale(peak, 50.0, 100.0)
        
        self.assertEqual(scale, 1.0)
    
    def test_peak_scale_logarithmic(self):
        """Test logarithmic scaling"""
        peak = Peak(2)
        peak.set_volume(10.0)
        
        scale = PeakList._determine_peak_scale(peak, 50.0, 100.0)
        
        # For very small values log10(10/100) = log10(0.1) = -1.0
        # scale = 1 / (1 - (-1)) = 1/2 = 0.5
        # So scale will be close to 0.5 for this case
        self.assertGreaterEqual(scale, 0.5)
        self.assertLessEqual(scale, 1.0)


class TestDiagonalExclusion(unittest.TestCase):
    """Test diagonal exclusion for peak picking"""
    
    def test_create_diagonal_exclusion(self):
        """Test creating diagonal exclusion"""
        de = DiagonalExclusion(0, 1, 1.0, 1.0, 0.0, 5.0)
        
        self.assertEqual(de.dim1, 0)
        self.assertEqual(de.dim2, 1)
        self.assertEqual(de.a1, 1.0)
        self.assertEqual(de.a2, 1.0)
        self.assertEqual(de.b12, 0.0)
        self.assertEqual(de.d, 5.0)
    
    def test_diagonal_exclusion_different_params(self):
        """Test diagonal exclusion with different parameters"""
        de = DiagonalExclusion(1, 2, 2.0, 1.5, 10.0, 3.0)
        
        self.assertEqual(de.dim1, 1)
        self.assertEqual(de.dim2, 2)
        self.assertEqual(de.a1, 2.0)
        self.assertEqual(de.a2, 1.5)


class TestHelperMethods(unittest.TestCase):
    """Test internal helper methods"""
    
    def test_find_point_1d(self):
        """Test converting linear index to point in 1D"""
        peak_list = PeakList(1, np.array([100]))
        
        cum_points = np.array([1])
        offset = np.array([10])
        
        point = peak_list._find_point(5, cum_points, offset)
        
        np.testing.assert_array_equal(point, [15])
    
    def test_find_point_2d(self):
        """Test converting linear index to point in 2D"""
        peak_list = PeakList(2, np.array([100, 200]))
        
        cum_points = np.array([1, 10])
        offset = np.array([0, 0])
        
        # Index 15 should give (1, 5) with cum_points structure
        point = peak_list._find_point(15, cum_points, offset)
        
        self.assertEqual(len(point), 2)
    
    def test_peak_within_buffer_true(self):
        """Test peak within buffer returns True"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak = Peak(2)
        peak.set_position(np.array([100.0, 100.0]))
        
        point = np.array([101, 101])
        buffer = np.array([5, 5])
        
        result = peak_list._peak_within_buffer(point, peak, buffer)
        
        self.assertTrue(result)
    
    def test_peak_within_buffer_false(self):
        """Test peak outside buffer returns False"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak = Peak(2)
        peak.set_position(np.array([100.0, 100.0]))
        
        point = np.array([120, 120])
        buffer = np.array([5, 5])
        
        result = peak_list._peak_within_buffer(point, peak, buffer)
        
        self.assertFalse(result)
    
    def test_check_new_peak_empty_list(self):
        """Test checking new peak with empty list"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        buffer = np.array([5, 5])
        point = np.array([100, 100])
        
        result = peak_list._check_new_peak(buffer, point, -1)
        
        self.assertTrue(result)
    
    def test_check_new_peak_too_close(self):
        """Test checking new peak too close to existing"""
        peak_list = PeakList(2, np.array([512, 512]))
        
        peak = peak_list.add_peak_peak_list()
        peak.set_position(np.array([100.0, 100.0]))
        
        buffer = np.array([5, 5])
        point = np.array([102, 102])
        
        result = peak_list._check_new_peak(buffer, point, -1)
        
        self.assertFalse(result)


class TestCAPICompatibility(unittest.TestCase):
    """Test C API compatibility functions"""
    
    def test_new_peak_list_function(self):
        """Test new_peak_list function"""
        npoints = np.array([512, 512])
        peak_list = new_peak_list(2, npoints)
        
        self.assertIsInstance(peak_list, PeakList)
        self.assertEqual(peak_list.ndim, 2)
    
    def test_add_peak_function(self):
        """Test add_peak_peak_list function"""
        peak_list = new_peak_list(2, np.array([512, 512]))
        peak = add_peak_peak_list(peak_list)
        
        self.assertIsInstance(peak, Peak)
        self.assertEqual(peak_list.npeaks, 1)
    
    def test_remove_peak_function(self):
        """Test remove_peak_peak_list function"""
        peak_list = new_peak_list(2, np.array([512, 512]))
        peak = add_peak_peak_list(peak_list)
        
        result = remove_peak_peak_list(peak_list, peak)
        
        self.assertTrue(result)
        self.assertEqual(peak_list.npeaks, 0)
    
    def test_selection_functions(self):
        """Test selection API functions"""
        peak_list = new_peak_list(2, np.array([512, 512]))
        add_peak_peak_list(peak_list)
        
        is_selected_peak_list(peak_list, True)
        self.assertTrue(peak_list.peaks[0].get_is_selected())
        
        unselect_selected_peak_list(peak_list)
        self.assertFalse(peak_list.peaks[0].get_is_selected())
    
    def test_color_symbol_functions(self):
        """Test color and symbol API functions"""
        peak_list = new_peak_list(2, np.array([512, 512]))
        
        color = np.array([1.0, 0.5, 0.0])
        set_color_peak_list(peak_list, color)
        np.testing.assert_array_equal(peak_list.color, color)
        
        result = set_symbol_peak_list(peak_list, 5)
        self.assertTrue(result)
        self.assertEqual(peak_list.symbol, 5)
    
    def test_search_functions(self):
        """Test search API functions"""
        peak_list = new_peak_list(2, np.array([512, 512]))
        peak = add_peak_peak_list(peak_list)
        peak.set_position(np.array([100.0, 100.0]))
        
        first = np.array([50.0, 50.0])
        last = np.array([150.0, 150.0])
        
        npeaks, indices = search_region_peak_list(peak_list, first, last)
        self.assertEqual(npeaks, 1)
        
        index, d2 = search_nearest_peak_list(
            peak_list, 0, 1, 1.0, 1.0, first, last
        )
        self.assertEqual(index, 0)
    
    def test_max_functions(self):
        """Test determine max API functions"""
        peak_list = new_peak_list(2, np.array([512, 512]))
        peak = add_peak_peak_list(peak_list)
        peak.set_intensity(100.0)
        peak.set_volume(200.0)
        
        intensity_max, volume_max = determine_peak_list_max(peak_list)
        self.assertEqual(intensity_max, 100.0)
        self.assertEqual(volume_max, 200.0)
        
        scale = determine_peak_scale(peak, intensity_max, volume_max)
        self.assertGreater(scale, 0.0)


class TestMockBlockFile(unittest.TestCase):
    """Test mock block file functionality"""
    
    def test_create_mock_block_file(self):
        """Test creating mock block file"""
        mock = MockBlockFile(2, np.array([100, 100]))
        
        self.assertEqual(mock.ndim, 2)
        np.testing.assert_array_equal(mock.points, [100, 100])
        self.assertEqual(mock.data.shape, (100, 100))
    
    def test_mock_get_point(self):
        """Test getting point from mock"""
        data = np.arange(100).reshape(10, 10).astype(float)
        mock = MockBlockFile(2, np.array([10, 10]), data=data)
        
        point = np.array([5, 3])
        value = mock.get_point(point)
        
        self.assertEqual(value, 53.0)
    
    def test_mock_linewidth(self):
        """Test mock linewidth calculation"""
        mock = MockBlockFile(2, np.array([100, 100]))
        
        linewidth = mock.linewidth(True, 10.0, np.array([50, 50]), 0)
        
        self.assertEqual(linewidth, 3.0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPeakListBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestPeakListColor))
    suite.addTests(loader.loadTestsFromTestCase(TestPeakListSymbol))
    suite.addTests(loader.loadTestsFromTestCase(TestPeakListAddRemove))
    suite.addTests(loader.loadTestsFromTestCase(TestPeakListSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchRegion))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchNearest))
    suite.addTests(loader.loadTestsFromTestCase(TestDetermineMax))
    suite.addTests(loader.loadTestsFromTestCase(TestPeakScale))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagonalExclusion))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestCAPICompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestMockBlockFile))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
