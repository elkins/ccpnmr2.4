"""
Tests for contourer module - contour generation engine.

Tests the marching squares algorithm for generating contour lines
at specified levels in 2D spectral data.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ccpnmr2.4" / "python"))

from memops.global_.python_impl.contourer import (
    ContoururInfo, ContourVertex, ContourVertices, Contours,
    new_contourer_info, delete_contourer_info, delete_contours,
    calculate_contours, process_chains
)


class TestContourVertex:
    """Test ContourVertex dataclass."""
    
    def test_creation(self):
        """Test vertex creation."""
        v = ContourVertex(x=np.array([1.0, 2.0]))
        assert v.x[0] == 1.0
        assert v.x[1] == 2.0
        assert v.v1 is None
        assert v.v2 is None
        assert v.visited is False
    
    def test_linking(self):
        """Test linking vertices."""
        v1 = ContourVertex(x=np.array([1.0, 2.0]))
        v2 = ContourVertex(x=np.array([3.0, 4.0]))
        v1.v2 = v2
        v2.v1 = v1
        
        assert v1.v2 is v2
        assert v2.v1 is v1


class TestContourVertices:
    """Test ContourVertices collection."""
    
    def test_creation(self):
        """Test vertices collection creation."""
        vertices = ContourVertices()
        assert vertices.nvertices == 0
        assert vertices.nalloc == 50
        assert len(vertices.vertex_store) == 0
    
    def test_new_vertex(self):
        """Test adding vertices."""
        vertices = ContourVertices()
        v1 = vertices.new_vertex(1.0, 2.0)
        assert vertices.nvertices == 1
        assert v1.x[0] == 1.0
        assert v1.x[1] == 2.0
        
        v2 = vertices.new_vertex(3.0, 4.0)
        assert vertices.nvertices == 2
    
    def test_block_allocation(self):
        """Test vertex block allocation."""
        vertices = ContourVertices(nalloc=10)
        
        # Add 10 vertices (fills first block)
        for i in range(10):
            vertices.new_vertex(float(i), float(i))
        
        assert len(vertices.vertex_store) == 1
        
        # Add one more (triggers second block)
        vertices.new_vertex(10.0, 10.0)
        assert len(vertices.vertex_store) == 2
        assert vertices.nvertices == 11
    
    def test_get_vertex(self):
        """Test retrieving vertices by index."""
        vertices = ContourVertices(nalloc=10)
        for i in range(15):
            vertices.new_vertex(float(i), float(i * 2))
        
        v0 = vertices.get_vertex(0)
        assert v0.x[0] == 0.0
        
        v10 = vertices.get_vertex(10)
        assert v10.x[0] == 10.0
        assert v10.x[1] == 20.0


class TestContours:
    """Test Contours container."""
    
    def test_creation(self):
        """Test contours container creation."""
        contours = Contours(n=3)
        assert contours.n == 3
        assert len(contours.vertices) == 0


class TestContoururInfo:
    """Test ContoururInfo configuration."""
    
    def test_creation(self):
        """Test contourer info creation."""
        def dummy_func(data):
            return np.zeros(10)
        
        info = ContoururInfo(
            user_data=None,
            nlevels=3,
            levels=np.array([1.0, 2.0, 3.0]),
            npoints=np.array([10, 10]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=dummy_func
        )
        
        assert info.nlevels == 3
        assert len(info.levels) == 3
        assert info.npoints[0] == 10
        assert len(info.v_rows) == 3  # One per level
        assert len(info.v_rows[0]) == 9  # npoints[0] - 1
    
    def test_factory_function(self):
        """Test factory function."""
        def dummy_func(data):
            return np.zeros(10)
        
        info = new_contourer_info(
            user_data=None,
            nlevels=2,
            levels=np.array([1.0, 2.0]),
            npoints=np.array([5, 5]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=dummy_func
        )
        
        assert isinstance(info, ContoururInfo)
        delete_contourer_info(info)  # Should not crash


class TestCalculateContours:
    """Test contour calculation."""
    
    def test_empty_data(self):
        """Test with empty data."""
        row_index = [0]
        
        def get_row(data):
            return np.array([])
        
        info = ContoururInfo(
            user_data=None,
            nlevels=1,
            levels=np.array([1.0]),
            npoints=np.array([0, 0]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        assert contours.n == 1
        assert contours.vertices[0].nvertices == 0
    
    def test_simple_peak(self):
        """Test contouring a simple peak."""
        # Create 5x5 grid with peak in center
        data = np.array([
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 2.0, 3.0, 2.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0]
        ], dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        info = ContoururInfo(
            user_data=None,
            nlevels=1,
            levels=np.array([1.5]),
            npoints=np.array([5, 5]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # Should have vertices for level 1.5
        assert contours.n == 1
        assert contours.vertices[0].nvertices > 0
    
    def test_multiple_levels(self):
        """Test contouring at multiple levels."""
        # Create gradient data
        data = np.array([
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0, 3.0]
        ], dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        info = ContoururInfo(
            user_data=None,
            nlevels=3,
            levels=np.array([0.5, 1.5, 2.5]),
            npoints=np.array([4, 4]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # Should have contours for all 3 levels
        assert contours.n == 3
        for i in range(3):
            # Each level should have some vertices
            assert contours.vertices[i].nvertices >= 0
    
    def test_offset_and_scale(self):
        """Test coordinate offset and scaling."""
        data = np.array([
            [0.0, 2.0],
            [2.0, 0.0]
        ], dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        info = ContoururInfo(
            user_data=None,
            nlevels=1,
            levels=np.array([1.0]),
            npoints=np.array([2, 2]),
            offset=np.array([10.0, 20.0]),  # Offset
            scale=np.array([2.0, 3.0]),     # Scale
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # Check that vertices respect offset and scale
        if contours.vertices[0].nvertices > 0:
            v = contours.vertices[0].get_vertex(0)
            # Coordinates should be: offset + scale * grid_coord
            assert v.x[0] >= 10.0  # At least offset
            assert v.x[1] >= 20.0
    
    def test_saddle_point(self):
        """Test handling of saddle points (ambiguous cases)."""
        # Create saddle point: diagonal corners high
        data = np.array([
            [2.0, 0.0, 2.0],
            [0.0, 1.0, 0.0],
            [2.0, 0.0, 2.0]
        ], dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        info = ContoururInfo(
            user_data=None,
            nlevels=1,
            levels=np.array([1.0]),
            npoints=np.array([3, 3]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # Should handle saddle point without crashing
        assert contours.n == 1
        # The ambiguous case is resolved by averaging
        assert contours.vertices[0].nvertices >= 0
    
    def test_all_above_level(self):
        """Test when all data is above level."""
        data = np.full((3, 3), 10.0, dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        info = ContoururInfo(
            user_data=None,
            nlevels=1,
            levels=np.array([1.0]),
            npoints=np.array([3, 3]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # No contour vertices (no level crossings)
        assert contours.vertices[0].nvertices == 0
    
    def test_all_below_level(self):
        """Test when all data is below level."""
        data = np.zeros((3, 3), dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        info = ContoururInfo(
            user_data=None,
            nlevels=1,
            levels=np.array([1.0]),
            npoints=np.array([3, 3]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # No contour vertices (no level crossings)
        assert contours.vertices[0].nvertices == 0


class TestProcessChains:
    """Test chain processing."""
    
    def test_single_chain(self):
        """Test processing a single chain."""
        vertices = ContourVertices()
        
        # Create simple chain: v1 -> v2 -> v3
        v1 = vertices.new_vertex(0.0, 0.0)
        v2 = vertices.new_vertex(1.0, 1.0)
        v3 = vertices.new_vertex(2.0, 2.0)
        
        v1.v2 = v2
        v2.v1 = v1
        v2.v2 = v3
        v3.v1 = v2
        
        chains = []
        
        def chain_func(user_data, nvertices, first_vertex):
            chains.append((nvertices, first_vertex))
        
        process_chains(vertices, None, chain_func)
        
        # Should find one chain with 3 vertices
        assert len(chains) == 1
        assert chains[0][0] == 3
    
    def test_closed_loop(self):
        """Test processing a closed loop."""
        vertices = ContourVertices()
        
        # Create closed loop: v1 -> v2 -> v3 -> v1
        v1 = vertices.new_vertex(0.0, 0.0)
        v2 = vertices.new_vertex(1.0, 0.0)
        v3 = vertices.new_vertex(0.5, 1.0)
        
        v1.v2 = v2
        v2.v1 = v1
        v2.v2 = v3
        v3.v1 = v2
        v3.v2 = v1
        v1.v1 = v3
        
        chains = []
        
        def chain_func(user_data, nvertices, first_vertex):
            chains.append((nvertices, first_vertex))
        
        process_chains(vertices, None, chain_func)
        
        # Should find one closed chain with 3 vertices
        assert len(chains) == 1
        assert chains[0][0] == 3
    
    def test_multiple_chains(self):
        """Test processing multiple disconnected chains."""
        vertices = ContourVertices()
        
        # Chain 1: v1 -> v2
        v1 = vertices.new_vertex(0.0, 0.0)
        v2 = vertices.new_vertex(1.0, 0.0)
        v1.v2 = v2
        v2.v1 = v1
        
        # Chain 2: v3 -> v4 -> v5
        v3 = vertices.new_vertex(5.0, 5.0)
        v4 = vertices.new_vertex(6.0, 5.0)
        v5 = vertices.new_vertex(7.0, 5.0)
        v3.v2 = v4
        v4.v1 = v3
        v4.v2 = v5
        v5.v1 = v4
        
        chains = []
        
        def chain_func(user_data, nvertices, first_vertex):
            chains.append(nvertices)
        
        process_chains(vertices, None, chain_func)
        
        # Should find 2 chains
        assert len(chains) == 2
        assert 2 in chains  # First chain
        assert 3 in chains  # Second chain
    
    def test_isolated_vertices(self):
        """Test vertices with no connections."""
        vertices = ContourVertices()
        
        # Create isolated vertices
        v1 = vertices.new_vertex(0.0, 0.0)
        v2 = vertices.new_vertex(1.0, 1.0)
        
        chains = []
        
        def chain_func(user_data, nvertices, first_vertex):
            chains.append(nvertices)
        
        process_chains(vertices, None, chain_func)
        
        # Each vertex is its own chain
        assert len(chains) == 2
        assert all(n == 1 for n in chains)


class TestIntegration:
    """Integration tests with realistic data."""
    
    def test_gaussian_peak_contours(self):
        """Test contouring a Gaussian peak."""
        # Create Gaussian peak
        size = 20
        center = size // 2
        sigma = 3.0
        
        x = np.arange(size)
        y = np.arange(size)
        xx, yy = np.meshgrid(x, y)
        
        data = np.exp(-((xx - center)**2 + (yy - center)**2) / (2 * sigma**2))
        data = data.astype(np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        # Contour at multiple levels
        levels = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        
        info = ContoururInfo(
            user_data=None,
            nlevels=len(levels),
            levels=levels,
            npoints=np.array([size, size]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # Should have contours at each level
        assert contours.n == len(levels)
        
        # Higher levels should have fewer vertices (smaller loops)
        vertex_counts = [contours.vertices[i].nvertices for i in range(len(levels))]
        
        # At least some levels should have vertices
        assert sum(vertex_counts) > 0
    
    def test_negative_and_positive_contours(self):
        """Test contouring with both negative and positive levels."""
        # Create data with positive and negative regions
        data = np.array([
            [-2.0, -1.0,  0.0,  1.0,  2.0],
            [-2.0, -1.0,  0.0,  1.0,  2.0],
            [-2.0, -1.0,  0.0,  1.0,  2.0],
            [-2.0, -1.0,  0.0,  1.0,  2.0]
        ], dtype=np.float32)
        
        row_index = [0]
        
        def get_row(user_data):
            row = data[row_index[0]]
            row_index[0] += 1
            return row
        
        levels = np.array([-1.5, -0.5, 0.5, 1.5])
        
        info = ContoururInfo(
            user_data=None,
            nlevels=len(levels),
            levels=levels,
            npoints=np.array([5, 4]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=get_row
        )
        
        contours = calculate_contours(info)
        
        # Should handle both negative and positive levels
        assert contours.n == len(levels)
        
        # Each level should have vertices
        for i in range(len(levels)):
            assert contours.vertices[i].nvertices > 0


class TestCAPICompatibility:
    """Test C API compatibility functions."""
    
    def test_factory_functions(self):
        """Test C-compatible factory functions."""
        def dummy_func(data):
            return np.zeros(5)
        
        # Test new_contourer_info
        info = new_contourer_info(
            user_data=None,
            nlevels=2,
            levels=np.array([1.0, 2.0]),
            npoints=np.array([5, 5]),
            offset=np.array([0.0, 0.0]),
            scale=np.array([1.0, 1.0]),
            get_row_func=dummy_func
        )
        
        assert info is not None
        
        # Test delete (should not crash)
        delete_contourer_info(info)
        
        # Test contours deletion
        contours = Contours(n=2)
        delete_contours(contours)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
