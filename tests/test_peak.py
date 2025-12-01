"""
Unit tests for peak module.

These tests are implementation-agnostic - they work with both
the C extension and pure Python implementations.
"""

import unittest
import sys
import os

# Add repo root to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

# Import through the wrapper
import importlib.util
wrapper_path = os.path.join(repo_root, 'ccpnmr2.4', 'c', 'ccpnmr', 'analysis', 'py_peak.py')
spec = importlib.util.spec_from_file_location('py_peak', wrapper_path)
if spec and spec.loader:
    py_peak = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(py_peak)
else:
    raise ImportError(f"Could not load py_peak from {wrapper_path}")


class TestPeakBasics(unittest.TestCase):
    """Test basic peak operations."""
    
    def test_peak_creation_1d(self):
        """Test creating a 1D peak."""
        peak = py_peak.new_peak(1)
        self.assertIsNotNone(peak)
        self.assertEqual(peak.ndim, 1)
        self.assertEqual(len(peak.position), 1)
        self.assertEqual(peak.position[0], 0.0)
    
    def test_peak_creation_2d(self):
        """Test creating a 2D peak."""
        peak = py_peak.new_peak(2)
        self.assertIsNotNone(peak)
        self.assertEqual(peak.ndim, 2)
        self.assertEqual(len(peak.position), 2)
    
    def test_peak_creation_3d(self):
        """Test creating a 3D peak."""
        peak = py_peak.new_peak(3)
        self.assertIsNotNone(peak)
        self.assertEqual(peak.ndim, 3)
        self.assertEqual(len(peak.position), 3)
    
    def test_initial_values(self):
        """Test peak initial values."""
        peak = py_peak.new_peak(2)
        self.assertEqual(peak.text, "")
        self.assertFalse(peak.isSelected)
        self.assertEqual(peak.intensity, 0.0)
        self.assertEqual(peak.volume, 0.0)
        self.assertEqual(peak.num_aliasing, [0, 0])
        self.assertEqual(peak.line_width, [0.0, 0.0])
    
    def test_delete_peak(self):
        """Test peak deletion (no-op in Python)."""
        peak = py_peak.new_peak(2)
        py_peak.delete_peak(peak)
        # No assertion - just verify it doesn't crash


class TestPeakSelection(unittest.TestCase):
    """Test peak selection state."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(2)
    
    def test_initial_not_selected(self):
        """Test peak starts unselected."""
        self.assertFalse(py_peak.get_is_selected_peak(self.peak))
    
    def test_set_selected(self):
        """Test setting peak as selected."""
        py_peak.set_is_selected_peak(self.peak, True)
        self.assertTrue(py_peak.get_is_selected_peak(self.peak))
    
    def test_set_unselected(self):
        """Test setting peak as unselected."""
        py_peak.set_is_selected_peak(self.peak, True)
        py_peak.set_is_selected_peak(self.peak, False)
        self.assertFalse(py_peak.get_is_selected_peak(self.peak))
    
    def test_toggle_selection(self):
        """Test toggling selection state."""
        for _ in range(3):
            current = py_peak.get_is_selected_peak(self.peak)
            py_peak.set_is_selected_peak(self.peak, not current)
            self.assertEqual(py_peak.get_is_selected_peak(self.peak), not current)


class TestPeakText(unittest.TestCase):
    """Test peak text/label operations."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(2)
    
    def test_set_text(self):
        """Test setting peak text."""
        result = py_peak.set_text_peak(self.peak, "Peak1", None)
        self.assertTrue(result)
        self.assertEqual(self.peak.text, "Peak1")
    
    def test_set_empty_text(self):
        """Test setting empty text."""
        py_peak.set_text_peak(self.peak, "", None)
        self.assertEqual(self.peak.text, "")
    
    def test_change_text(self):
        """Test changing peak text."""
        py_peak.set_text_peak(self.peak, "First", None)
        py_peak.set_text_peak(self.peak, "Second", None)
        self.assertEqual(self.peak.text, "Second")
    
    def test_unicode_text(self):
        """Test setting unicode text."""
        py_peak.set_text_peak(self.peak, "Peak α", None)
        self.assertEqual(self.peak.text, "Peak α")


