"""
Tests for store_file module.

Tests reading contour storage files created by store_handler.
"""

import pytest
import numpy as np
import tempfile
import os
import sys
from pathlib import Path

# Add ccpnmr2.4 directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from memops.global_.python_impl.store_file import (
    StoreFile, Polyline, new_store_file, delete_store_file
)
from memops.global_.python_impl.store_handler import (
    StoreHandler, new_store_handler
)


class TestStoreFileCreation:
    """Test store file opening."""
    
    def test_open_invalid_file(self):
        """Test opening non-existent file."""
        with pytest.raises(IOError):
            store_file = StoreFile("/invalid/path/file.dat", 2, 0, 1,
                                  np.array([10, 10]))
                                  
    def test_open_empty_file(self):
        """Test opening empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            with pytest.raises(IOError):
                store_file = StoreFile(fname, 2, 0, 1, np.array([10, 10]))
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestRoundTrip:
    """Test writing with store_handler and reading with store_file."""
    
    def test_simple_roundtrip(self):
        """Test writing and reading back polylines."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Write file
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(1.0)
            
            # Write polyline
            vertices = np.array([[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]])
            handler.draw_polyline(vertices)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # Read file back
            store_file = StoreFile(fname, ndim, 0, 1, block_size)
            
            assert store_file.ndim == 2
            assert store_file.have_pos == True
            assert store_file.have_neg == False
            
            # Process contours
            results = []
            
            def collect_polylines(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.append({
                    'block': block.copy(),
                    'plane': plane.copy(),
                    'level': level,
                    'npolylines': npolylines,
                    'polylines': polylines
                })
                return True
            
            success = store_file.process_contours(np.array([0, 0]), np.array([0, 0]),
                                                 collect_polylines)
            
            assert success == True
            assert len(results) == 1
            assert results[0]['npolylines'] == 1
            assert len(results[0]['polylines']) == 1
            
            polyline = results[0]['polylines'][0]
            assert polyline.nvertices == 3
            np.testing.assert_array_almost_equal(polyline.vertices, vertices)
            
            store_file.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_closed_polyline_roundtrip(self):
        """Test closed polyline roundtrip."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Write
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(1.0)
            
            vertices = np.array([[10.0, 20.0], [30.0, 40.0], [50.0, 20.0]])
            handler.draw_polyline(vertices, closed=True)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # Read
            store_file = StoreFile(fname, ndim, 0, 1, block_size)
            
            results = []
            def collect(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.extend(polylines)
                return True
            
            store_file.process_contours(np.array([0, 0]), np.array([0, 0]), collect)
            
            assert len(results) == 1
            assert results[0].closed == True
            
            store_file.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_multiple_polylines_roundtrip(self):
        """Test multiple polylines roundtrip."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Write
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(1.0)
            
            # Write three polylines
            for i in range(3):
                vertices = np.array([[i*10.0, i*20.0], [(i+1)*30.0, (i+1)*40.0]])
                handler.draw_polyline(vertices)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # Read
            store_file = StoreFile(fname, ndim, 0, 1, block_size)
            
            results = []
            def collect(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.extend(polylines)
                return True
            
            store_file.process_contours(np.array([0, 0]), np.array([0, 0]), collect)
            
            assert len(results) == 3
            
            store_file.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestPosNegRoundtrip:
    """Test positive and negative contours."""
    
    def test_pos_and_neg_roundtrip(self):
        """Test both positive and negative levels."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Write
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([-1.0, 1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 2, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            
            # Negative level
            handler.init_store_level(-1.0)
            vertices_neg = np.array([[10.0, 20.0], [30.0, 40.0]])
            handler.draw_polyline(vertices_neg)
            
            # Positive level
            handler.init_store_level(1.0)
            vertices_pos = np.array([[50.0, 60.0], [70.0, 80.0]])
            handler.draw_polyline(vertices_pos)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # Read
            store_file = StoreFile(fname, ndim, 0, 1, block_size)
            
            assert store_file.have_pos == True
            assert store_file.have_neg == True
            
            results = []
            def collect(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.append({
                    'level': level,
                    'npolylines': npolylines,
                    'polylines': polylines
                })
                return True
            
            store_file.process_contours(np.array([0, 0]), np.array([0, 0]), collect)
            
            # Should have both negative (level=0) and positive (level=1)
            assert len(results) == 2
            assert results[0]['level'] == 0  # Negative
            assert results[1]['level'] == 1  # Positive
            
            store_file.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestTranspose:
    """Test coordinate transposition."""
    
    def test_transposed_coordinates(self):
        """Test transposed reading."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Write
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(1.0)
            
            vertices = np.array([[10.0, 20.0], [30.0, 40.0]])
            handler.draw_polyline(vertices)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # Read with transpose
            store_file = StoreFile(fname, ndim, 0, 1, block_size)
            
            results = []
            def collect(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.extend(polylines)
                return True
            
            store_file.process_contours(np.array([0, 0]), np.array([0, 0]),
                                       collect, transposed=True)
            
            assert len(results) == 1
            # Coordinates should be swapped
            expected = np.array([[20.0, 10.0], [40.0, 30.0]])
            np.testing.assert_array_almost_equal(results[0].vertices, expected)
            
            store_file.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestEmptyBlocks:
    """Test handling of empty blocks."""
    
    def test_empty_block(self):
        """Test reading block with no data."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Write file with no polylines
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            # Don't write any polylines
            handler.end_store_plane()
            handler.end_store_save()
            
            # Read
            store_file = StoreFile(fname, ndim, 0, 1, block_size)
            
            results = []
            def collect(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.append(npolylines)
                return True
            
            store_file.process_contours(np.array([0, 0]), np.array([0, 0]), collect)
            
            assert len(results) == 1
            assert results[0] == 0  # No polylines
            
            store_file.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestCAPIFunctions:
    """Test C API compatibility functions."""
    
    def test_new_and_delete_functions(self):
        """Test new_store_file and delete_store_file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create simple file first
            handler = StoreHandler(fname)
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            handler.end_store_save()
            
            # Test C API functions
            store_file = new_store_file(fname, ndim, 0, 1, block_size)
            assert isinstance(store_file, StoreFile)
            delete_store_file(store_file)
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
