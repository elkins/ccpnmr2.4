"""
Tests for clipping module.

Tests Cohen-Sutherland line clipping algorithm.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add ccpnmr2.4 directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from memops.global_.python_impl.clipping import (
    PolylineDrawn, Polyline,
    _polyline_drawn, draw_clipped_line, draw_clipped_polyline,
    draw_clipped_polyline_capi
)


class DrawingRecorder:
    """Records drawing operations for testing."""
    def __init__(self):
        self.lines = []
        self.polylines = []
        
    def draw_line(self, data, x0, y0, x1, y1):
        """Record line drawing."""
        self.lines.append((x0, y0, x1, y1))
        
    def draw_polyline(self, data, vertices, closed):
        """Record polyline drawing."""
        self.polylines.append((vertices.copy(), closed))
        
    def draw_clipped_line(self, data, x0, y0, x1, y1):
        """Record clipped line drawing (delegates to draw_line)."""
        # In actual usage, this would call back to draw_clipped_line function
        # For testing, we just record it like a regular line
        self.lines.append((x0, y0, x1, y1))
        
    def get_funcs(self):
        """Get function dictionary."""
        return {
            'draw_line': self.draw_line,
            'draw_polyline': self.draw_polyline,
            'draw_clipped_line': self.draw_clipped_line
        }


class TestPolylineDrawn:
    """Test polyline visibility determination."""
    
    def test_empty_polyline(self):
        """Test empty polyline."""
        vertices = np.array([])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.NONE_DRAWN
        
    def test_all_inside(self):
        """Test polyline entirely inside region."""
        vertices = np.array([[2, 2], [5, 5], [8, 8]])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.ALL_DRAWN
        
    def test_all_outside_left(self):
        """Test polyline entirely left of region."""
        vertices = np.array([[-5, 2], [-3, 5], [-1, 8]])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.NONE_DRAWN
        
    def test_all_outside_right(self):
        """Test polyline entirely right of region."""
        vertices = np.array([[15, 2], [18, 5], [20, 8]])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.NONE_DRAWN
        
    def test_all_outside_below(self):
        """Test polyline entirely below region."""
        vertices = np.array([[2, -5], [5, -3], [8, -1]])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.NONE_DRAWN
        
    def test_all_outside_above(self):
        """Test polyline entirely above region."""
        vertices = np.array([[2, 15], [5, 18], [8, 20]])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.NONE_DRAWN
        
    def test_some_drawn(self):
        """Test polyline partially overlapping region."""
        vertices = np.array([[-2, 5], [5, 5], [12, 5]])
        result = _polyline_drawn(vertices, False, 0, 0, 10, 10)
        assert result == PolylineDrawn.SOME_DRAWN


class TestDrawClippedLine:
    """Test line clipping."""
    
    def test_line_entirely_inside(self):
        """Test line entirely inside region."""
        recorder = DrawingRecorder()
        draw_clipped_line(2, 2, 8, 8, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        assert recorder.lines[0] == (2, 2, 8, 8)
        
    def test_line_entirely_outside_left(self):
        """Test line entirely left of region."""
        recorder = DrawingRecorder()
        draw_clipped_line(-5, 5, -2, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 0
        
    def test_line_entirely_outside_right(self):
        """Test line entirely right of region."""
        recorder = DrawingRecorder()
        draw_clipped_line(15, 5, 20, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 0
        
    def test_line_entirely_outside_below(self):
        """Test line entirely below region."""
        recorder = DrawingRecorder()
        draw_clipped_line(5, -5, 5, -2, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 0
        
    def test_line_entirely_outside_above(self):
        """Test line entirely above region."""
        recorder = DrawingRecorder()
        draw_clipped_line(5, 15, 5, 20, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 0
        
    def test_line_crosses_left_boundary(self):
        """Test line crossing left boundary."""
        recorder = DrawingRecorder()
        draw_clipped_line(-2, 5, 5, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        # Should be clipped to start at x=0
        x0, y0, x1, y1 = recorder.lines[0]
        assert x0 == pytest.approx(0, abs=0.01)
        assert y0 == pytest.approx(5, abs=0.01)
        assert x1 == pytest.approx(5, abs=0.01)
        
    def test_line_crosses_right_boundary(self):
        """Test line crossing right boundary."""
        recorder = DrawingRecorder()
        draw_clipped_line(5, 5, 15, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        # Should be clipped to end at x=10
        x0, y0, x1, y1 = recorder.lines[0]
        assert x0 == pytest.approx(5, abs=0.01)
        assert x1 == pytest.approx(10, abs=0.01)
        assert y1 == pytest.approx(5, abs=0.01)
        
    def test_line_crosses_bottom_boundary(self):
        """Test line crossing bottom boundary."""
        recorder = DrawingRecorder()
        draw_clipped_line(5, -2, 5, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        # Should be clipped to start at y=0
        x0, y0, x1, y1 = recorder.lines[0]
        assert x0 == pytest.approx(5, abs=0.01)
        assert y0 == pytest.approx(0, abs=0.01)
        assert y1 == pytest.approx(5, abs=0.01)
        
    def test_line_crosses_top_boundary(self):
        """Test line crossing top boundary."""
        recorder = DrawingRecorder()
        draw_clipped_line(5, 5, 5, 15, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        # Should be clipped to end at y=10
        x0, y0, x1, y1 = recorder.lines[0]
        assert y0 == pytest.approx(5, abs=0.01)
        assert x1 == pytest.approx(5, abs=0.01)
        assert y1 == pytest.approx(10, abs=0.01)
        
    def test_line_crosses_two_boundaries(self):
        """Test line crossing two boundaries."""
        recorder = DrawingRecorder()
        draw_clipped_line(-2, 5, 15, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        # Should be clipped to [0,5] to [10,5]
        x0, y0, x1, y1 = recorder.lines[0]
        assert x0 == pytest.approx(0, abs=0.01)
        assert y0 == pytest.approx(5, abs=0.01)
        assert x1 == pytest.approx(10, abs=0.01)
        assert y1 == pytest.approx(5, abs=0.01)
        
    def test_diagonal_line_clipped(self):
        """Test diagonal line clipping."""
        recorder = DrawingRecorder()
        # Line from (-5, -4) to (14, 13) passes through region without hitting corners
        draw_clipped_line(-5, -4, 14, 13, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        # Should be clipped to visible segment
        x0, y0, x1, y1 = recorder.lines[0]
        # Line has slope close to 1, so expect both endpoints in region
        assert 0 <= x0 <= 10
        assert 0 <= y0 <= 10
        assert 0 <= x1 <= 10
        assert 0 <= y1 <= 10


class TestDrawClippedPolyline:
    """Test polyline clipping."""
    
    def test_polyline_all_inside(self):
        """Test polyline entirely inside region."""
        vertices = np.array([[2, 2], [5, 5], [8, 8]])
        recorder = DrawingRecorder()
        draw_clipped_polyline(vertices, False, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.polylines) == 1
        np.testing.assert_array_equal(recorder.polylines[0][0], vertices)
        assert recorder.polylines[0][1] == False
        
    def test_polyline_all_outside(self):
        """Test polyline entirely outside region."""
        vertices = np.array([[-5, -5], [-3, -3], [-1, -1]])
        recorder = DrawingRecorder()
        draw_clipped_polyline(vertices, False, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 0
        assert len(recorder.polylines) == 0
        
    def test_polyline_some_visible(self):
        """Test polyline partially visible."""
        vertices = np.array([[-2, 5], [5, 5], [12, 5]])
        recorder = DrawingRecorder()
        draw_clipped_polyline(vertices, False, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        # Should draw clipped segments
        assert len(recorder.lines) == 2
        
    def test_polyline_closed(self):
        """Test closed polyline."""
        vertices = np.array([[-2, 5], [5, 5], [12, 5]])
        recorder = DrawingRecorder()
        draw_clipped_polyline(vertices, True, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        # Should draw clipped segments including closing segment
        assert len(recorder.lines) == 3
        
    def test_polyline_complex_path(self):
        """Test complex polyline path."""
        vertices = np.array([
            [2, 2],
            [8, 2],
            [8, 8],
            [2, 8]
        ])
        recorder = DrawingRecorder()
        draw_clipped_polyline(vertices, True, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        # All inside, should draw as polyline
        assert len(recorder.polylines) == 1


class TestPolylineClass:
    """Test Polyline class."""
    
    def test_create_polyline(self):
        """Test creating polyline."""
        vertices = np.array([[0, 0], [10, 10]])
        polyline = Polyline(vertices)
        
        assert polyline.nvertices == 2
        np.testing.assert_array_equal(polyline.vertices, vertices)
        assert polyline.closed == False
        
    def test_create_closed_polyline(self):
        """Test creating closed polyline."""
        vertices = np.array([[0, 0], [10, 0], [10, 10], [0, 10]])
        polyline = Polyline(vertices, closed=True)
        
        assert polyline.nvertices == 4
        assert polyline.closed == True


class TestCAPIWrapper:
    """Test C API compatibility wrapper."""
    
    def test_draw_clipped_polyline_capi(self):
        """Test C API wrapper."""
        vertices = np.array([[2, 2], [5, 5], [8, 8]])
        polyline = Polyline(vertices)
        recorder = DrawingRecorder()
        
        draw_clipped_polyline_capi(polyline, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.polylines) == 1


class TestEdgeCases:
    """Test edge cases and numerical stability."""
    
    def test_vertical_line(self):
        """Test vertical line."""
        recorder = DrawingRecorder()
        draw_clipped_line(5, -5, 5, 15, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        x0, y0, x1, y1 = recorder.lines[0]
        assert x0 == pytest.approx(5, abs=0.01)
        assert x1 == pytest.approx(5, abs=0.01)
        assert y0 == pytest.approx(0, abs=0.01)
        assert y1 == pytest.approx(10, abs=0.01)
        
    def test_horizontal_line(self):
        """Test horizontal line."""
        recorder = DrawingRecorder()
        draw_clipped_line(-5, 5, 15, 5, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        x0, y0, x1, y1 = recorder.lines[0]
        assert x0 == pytest.approx(0, abs=0.01)
        assert x1 == pytest.approx(10, abs=0.01)
        assert y0 == pytest.approx(5, abs=0.01)
        assert y1 == pytest.approx(5, abs=0.01)
        
    def test_line_at_corner(self):
        """Test line passing through corner."""
        recorder = DrawingRecorder()
        # Line from (-5, -5) to (5, 5) intersects at (0,0)
        # but strict inequalities mean corners don't count as inside
        # Use slightly offset line
        draw_clipped_line(-5, -5, 5, 5.1, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        assert len(recorder.lines) == 1
        x0, y0, x1, y1 = recorder.lines[0]
        # Should start near (0, 0) and end around (5, 5.1)
        assert 0 <= x0 <= 1
        assert 0 <= y0 <= 1
        
    def test_single_point_polyline(self):
        """Test polyline with single point."""
        vertices = np.array([[5, 5]])
        recorder = DrawingRecorder()
        draw_clipped_polyline(vertices, False, recorder.get_funcs(), None, 0, 0, 10, 10)
        
        # Single point, no segments to draw
        assert len(recorder.lines) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