class TestPeakPosition(unittest.TestCase):
    """Test peak position operations."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(3)
    
    def test_set_position(self):
        """Test setting peak position."""
        position = [10.5, 20.3, 30.1]
        py_peak.set_position_peak(self.peak, position)
        self.assertEqual(self.peak.position, position)
    
    def test_position_is_copied(self):
        """Test that position is copied, not referenced."""
        position = [10.0, 20.0, 30.0]
        py_peak.set_position_peak(self.peak, position)
        position[0] = 999.0  # Modify original
        self.assertEqual(self.peak.position[0], 10.0)  # Peak should be unchanged
    
    def test_change_position(self):
        """Test changing position multiple times."""
        py_peak.set_position_peak(self.peak, [1.0, 2.0, 3.0])
        py_peak.set_position_peak(self.peak, [4.0, 5.0, 6.0])
        self.assertEqual(self.peak.position, [4.0, 5.0, 6.0])


class TestPeakAliasing(unittest.TestCase):
    """Test peak aliasing operations."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(2)
    
    def test_set_num_aliasing(self):
        """Test setting aliasing numbers."""
        aliasing = [1, -2]
        py_peak.set_num_aliasing_peak(self.peak, aliasing)
        self.assertEqual(self.peak.num_aliasing, aliasing)
    
    def test_zero_aliasing(self):
        """Test zero aliasing (default)."""
        self.assertEqual(self.peak.num_aliasing, [0, 0])
    
    def test_aliasing_is_copied(self):
        """Test that aliasing is copied."""
        aliasing = [3, 4]
        py_peak.set_num_aliasing_peak(self.peak, aliasing)
        aliasing[0] = 999
        self.assertEqual(self.peak.num_aliasing[0], 3)


class TestPeakIntensityVolume(unittest.TestCase):
    """Test peak intensity and volume operations."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(2)
    
    def test_set_intensity(self):
        """Test setting peak intensity."""
        py_peak.set_intensity_peak(self.peak, 1234.5)
        self.assertEqual(self.peak.intensity, 1234.5)
    
    def test_set_volume(self):
        """Test setting peak volume."""
        py_peak.set_volume_peak(self.peak, 5678.9)
        self.assertEqual(self.peak.volume, 5678.9)
    
    def test_negative_intensity(self):
        """Test negative intensity (valid for some peaks)."""
        py_peak.set_intensity_peak(self.peak, -100.0)
        self.assertEqual(self.peak.intensity, -100.0)
    
    def test_zero_values(self):
        """Test zero intensity and volume."""
        py_peak.set_intensity_peak(self.peak, 0.0)
        py_peak.set_volume_peak(self.peak, 0.0)
        self.assertEqual(self.peak.intensity, 0.0)
        self.assertEqual(self.peak.volume, 0.0)


class TestPeakLineWidth(unittest.TestCase):
    """Test peak line width operations."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(3)
    
    def test_set_line_width(self):
        """Test setting line width for each dimension."""
        py_peak.set_line_width_peak(self.peak, 0, 2.5)
        py_peak.set_line_width_peak(self.peak, 1, 3.0)
        py_peak.set_line_width_peak(self.peak, 2, 1.8)
        
        self.assertEqual(self.peak.line_width[0], 2.5)
        self.assertEqual(self.peak.line_width[1], 3.0)
        self.assertEqual(self.peak.line_width[2], 1.8)
    
    def test_initial_line_width_zero(self):
        """Test initial line widths are zero."""
        self.assertEqual(self.peak.line_width, [0.0, 0.0, 0.0])
    
    def test_change_line_width(self):
        """Test changing line width."""
        py_peak.set_line_width_peak(self.peak, 0, 5.0)
        py_peak.set_line_width_peak(self.peak, 0, 10.0)
        self.assertEqual(self.peak.line_width[0], 10.0)


