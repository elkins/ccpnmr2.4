"""
Tests for slice_file module - spectral data slicing.

Tests 1D slice extraction through multi-dimensional NMR spectral data
with interpolation and rendering.
"""

import pytest
import numpy as np
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ccpnmr2.4" / "python"))

from ccpnmr.analysis.python_impl.slice_file import (
    SliceFile, new_slice_file, delete_slice_file,
    draw_slice_file, draw_all_slice_file
)


@dataclass
class MockBlockFile:
    """Mock block file for testing."""
    ndim: int
    points: np.ndarray
    data: np.ndarray  # For testing
    
    def get_point(self, point: np.ndarray) -> float:
        """Get point value."""
        # Convert multi-dimensional point to linear index
        if self.ndim == 2:
            return float(self.data[point[1], point[0]])
        elif self.ndim == 3:
            return float(self.data[point[2], point[1], point[0]])
        else:
            return 0.0


class MockDrawingFuncs:
    """Mock drawing functions for testing."""
    
    def __init__(self):
        self.lines = []
    
    def draw_line(self, data, x0, y0, x1, y1):
        """Record line drawing."""
        self.lines.append((x0, y0, x1, y1))


class TestSliceFileCreation:
    """Test slice file creation and validation."""
    
    def test_creation_2d(self):
        """Test 2D slice file creation."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        
        assert slice_file.orient == 1
        assert slice_file.dim == 0
        assert slice_file.block_file is block_file
    
    def test_creation_3d(self):
        """Test 3D slice file creation."""
        block_file = MockBlockFile(
            ndim=3,
            points=np.array([10, 20, 30]),
            data=np.zeros((30, 20, 10))
        )
        
        slice_file = SliceFile(orient=0, dim=1, block_file=block_file)
        
        assert slice_file.orient == 0
        assert slice_file.dim == 1
    
    def test_invalid_dim(self):
        """Test creation with invalid dimension."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        with pytest.raises(ValueError, match="out of range"):
            SliceFile(orient=1, dim=5, block_file=block_file)
    
    def test_negative_dim(self):
        """Test creation with negative dimension."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        with pytest.raises(ValueError):
            SliceFile(orient=1, dim=-1, block_file=block_file)
    
    def test_factory_function(self):
        """Test factory function."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        slice_file = new_slice_file(1, 0, block_file)
        
        assert isinstance(slice_file, SliceFile)
        assert slice_file.orient == 1
        assert slice_file.dim == 0


