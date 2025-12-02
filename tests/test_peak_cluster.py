"""
Tests for peak_cluster module.

Tests the PeakCluster class for grouping related NMR peaks.
"""

import pytest
from ccpnmr.analysis.python_impl.peak_cluster import (
    PeakCluster, PeakClusterType,
    new_peak_cluster, delete_peak_cluster,
    add_peak_peak_cluster, remove_peak_peak_cluster,
    set_peaks_peak_cluster, clear_peaks_peak_cluster,
    set_text_peak_cluster, set_dim_text_peak_cluster,
    draw_peak_cluster
)


# Mock Peak class for testing
class MockPeak:
    """Mock peak object for testing."""
    def __init__(self, ndim, position):
        self.ndim = ndim
        self.position = position
        
    def __eq__(self, other):
        return (isinstance(other, MockPeak) and 
                self.ndim == other.ndim and
                self.position == other.position)


class TestPeakClusterCreation:
    """Test peak cluster creation and initialization."""
    
    def test_create_2d_multiplet(self):
        """Test creating 2D multiplet cluster."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        assert pc.ndim == 2
        assert pc.cluster_type == PeakClusterType.MULTIPLET
        assert pc.text == ""
        assert pc.dim_text == ["", ""]
        assert len(pc.peaks) == 0
        
    def test_create_3d_shift(self):
        """Test creating 3D shift cluster."""
        pc = PeakCluster(3, PeakClusterType.SHIFT)
        assert pc.ndim == 3
        assert pc.cluster_type == PeakClusterType.SHIFT
        assert len(pc.dim_text) == 3
        
    def test_create_static_type(self):
        """Test creating static cluster."""
        pc = PeakCluster(2, PeakClusterType.STATIC)
        assert pc.cluster_type == PeakClusterType.STATIC
        
    def test_create_symmetry_type(self):
        """Test creating symmetry cluster."""
        pc = PeakCluster(2, PeakClusterType.SYMMETRY)
        assert pc.cluster_type == PeakClusterType.SYMMETRY
        
    def test_create_invalid_ndim(self):
        """Test that invalid ndim raises error."""
        with pytest.raises(ValueError, match="ndim must be positive"):
            PeakCluster(0, PeakClusterType.MULTIPLET)
        with pytest.raises(ValueError, match="ndim must be positive"):
            PeakCluster(-1, PeakClusterType.MULTIPLET)
            
    def test_create_invalid_type(self):
        """Test that invalid cluster type raises error."""
        with pytest.raises(ValueError, match="cluster_type must be 0-3"):
            PeakCluster(2, 4)
        with pytest.raises(ValueError, match="cluster_type must be 0-3"):
            PeakCluster(2, -1)


class TestAddRemovePeaks:
    """Test adding and removing peaks."""
    
    def test_add_single_peak(self):
        """Test adding one peak."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak = MockPeak(2, [1.0, 2.0])
        pc.add_peak(peak)
        assert len(pc.peaks) == 1
        assert pc.peaks[0] == peak
        
    def test_add_multiple_peaks(self):
        """Test adding multiple peaks."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak1 = MockPeak(2, [1.0, 2.0])
        peak2 = MockPeak(2, [1.1, 2.1])
        peak3 = MockPeak(2, [1.2, 2.2])
        
        pc.add_peak(peak1)
        pc.add_peak(peak2)
        pc.add_peak(peak3)
        
        assert len(pc.peaks) == 3
        assert pc.peaks[0] == peak1
        assert pc.peaks[1] == peak2
        assert pc.peaks[2] == peak3
        
    def test_add_peak_wrong_ndim(self):
        """Test that adding peak with wrong ndim fails."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak = MockPeak(3, [1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError, match="peak_cluster ndim = 2 != 3 = peak ndim"):
            pc.add_peak(peak)
            
    def test_remove_peak(self):
        """Test removing a peak."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak1 = MockPeak(2, [1.0, 2.0])
        peak2 = MockPeak(2, [1.1, 2.1])
        
        pc.add_peak(peak1)
        pc.add_peak(peak2)
        assert len(pc.peaks) == 2
        
        pc.remove_peak(peak1)
        assert len(pc.peaks) == 1
        assert pc.peaks[0] == peak2
        
    def test_remove_peak_not_in_cluster(self):
        """Test that removing non-existent peak doesn't error."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak1 = MockPeak(2, [1.0, 2.0])
        peak2 = MockPeak(2, [1.1, 2.1])
        
        pc.add_peak(peak1)
        pc.remove_peak(peak2)  # Not in cluster, should not error
        assert len(pc.peaks) == 1
        
    def test_remove_middle_peak(self):
        """Test removing peak from middle of list."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak1 = MockPeak(2, [1.0, 2.0])
        peak2 = MockPeak(2, [1.1, 2.1])
        peak3 = MockPeak(2, [1.2, 2.2])
        
        pc.add_peak(peak1)
        pc.add_peak(peak2)
        pc.add_peak(peak3)
        
        pc.remove_peak(peak2)
        assert len(pc.peaks) == 2
        assert pc.peaks[0] == peak1
        assert pc.peaks[1] == peak3


class TestSetPeaks:
    """Test setting and clearing peaks."""
    
    def test_set_peaks(self):
        """Test replacing all peaks."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak1 = MockPeak(2, [1.0, 2.0])
        peak2 = MockPeak(2, [1.1, 2.1])
        
        pc.add_peak(peak1)
        assert len(pc.peaks) == 1
        
        new_peaks = [MockPeak(2, [2.0, 3.0]), MockPeak(2, [2.1, 3.1])]
        pc.set_peaks(new_peaks)
        
        assert len(pc.peaks) == 2
        assert pc.peaks == new_peaks
        
    def test_clear_peaks(self):
        """Test clearing all peaks."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak1 = MockPeak(2, [1.0, 2.0])
        peak2 = MockPeak(2, [1.1, 2.1])
        
        pc.add_peak(peak1)
        pc.add_peak(peak2)
        assert len(pc.peaks) == 2
        
        pc.clear_peaks()
        assert len(pc.peaks) == 0
        
    def test_clear_empty_cluster(self):
        """Test clearing already empty cluster."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.clear_peaks()
        assert len(pc.peaks) == 0