class TestPeakTextOffset(unittest.TestCase):
    """Test peak text offset operations."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(2)
    
    def test_set_text_offset(self):
        """Test setting text offset."""
        py_peak.set_text_offset_peak(self.peak, 0, 5.0)
        self.assertEqual(self.peak.text_offset[0], 5.0)
    
    def test_set_value_offset(self):
        """Test setting value offset (dim=-1)."""
        py_peak.set_text_offset_peak(self.peak, -1, 10.0)
        self.assertEqual(self.peak.value_offset, 10.0)
    
    def test_reset_text_offset(self):
        """Test resetting text offset to default."""
        py_peak.set_text_offset_peak(self.peak, 0, 5.0)
        py_peak.reset_text_offset_peak(self.peak, 0)
        self.assertEqual(self.peak.text_offset[0], py_peak.DEFAULT_TEXT_OFFSET)
    
    def test_reset_value_offset(self):
        """Test resetting value offset."""
        py_peak.set_text_offset_peak(self.peak, -1, 10.0)
        py_peak.reset_text_offset_peak(self.peak, -1)
        self.assertEqual(self.peak.value_offset, py_peak.DEFAULT_TEXT_OFFSET)


class TestPeakRegion(unittest.TestCase):
    """Test peak region checking."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(2)
        py_peak.set_position_peak(self.peak, [50.0, 100.0])
    
    def test_peak_in_region(self):
        """Test peak is detected when in region."""
        first = [40.0, 90.0]
        last = [60.0, 110.0]
        npoints = [100, 200]
        
        result = py_peak.is_in_region_peak(self.peak, first, last, npoints)
        self.assertTrue(result)
    
    def test_peak_outside_region(self):
        """Test peak is not detected when outside region."""
        first = [10.0, 20.0]
        last = [30.0, 40.0]
        npoints = [100, 200]
        
        result = py_peak.is_in_region_peak(self.peak, first, last, npoints)
        self.assertFalse(result)
    
    def test_peak_on_boundary(self):
        """Test peak exactly on region boundary."""
        first = [50.0, 100.0]
        last = [60.0, 110.0]
        npoints = [100, 200]
        
        result = py_peak.is_in_region_peak(self.peak, first, last, npoints)
        self.assertTrue(result)
    
    def test_peak_with_aliasing(self):
        """Test peak detection with aliasing."""
        py_peak.set_num_aliasing_peak(self.peak, [1, 0])
        first = [140.0, 90.0]
        last = [160.0, 110.0]
        npoints = [100, 200]
        allow_aliasing = [True, False]
        
        # With aliasing: position 50 + 1*100 = 150 (in range 140-160)
        result = py_peak.is_in_region_peak(self.peak, first, last, npoints, 
                                          allow_aliasing)
        self.assertTrue(result)


class TestPeakScaledRegion(unittest.TestCase):
    """Test peak scaled region calculation."""
    
    def setUp(self):
        """Create a peak for testing."""
        self.peak = py_peak.new_peak(3)
        py_peak.set_position_peak(self.peak, [10.0, 20.0, 30.0])
    
    def test_find_scaled_region(self):
        """Test finding scaled region around peak."""
        xdim = 0
        ydim = 1
        scale = 5.0
        yscale = 3.0
        
        first, last = py_peak.find_scaled_region_peak(self.peak, xdim, ydim, 
                                                     scale, yscale)
        
        # X dimension should be position ± scale
        self.assertEqual(first[xdim], 5.0)
        self.assertEqual(last[xdim], 15.0)
        
        # Y dimension should be position ± yscale
        self.assertEqual(first[ydim], 17.0)
        self.assertEqual(last[ydim], 23.0)
        
        # Other dimensions should be unchanged
        self.assertEqual(first[2], 30.0)
        self.assertEqual(last[2], 30.0)


class TestPeakConstants(unittest.TestCase):
    """Test module constants."""
    
    def test_method_constants(self):
        """Test fitting method constants are defined."""
        self.assertEqual(py_peak.GAUSSIAN_METHOD, 0)
        self.assertEqual(py_peak.LORENTZIAN_METHOD, 1)
        self.assertEqual(py_peak.NMETHODS, 2)
    
    def test_default_text_offset(self):
        """Test default text offset constant."""
        self.assertAlmostEqual(py_peak.DEFAULT_TEXT_OFFSET, -999.9, places=1)


class TestPeakAPICompatibility(unittest.TestCase):
    """Test API matches C implementation."""
    
    def test_c_style_api_functions_exist(self):
        """Verify all C-style API functions are available."""
        functions = [
            'new_peak',
            'delete_peak',
            'get_is_selected_peak',
            'set_is_selected_peak',
            'set_text_peak',
            'set_position_peak',
            'set_text_offset_peak',
            'reset_text_offset_peak',
            'set_num_aliasing_peak',
            'set_intensity_peak',
            'set_volume_peak',
            'set_line_width_peak',
            'is_in_region_peak',
            'find_scaled_region_peak',
        ]
        
        for func_name in functions:
            self.assertTrue(hasattr(py_peak, func_name),
                           f"Missing function: {func_name}")
            self.assertTrue(callable(getattr(py_peak, func_name)),
                           f"Not callable: {func_name}")
    
    def test_peak_class_exists(self):
        """Verify Peak class is available."""
        self.assertTrue(hasattr(py_peak, 'Peak'))
        peak = py_peak.Peak(2)
        self.assertIsNotNone(peak)


def run_tests(verbosity=2):
    """Run all tests with specified verbosity."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