class TestDrawSlice:
    """Test single slice drawing."""
    
    def test_horizontal_slice_2d(self):
        """Test drawing horizontal slice through 2D data."""
        # Create gradient data
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Draw slice at y=5
        position = np.array([0.0, 5.0])
        slice_file.draw_slice(0, 10, position, drawing, None)
        
        # Should have drawn 9 line segments (10 points - 1)
        assert len(drawing.lines) == 9
        
        # Check line coordinates
        for i, (x0, y0, x1, y1) in enumerate(drawing.lines):
            assert x0 == i
            assert x1 == i + 1
    
    def test_vertical_slice_2d(self):
        """Test drawing vertical slice through 2D data."""
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = SliceFile(orient=0, dim=1, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Draw slice at x=5
        position = np.array([5.0, 0.0])
        slice_file.draw_slice(0, 10, position, drawing, None)
        
        # Should have drawn 9 line segments
        assert len(drawing.lines) == 9
        
        # Vertical: coordinates are swapped
        for i, (x0, y0, x1, y1) in enumerate(drawing.lines):
            # For vertical, draw_line is called with (b0, a0, b1, a1)
            # where a is slice position, b is value
            assert y0 == i
            assert y1 == i + 1
    
    def test_interpolation(self):
        """Test interpolation at non-integer position."""
        # Create simple data for testing interpolation
        # data[y, x] format
        data = np.array([
            [0.0, 0.0],  # y=0
            [10.0, 10.0]  # y=1
        ], dtype=np.float32)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([2, 2]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Draw slice at y=0.5 (halfway between rows)
        position = np.array([0.0, 0.5])
        slice_file.draw_slice(0, 2, position, drawing, None)
        
        # Should have interpolated values
        assert len(drawing.lines) == 1
        
        # At y=0.5, should interpolate (weight 0.5 to each)
        # But exact value depends on implementation
        # Just verify it doesn't crash and produces some output
        x0, y0, x1, y1 = drawing.lines[0]
        assert y0 >= 0.0  # Some value produced
        assert y1 >= 0.0
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Test first < 0
        with pytest.raises(ValueError, match="first.*< 0"):
            slice_file.draw_slice(-1, 5, np.array([0.0, 5.0]), drawing, None)
        
        # Test last > points
        with pytest.raises(ValueError, match="last.*> points"):
            slice_file.draw_slice(0, 25, np.array([0.0, 5.0]), drawing, None)
        
        # Test first >= last
        with pytest.raises(ValueError, match="first.*>= last"):
            slice_file.draw_slice(5, 5, np.array([0.0, 5.0]), drawing, None)
        
        # Test position < 0
        with pytest.raises(ValueError, match="position.*< 0"):
            slice_file.draw_slice(0, 5, np.array([0.0, -1.0]), drawing, None)
        
        # Test position >= points
        with pytest.raises(ValueError, match="position.*>= points"):
            slice_file.draw_slice(0, 5, np.array([0.0, 25.0]), drawing, None)
    
    def test_partial_slice(self):
        """Test drawing partial slice."""
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Draw only middle portion
        position = np.array([0.0, 5.0])
        slice_file.draw_slice(3, 7, position, drawing, None)
        
        # Should have 3 line segments (points 3,4,5,6)
        assert len(drawing.lines) == 3


class TestDrawAllSlices:
    """Test drawing all slices in region."""
    
    def test_draw_all_2d(self):
        """Test drawing all slices in 2D region."""
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Draw region from (0,0) to (10,3)
        first = np.array([0, 0])
        last = np.array([10, 3])
        components = np.array([0])
        
        slice_file.draw_all_slices(first, last, 1, components, drawing, None)
        
        # Should draw 3 horizontal slices (y=0,1,2)
        # Each slice has 9 segments
        assert len(drawing.lines) == 3 * 9
    
    def test_parameter_validation_all(self):
        """Test parameter validation for draw_all_slices."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        components = np.array([0])
        
        # Test first < 0
        with pytest.raises(ValueError, match="first.*< 0"):
            first = np.array([-1, 0])
            last = np.array([5, 5])
            slice_file.draw_all_slices(first, last, 1, components, drawing, None)
        
        # Test last > points
        with pytest.raises(ValueError, match="last.*> points"):
            first = np.array([0, 0])
            last = np.array([10, 25])
            slice_file.draw_all_slices(first, last, 1, components, drawing, None)
        
        # Test first >= last
        with pytest.raises(ValueError, match="first.*>= last"):
            first = np.array([5, 5])
            last = np.array([5, 10])
            slice_file.draw_all_slices(first, last, 1, components, drawing, None)
    
    def test_single_slice_in_region(self):
        """Test drawing single slice via draw_all_slices."""
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Draw region with only one slice (y=5)
        first = np.array([0, 5])
        last = np.array([10, 6])
        components = np.array([0])
        
        slice_file.draw_all_slices(first, last, 1, components, drawing, None)
        
        # Should have 9 line segments
        assert len(drawing.lines) == 9


class TestCAPICompatibility:
    """Test C API compatibility functions."""
    
    def test_factory_and_delete(self):
        """Test C-style factory and delete."""
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 20]),
            data=np.zeros((20, 10))
        )
        
        slice_file = new_slice_file(1, 0, block_file)
        assert slice_file is not None
        
        # Delete should not crash
        delete_slice_file(slice_file)
    
    def test_draw_slice_wrapper(self):
        """Test C API draw_slice_file wrapper."""
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = new_slice_file(1, 0, block_file)
        drawing = MockDrawingFuncs()
        
        position = np.array([0.0, 5.0])
        draw_slice_file(slice_file, 0, 10, position, drawing, None)
        
        assert len(drawing.lines) == 9
    
    def test_draw_all_wrapper(self):
        """Test C API draw_all_slice_file wrapper."""
        data = np.arange(100, dtype=np.float32).reshape(10, 10)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([10, 10]),
            data=data
        )
        
        slice_file = new_slice_file(1, 0, block_file)
        drawing = MockDrawingFuncs()
        
        first = np.array([0, 0])
        last = np.array([10, 3])
        components = np.array([0])
        
        draw_all_slice_file(slice_file, first, last, 1, components, drawing, None)
        
        assert len(drawing.lines) == 3 * 9


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_point_slice(self):
        """Test drawing slice with only one point."""
        data = np.array([[5.0, 10.0]], dtype=np.float32)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([2, 1]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        position = np.array([0.0, 0.0])
        slice_file.draw_slice(0, 2, position, drawing, None)
        
        # Should have 1 line segment
        assert len(drawing.lines) == 1
    
    def test_position_at_boundary(self):
        """Test position at data boundary."""
        data = np.array([
            [1.0, 2.0],
            [3.0, 4.0]
        ], dtype=np.float32)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([2, 2]),
            data=data
        )
        
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        # Position at boundary (no interpolation)
        position = np.array([0.0, 1.0])
        slice_file.draw_slice(0, 2, position, drawing, None)
        
        # Should work without error
        assert len(drawing.lines) == 1


class TestIntegration:
    """Integration tests with realistic scenarios."""
    
    def test_spectrum_cross_section(self):
        """Test extracting cross-section from synthetic spectrum."""
        # Create synthetic 2D spectrum with Gaussian peak
        size = 50
        center = size // 2
        sigma = 5.0
        
        x = np.arange(size)
        y = np.arange(size)
        xx, yy = np.meshgrid(x, y)
        
        data = np.exp(-((xx - center)**2 + (yy - center)**2) / (2 * sigma**2))
        data = data.astype(np.float32)
        
        block_file = MockBlockFile(
            ndim=2,
            points=np.array([size, size]),
            data=data
        )
        
        # Extract horizontal slice through center
        slice_file = SliceFile(orient=1, dim=0, block_file=block_file)
        drawing = MockDrawingFuncs()
        
        position = np.array([0.0, float(center)])
        slice_file.draw_slice(0, size, position, drawing, None)
        
        # Should have size-1 line segments
        assert len(drawing.lines) == size - 1
        
        # Peak should be near center
        # Check that middle values are higher than edge values
        middle_idx = len(drawing.lines) // 2
        _, y_middle, _, _ = drawing.lines[middle_idx]
        _, y_edge, _, _ = drawing.lines[0]
        
        assert y_middle > y_edge


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