class TestTextLabels:
    """Test text label management."""
    
    def test_set_text(self):
        """Test setting cluster text."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.set_text("Doublet")
        assert pc.text == "Doublet"
        
    def test_set_text_overwrites(self):
        """Test that setting text overwrites previous."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.set_text("Old")
        pc.set_text("New")
        assert pc.text == "New"
        
    def test_set_dim_text(self):
        """Test setting dimension text."""
        pc = PeakCluster(3, PeakClusterType.MULTIPLET)
        pc.set_dim_text(0, "H1")
        pc.set_dim_text(1, "N15")
        pc.set_dim_text(2, "C13")
        
        assert pc.dim_text[0] == "H1"
        assert pc.dim_text[1] == "N15"
        assert pc.dim_text[2] == "C13"
        
    def test_set_dim_text_invalid_dim(self):
        """Test that invalid dimension raises error."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        
        with pytest.raises(ValueError, match="dim = -1, must be between 0 and 1"):
            pc.set_dim_text(-1, "Test")
            
        with pytest.raises(ValueError, match="dim = 2, must be between 0 and 1"):
            pc.set_dim_text(2, "Test")


class TestBoundingBox:
    """Test bounding box calculation."""
    
    def test_bounding_box_single_peak(self):
        """Test bounding box with single peak."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        peak = MockPeak(2, [1.5, 2.5])
        pc.add_peak(peak)
        
        bbox = pc.get_bounding_box(0, 1)
        assert bbox == (1.5, 1.5, 2.5, 2.5)
        
    def test_bounding_box_multiple_peaks(self):
        """Test bounding box with multiple peaks."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        pc.add_peak(MockPeak(2, [3.0, 4.0]))
        pc.add_peak(MockPeak(2, [2.0, 1.0]))
        
        bbox = pc.get_bounding_box(0, 1)
        assert bbox == (1.0, 3.0, 1.0, 4.0)
        
    def test_bounding_box_3d(self):
        """Test bounding box in 3D space."""
        pc = PeakCluster(3, PeakClusterType.MULTIPLET)
        pc.add_peak(MockPeak(3, [1.0, 2.0, 3.0]))
        pc.add_peak(MockPeak(3, [4.0, 5.0, 6.0]))
        pc.add_peak(MockPeak(3, [2.0, 1.0, 4.0]))
        
        # X-Y plane
        bbox = pc.get_bounding_box(0, 1)
        assert bbox == (1.0, 4.0, 1.0, 5.0)
        
        # X-Z plane
        bbox = pc.get_bounding_box(0, 2)
        assert bbox == (1.0, 4.0, 3.0, 6.0)
        
        # Y-Z plane
        bbox = pc.get_bounding_box(1, 2)
        assert bbox == (1.0, 5.0, 3.0, 6.0)
        
    def test_bounding_box_no_peaks(self):
        """Test bounding box with no peaks."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        bbox = pc.get_bounding_box(0, 1)
        assert bbox is None
        
    def test_bounding_box_invalid_dims(self):
        """Test bounding box with invalid dimensions."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        
        assert pc.get_bounding_box(-1, 1) is None
        assert pc.get_bounding_box(0, 2) is None
        assert pc.get_bounding_box(2, 0) is None


class TestDrawing:
    """Test drawing functionality."""
    
    def test_draw_calls_callbacks(self):
        """Test that draw calls drawing functions."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        pc.add_peak(MockPeak(2, [3.0, 4.0]))
        pc.set_text("Cluster")
        pc.set_dim_text(0, "X")
        pc.set_dim_text(1, "Y")
        
        lines = []
        texts = []
        
        def draw_line(data, x1, y1, x2, y2):
            lines.append((x1, y1, x2, y2))
            
        def draw_text(data, text, x, y, dx, dy):
            texts.append((text, x, y, dx, dy))
            
        drawing_funcs = {
            'draw_line': draw_line,
            'draw_text': draw_text
        }
        
        pc.draw(0, 1, drawing_funcs, None)
        
        # Should draw 4 lines (box)
        assert len(lines) == 4
        assert lines[0] == (1.0, 2.0, 3.0, 2.0)  # Bottom
        assert lines[1] == (3.0, 2.0, 3.0, 4.0)  # Right
        assert lines[2] == (3.0, 4.0, 1.0, 4.0)  # Top
        assert lines[3] == (1.0, 4.0, 1.0, 2.0)  # Left
        
        # Should draw 3 texts (x label, y label, cluster label)
        assert len(texts) == 3
        assert texts[0] == ("X", 2.0, 4.0, 0.0, 0.0)  # X label at top
        assert texts[1] == ("Y", 3.0, 3.0, 0.0, 0.0)  # Y label at right
        assert texts[2] == ("Cluster", 2.0, 3.0, 0.0, 0.0)  # Cluster at center
        
    def test_draw_no_labels(self):
        """Test drawing without labels."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        pc.add_peak(MockPeak(2, [3.0, 4.0]))
        
        lines = []
        texts = []
        
        def draw_line(data, x1, y1, x2, y2):
            lines.append((x1, y1, x2, y2))
            
        def draw_text(data, text, x, y, dx, dy):
            texts.append((text, x, y, dx, dy))
            
        drawing_funcs = {
            'draw_line': draw_line,
            'draw_text': draw_text
        }
        
        pc.draw(0, 1, drawing_funcs, None)
        
        # Should draw box but no text
        assert len(lines) == 4
        assert len(texts) == 0
        
    def test_draw_no_peaks(self):
        """Test that drawing with no peaks does nothing."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        
        lines = []
        
        def draw_line(data, x1, y1, x2, y2):
            lines.append((x1, y1, x2, y2))
            
        drawing_funcs = {'draw_line': draw_line}
        
        pc.draw(0, 1, drawing_funcs, None)
        assert len(lines) == 0
        
    def test_draw_invalid_dims(self):
        """Test that drawing with invalid dims does nothing."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        
        lines = []
        def draw_line(data, x1, y1, x2, y2):
            lines.append((x1, y1, x2, y2))
            
        drawing_funcs = {'draw_line': draw_line}
        
        pc.draw(-1, 1, drawing_funcs, None)
        assert len(lines) == 0
        
        pc.draw(0, 2, drawing_funcs, None)
        assert len(lines) == 0


class TestCAPIFunctions:
    """Test C API compatibility functions."""
    
    def test_new_peak_cluster(self):
        """Test new_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        assert isinstance(pc, PeakCluster)
        assert pc.ndim == 2
        assert pc.cluster_type == PeakClusterType.MULTIPLET
        
    def test_delete_peak_cluster(self):
        """Test delete_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        delete_peak_cluster(pc)  # Should not error
        
    def test_add_peak_peak_cluster(self):
        """Test add_peak_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        peak = MockPeak(2, [1.0, 2.0])
        
        error_msg = []
        result = add_peak_peak_cluster(pc, peak, error_msg)
        
        assert result is True
        assert len(pc.peaks) == 1
        assert len(error_msg) == 0
        
    def test_add_peak_peak_cluster_error(self):
        """Test add_peak_peak_cluster with error."""
        pc = new_peak_cluster(2, 0)
        peak = MockPeak(3, [1.0, 2.0, 3.0])
        
        error_msg = []
        result = add_peak_peak_cluster(pc, peak, error_msg)
        
        assert result is False
        assert len(error_msg) == 1
        assert "ndim" in error_msg[0]
        
    def test_remove_peak_peak_cluster(self):
        """Test remove_peak_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        peak = MockPeak(2, [1.0, 2.0])
        pc.add_peak(peak)
        
        remove_peak_peak_cluster(pc, peak)
        assert len(pc.peaks) == 0
        
    def test_set_peaks_peak_cluster(self):
        """Test set_peaks_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        peaks = [MockPeak(2, [1.0, 2.0]), MockPeak(2, [1.1, 2.1])]
        
        set_peaks_peak_cluster(pc, peaks)
        assert len(pc.peaks) == 2
        
    def test_clear_peaks_peak_cluster(self):
        """Test clear_peaks_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        
        clear_peaks_peak_cluster(pc)
        assert len(pc.peaks) == 0
        
    def test_set_text_peak_cluster(self):
        """Test set_text_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        
        error_msg = []
        result = set_text_peak_cluster(pc, "Test", error_msg)
        
        assert result is True
        assert pc.text == "Test"
        assert len(error_msg) == 0
        
    def test_set_dim_text_peak_cluster(self):
        """Test set_dim_text_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        
        error_msg = []
        result = set_dim_text_peak_cluster(pc, 0, "H1", error_msg)
        
        assert result is True
        assert pc.dim_text[0] == "H1"
        assert len(error_msg) == 0
        
    def test_set_dim_text_peak_cluster_error(self):
        """Test set_dim_text_peak_cluster with error."""
        pc = new_peak_cluster(2, 0)
        
        error_msg = []
        result = set_dim_text_peak_cluster(pc, 5, "Test", error_msg)
        
        assert result is False
        assert len(error_msg) == 1
        
    def test_draw_peak_cluster(self):
        """Test draw_peak_cluster function."""
        pc = new_peak_cluster(2, 0)
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        
        lines = []
        def draw_line(data, x1, y1, x2, y2):
            lines.append((x1, y1, x2, y2))
            
        drawing_funcs = {'draw_line': draw_line}
        
        draw_peak_cluster(pc, 0, 1, drawing_funcs, None)
        assert len(lines) == 4


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_len(self):
        """Test __len__ method."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        assert len(pc) == 0
        
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        assert len(pc) == 1
        
        pc.add_peak(MockPeak(2, [1.1, 2.1]))
        assert len(pc) == 2
        
    def test_repr(self):
        """Test __repr__ method."""
        pc = PeakCluster(2, PeakClusterType.MULTIPLET)
        assert repr(pc) == "PeakCluster(MULTIPLET, 0 peaks)"
        
        pc.add_peak(MockPeak(2, [1.0, 2.0]))
        assert repr(pc) == "PeakCluster(MULTIPLET, 1 peaks)"
        
        pc.set_text("Test")
        assert repr(pc) == "PeakCluster(MULTIPLET, 1 peaks 'Test')"
        
    def test_repr_different_types(self):
        """Test __repr__ with different cluster types."""
        pc_shift = PeakCluster(2, PeakClusterType.SHIFT)
        assert "SHIFT" in repr(pc_shift)
        
        pc_static = PeakCluster(2, PeakClusterType.STATIC)
        assert "STATIC" in repr(pc_static)
        
        pc_sym = PeakCluster(2, PeakClusterType.SYMMETRY)
        assert "SYMMETRY" in repr(pc_sym)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
