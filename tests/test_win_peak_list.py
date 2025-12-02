"""
Tests for win_peak_list module.

Tests window peak list rendering.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add ccpnmr2.4 directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from ccpnmr.analysis.python_impl.win_peak_list import (
    WinPeakList, draw_win_peak_list,
    new_win_peak_list, delete_win_peak_list,
    is_symbol_drawn_win_peak_list, is_text_drawn_win_peak_list,
    is_text_pointer_drawn_win_peak_list,
    DRAW_UNIFORM_METHOD, DRAW_GLOBAL_METHOD, DRAW_PEAKLIST_METHOD,
    DRAW_LINE_WIDTH_METHOD, NDRAW_METHODS, NCOLORS,
    _is_peak_drawn, _invert_color, _depth_cue_peak
)


# Mock classes for testing
class MockPeak:
    """Mock peak for testing."""
    def __init__(self, ndim, position, intensity=1.0):
        self.ndim = ndim
        self.position = np.array(position)
        self.intensity = intensity
        self.isSelected = False
        self.line_width = np.ones(ndim)
        self.text = f"Peak {position[0]:.1f}"
        self.num_aliasing = np.zeros(ndim, dtype=int)
        
    def draw(self, xdim, ydim, first, last, xpix, ypix, xsc, ysc,
             symbol, is_symbol_drawn, is_text_drawn, is_text_pointer_drawn,
             has_value_axis, tile, drawing_funcs, data):
        """Mock draw method."""
        pass


class MockPeakList:
    """Mock peak list for testing."""
    def __init__(self, ndim, peaks=None):
        self.ndim = ndim
        self.peaks = peaks or []
        self.color = np.array([1.0, 0.0, 0.0])  # Red
        self.symbol = 0
        self.npoints = np.array([100] * ndim)
        
    def determine_max(self):
        """Mock max determination."""
        return 1.0, 1.0
        
    def determine_peak_scale(self, peak, intensity_max, volume_max):
        """Mock scale determination."""
        return 1.0


class DrawingRecorder:
    """Records drawing operations."""
    def __init__(self):
        self.colors = []
        
    def set_draw_color(self, data, color):
        """Record color setting."""
        self.colors.append(np.array(color))
        
    def get_funcs(self):
        """Get function dict."""
        return {'set_draw_color': self.set_draw_color}


class TestConstants:
    """Test constants."""
    
    def test_draw_method_constants(self):
        """Test drawing method constants."""
        assert DRAW_UNIFORM_METHOD == 0
        assert DRAW_GLOBAL_METHOD == 1
        assert DRAW_PEAKLIST_METHOD == 2
        assert DRAW_LINE_WIDTH_METHOD == 3
        assert NDRAW_METHODS == 4
        
    def test_color_constant(self):
        """Test color component constant."""
        assert NCOLORS == 3


class TestWinPeakListCreation:
    """Test WinPeakList creation."""
    
    def test_create_basic(self):
        """Test basic creation."""
        peak_list = MockPeakList(2)
        win_peak_list = WinPeakList(peak_list)
        
        assert win_peak_list.peak_list is peak_list
        assert win_peak_list.hasValueAxis == False
        assert win_peak_list.isSymbolDrawn == True
        assert win_peak_list.isTextDrawn == True
        assert win_peak_list.isTextPointerDrawn == True
        
    def test_create_with_value_axis(self):
        """Test creation with value axis."""
        peak_list = MockPeakList(1)
        win_peak_list = WinPeakList(peak_list, hasValueAxis=True)
        
        assert win_peak_list.hasValueAxis == True
        
    def test_set_symbol_drawn(self):
        """Test setting symbol drawn flag."""
        peak_list = MockPeakList(2)
        win_peak_list = WinPeakList(peak_list)
        
        win_peak_list.set_symbol_drawn(False)
        assert win_peak_list.isSymbolDrawn == False
        
        win_peak_list.set_symbol_drawn(True)
        assert win_peak_list.isSymbolDrawn == True
        
    def test_set_text_drawn(self):
        """Test setting text drawn flag."""
        peak_list = MockPeakList(2)
        win_peak_list = WinPeakList(peak_list)
        
        win_peak_list.set_text_drawn(False)
        assert win_peak_list.isTextDrawn == False
        
    def test_set_text_pointer_drawn(self):
        """Test setting text pointer drawn flag."""
        peak_list = MockPeakList(2)
        win_peak_list = WinPeakList(peak_list)
        
        win_peak_list.set_text_pointer_drawn(False)
        assert win_peak_list.isTextPointerDrawn == False


class TestIsPeakDrawn:
    """Test peak visibility checking."""
    
    def test_peak_in_region(self):
        """Test peak within region."""
        peak = MockPeak(2, [5.0, 10.0])
        first = np.array([0.0, 0.0])
        last = np.array([10.0, 20.0])
        
        assert _is_peak_drawn(2, peak, first, last) == True
        
    def test_peak_outside_region_x(self):
        """Test peak outside in x dimension."""
        peak = MockPeak(2, [15.0, 10.0])
        first = np.array([0.0, 0.0])
        last = np.array([10.0, 20.0])
        
        assert _is_peak_drawn(2, peak, first, last) == False
        
    def test_peak_outside_region_y(self):
        """Test peak outside in y dimension."""
        peak = MockPeak(2, [5.0, 25.0])
        first = np.array([0.0, 0.0])
        last = np.array([10.0, 20.0])
        
        assert _is_peak_drawn(2, peak, first, last) == False
        
    def test_peak_at_boundary(self):
        """Test peak at region boundary."""
        peak = MockPeak(2, [11.0, 10.0])  # Position 11 becomes 10 (0-based)
        first = np.array([0.0, 0.0])
        last = np.array([10.0, 20.0])
        
        # At last boundary (0-based pos 10 == last), should not be drawn
        assert _is_peak_drawn(2, peak, first, last) == False
        
    def test_peak_no_position(self):
        """Test peak without position."""
        peak = MockPeak(2, [5.0, 10.0])
        peak.position = None
        first = np.array([0.0, 0.0])
        last = np.array([10.0, 20.0])
        
        assert _is_peak_drawn(2, peak, first, last) == False
        
    def test_3d_peak(self):
        """Test 3D peak visibility."""
        peak = MockPeak(3, [5.0, 10.0, 15.0])
        first = np.array([0.0, 0.0, 10.0])
        last = np.array([10.0, 20.0, 20.0])
        
        assert _is_peak_drawn(3, peak, first, last) == True


class TestInvertColor:
    """Test color inversion."""
    
    def test_invert_black(self):
        """Test inverting black gives white."""
        color = np.array([0.0, 0.0, 0.0])
        inverted = _invert_color(color)
        np.testing.assert_array_almost_equal(inverted, [1.0, 1.0, 1.0])
        
    def test_invert_white(self):
        """Test inverting white gives black."""
        color = np.array([1.0, 1.0, 1.0])
        inverted = _invert_color(color)
        np.testing.assert_array_almost_equal(inverted, [0.0, 0.0, 0.0])
        
    def test_invert_red(self):
        """Test inverting red gives cyan."""
        color = np.array([1.0, 0.0, 0.0])
        inverted = _invert_color(color)
        np.testing.assert_array_almost_equal(inverted, [0.0, 1.0, 1.0])
        
    def test_invert_gray(self):
        """Test inverting gray."""
        color = np.array([0.5, 0.5, 0.5])
        inverted = _invert_color(color)
        np.testing.assert_array_almost_equal(inverted, [0.5, 0.5, 0.5])


class TestDepthCueing:
    """Test depth cueing."""
    
    def test_depth_cue_center(self):
        """Test peak at center has no depth cueing."""
        peak = MockPeak(3, [50.0, 50.0, 50.0])
        recorder = DrawingRecorder()
        
        npoints = np.array([100, 100, 100])
        center = np.array([50.0, 50.0, 50.0])
        thickness = np.array([10.0, 10.0, 10.0])
        tile = np.array([0, 0, 0])
        fg_color = np.array([1.0, 0.0, 0.0])
        bg_color = np.array([1.0, 1.0, 1.0])
        
        _depth_cue_peak(peak, 0, 1, npoints, center, thickness, tile,
                       fg_color, bg_color, recorder.get_funcs(), None)
        
        # Should be mostly foreground color
        assert len(recorder.colors) == 1
        # Center should be close to fg_color
        assert recorder.colors[0][0] > 0.9  # Red channel
        
    def test_depth_cue_edge(self):
        """Test peak at edge gets depth cueing."""
        peak = MockPeak(3, [50.0, 50.0, 60.0])  # 10 away from center
        recorder = DrawingRecorder()
        
        npoints = np.array([100, 100, 100])
        center = np.array([50.0, 50.0, 50.0])
        thickness = np.array([10.0, 10.0, 10.0])
        tile = np.array([0, 0, 0])
        fg_color = np.array([1.0, 0.0, 0.0])
        bg_color = np.array([1.0, 1.0, 1.0])
        
        _depth_cue_peak(peak, 0, 1, npoints, center, thickness, tile,
                       fg_color, bg_color, recorder.get_funcs(), None)
        
        # Should blend toward background
        assert len(recorder.colors) == 1
        # Should have some white blended in
        assert recorder.colors[0][1] > 0.0  # Green channel should increase
        
    def test_depth_cue_no_thickness(self):
        """Test depth cue with zero thickness (pseudo-3D)."""
        peak = MockPeak(3, [50.0, 50.0, 60.0])
        recorder = DrawingRecorder()
        
        npoints = np.array([100, 100, 100])
        center = np.array([50.0, 50.0, 50.0])
        thickness = np.array([10.0, 10.0, 0.0])  # No depth in Z
        tile = np.array([0, 0, 0])
        fg_color = np.array([1.0, 0.0, 0.0])
        bg_color = np.array([1.0, 1.0, 1.0])
        
        _depth_cue_peak(peak, 0, 1, npoints, center, thickness, tile,
                       fg_color, bg_color, recorder.get_funcs(), None)
        
        # Should be foreground (no depth cueing in Z)
        assert len(recorder.colors) == 1


class TestDrawWinPeakList:
    """Test main drawing function."""
    
    def test_draw_empty_list(self):
        """Test drawing empty peak list."""
        peak_list = MockPeakList(2, [])
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_UNIFORM_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True
        
    def test_draw_single_peak(self):
        """Test drawing single peak."""
        peak = MockPeak(2, [5.0, 5.0])
        peak_list = MockPeakList(2, [peak])
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_UNIFORM_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True
        assert len(recorder.colors) >= 1  # Initial + per-peak
        
    def test_draw_multiple_peaks(self):
        """Test drawing multiple peaks."""
        peaks = [
            MockPeak(2, [3.0, 3.0]),
            MockPeak(2, [5.0, 5.0]),
            MockPeak(2, [7.0, 7.0])
        ]
        peak_list = MockPeakList(2, peaks)
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_UNIFORM_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True
        
    def test_draw_with_symbols_disabled(self):
        """Test drawing with symbols disabled."""
        peak = MockPeak(2, [5.0, 5.0])
        peak_list = MockPeakList(2, [peak])
        win_peak_list = WinPeakList(peak_list)
        win_peak_list.set_symbol_drawn(False)
        win_peak_list.set_text_drawn(False)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_UNIFORM_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        # Should return early
        assert result == True
        
    def test_draw_outside_region(self):
        """Test peaks outside region are skipped."""
        peaks = [
            MockPeak(2, [15.0, 15.0]),  # Outside
            MockPeak(2, [5.0, 5.0])     # Inside
        ]
        peak_list = MockPeakList(2, peaks)
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_UNIFORM_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True


class TestCAPIFunctions:
    """Test C API compatibility functions."""
    
    def test_new_win_peak_list(self):
        """Test new_win_peak_list function."""
        peak_list = MockPeakList(2)
        win_peak_list = new_win_peak_list(peak_list)
        
        assert isinstance(win_peak_list, WinPeakList)
        assert win_peak_list.peak_list is peak_list
        
    def test_new_win_peak_list_with_value_axis(self):
        """Test new_win_peak_list with value axis."""
        peak_list = MockPeakList(1)
        win_peak_list = new_win_peak_list(peak_list, hasValueAxis=True)
        
        assert win_peak_list.hasValueAxis == True
        
    def test_delete_win_peak_list(self):
        """Test delete_win_peak_list function."""
        peak_list = MockPeakList(2)
        win_peak_list = new_win_peak_list(peak_list)
        delete_win_peak_list(win_peak_list)  # Should not error
        
    def test_is_symbol_drawn_capi(self):
        """Test is_symbol_drawn_win_peak_list function."""
        peak_list = MockPeakList(2)
        win_peak_list = new_win_peak_list(peak_list)
        
        is_symbol_drawn_win_peak_list(win_peak_list, False)
        assert win_peak_list.isSymbolDrawn == False
        
    def test_is_text_drawn_capi(self):
        """Test is_text_drawn_win_peak_list function."""
        peak_list = MockPeakList(2)
        win_peak_list = new_win_peak_list(peak_list)
        
        is_text_drawn_win_peak_list(win_peak_list, False)
        assert win_peak_list.isTextDrawn == False
        
    def test_is_text_pointer_drawn_capi(self):
        """Test is_text_pointer_drawn_win_peak_list function."""
        peak_list = MockPeakList(2)
        win_peak_list = new_win_peak_list(peak_list)
        
        is_text_pointer_drawn_win_peak_list(win_peak_list, False)
        assert win_peak_list.isTextPointerDrawn == False


class TestDrawingMethods:
    """Test different drawing methods."""
    
    def test_uniform_method(self):
        """Test uniform drawing method."""
        peak = MockPeak(2, [5.0, 5.0])
        peak_list = MockPeakList(2, [peak])
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_UNIFORM_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True
        
    def test_peaklist_method(self):
        """Test peak list method."""
        peak = MockPeak(2, [5.0, 5.0])
        peak_list = MockPeakList(2, [peak])
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_PEAKLIST_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True
        
    def test_linewidth_method(self):
        """Test line width method."""
        peak = MockPeak(2, [5.0, 5.0])
        peak.line_width = np.array([2.0, 3.0])
        peak_list = MockPeakList(2, [peak])
        win_peak_list = WinPeakList(peak_list)
        recorder = DrawingRecorder()
        
        result = draw_win_peak_list(
            win_peak_list, 0, 1, 1.0, 1.0, 1.0, 1.0,
            np.array([0.0, 0.0]), np.array([10.0, 10.0]),
            DRAW_LINE_WIDTH_METHOD, 1.0, 1.0,
            np.array([1.0, 1.0, 1.0]),
            np.array([5.0, 5.0]), np.array([10.0, 10.0]), np.array([0, 0]),
            recorder.get_funcs(), None
        )
        
        assert result == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
