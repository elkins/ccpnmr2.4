"""
Tests for store_handler module.

Tests contour storage for disk-based caching.
"""

import pytest
import numpy as np
import tempfile
import os
import struct
import sys
from pathlib import Path

# Add ccpnmr2.4 directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from memops.global_.python_impl.store_handler import (
    StoreHandler, new_store_handler, delete_store_handler,
    store_drawing_funcs,
    STORE_MAGIC, STORE_VERSION, STORE_DRAWING,
    HEADER0, HEADER1, HEADER2, BYTES_PER_WORD
)


class TestConstants:
    """Test module constants."""
    
    def test_store_magic(self):
        """Test magic constant."""
        assert STORE_MAGIC == 0x5354524F
        
    def test_store_version(self):
        """Test version constant."""
        assert STORE_VERSION == 1
        
    def test_header_constants(self):
        """Test header size constants."""
        assert HEADER0 == 7
        assert HEADER1 == 4
        assert HEADER2 == 1
        assert BYTES_PER_WORD == 4


class TestStoreHandlerCreation:
    """Test store handler creation."""
    
    def test_create_handler(self):
        """Test creating store handler."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            assert handler.fp is not None
            assert handler.swap == False
            handler.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_create_with_swap(self):
        """Test creating with byte swapping."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname, swap=True)
            assert handler.swap == True
            handler.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_create_invalid_file(self):
        """Test creating with invalid file path."""
        with pytest.raises(IOError):
            handler = StoreHandler("/invalid/path/file.dat")
            
    def test_new_store_handler_function(self):
        """Test new_store_handler function."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = new_store_handler(fname)
            assert isinstance(handler, StoreHandler)
            delete_store_handler(handler)
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestInitStoreSave:
    """Test storage initialization."""
    
    def test_init_2d_storage(self):
        """Test initializing 2D storage."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 200])
            first = np.array([0, 0])
            last = np.array([100, 200])
            block_size = np.array([10, 20])
            nblocks = np.array([10, 10])
            levels = np.array([-2.0, -1.0, 1.0, 2.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 4, levels)
            
            assert handler.ndim == 2
            assert handler.xdim == 0
            assert handler.ydim == 1
            assert handler.have_pos == True
            assert handler.have_neg == True
            assert handler.directory is not None
            
            handler.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_init_3d_storage(self):
        """Test initializing 3D storage."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            ndim = 3
            npoints = np.array([100, 200, 150])
            first = np.array([0, 0, 50])
            last = np.array([100, 200, 100])
            block_size = np.array([10, 20, 10])
            nblocks = np.array([10, 10, 1])
            levels = np.array([1.0, 2.0])  # Only positive
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 2, levels)
            
            assert handler.ndim == 3
            assert handler.have_pos == True
            assert handler.have_neg == False
            # Directory size should not be doubled (only positive)
            
            handler.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestPolylineStorage:
    """Test polyline writing."""
    
    def test_write_single_polyline(self):
        """Test writing single polyline."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            # Initialize 2D storage
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            # Set block and plane
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(1.0)
            
            # Write polyline
            vertices = np.array([[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]])
            handler.draw_polyline(vertices)
            
            assert handler.npos_polys == 1
            
            handler.end_store_plane()
            handler.end_store_save()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_write_closed_polyline(self):
        """Test writing closed polyline."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
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
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_write_multiple_polylines(self):
        """Test writing multiple polylines."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
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
            
            assert handler.npos_polys == 3
            
            handler.end_store_plane()
            handler.end_store_save()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestPosNegLevels:
    """Test positive and negative level handling."""
    
    def test_positive_and_negative_levels(self):
        """Test storage with both positive and negative levels."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
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
            
            # Write negative level
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(-1.0)
            
            vertices = np.array([[10.0, 20.0], [30.0, 40.0]])
            handler.draw_polyline(vertices)
            assert handler.nneg_polys == 1
            
            # Write positive level
            handler.init_store_level(1.0)
            vertices = np.array([[50.0, 60.0], [70.0, 80.0]])
            handler.draw_polyline(vertices)
            assert handler.npos_polys == 1
            
            handler.end_store_plane()
            handler.end_store_save()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestDirectoryIndexing:
    """Test directory index calculation."""
    
    def test_get_dir_index_2d(self):
        """Test directory index for 2D case."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([10, 10])
            nblocks = np.array([10, 10])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            handler.init_store_block(np.array([0, 0]))
            handler.init_store_plane(np.array([0, 0]))
            handler.init_store_level(1.0)
            
            idx = handler._get_dir_index()
            assert idx == 0  # First block
            
            handler.init_store_block(np.array([1, 0]))
            idx = handler._get_dir_index()
            assert idx == 1  # Second block in x
            
            handler.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestFileFormat:
    """Test binary file format."""
    
    def test_header_format(self):
        """Test header is written correctly."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            ndim = 2
            npoints = np.array([100, 200])
            first = np.array([0, 0])
            last = np.array([100, 200])
            block_size = np.array([10, 20])
            nblocks = np.array([10, 10])
            levels = np.array([1.0, 2.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 2, levels)
            handler.end_store_save()
            
            # Read and verify header
            with open(fname, 'rb') as f:
                magic = struct.unpack('i', f.read(4))[0]
                assert magic == STORE_MAGIC
                
                version = struct.unpack('i', f.read(4))[0]
                assert version == STORE_VERSION
                
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestDrawingFunctions:
    """Test drawing functions interface."""
    
    def test_get_drawing_funcs(self):
        """Test getting drawing functions."""
        funcs = store_drawing_funcs()
        assert funcs['type'] == STORE_DRAWING
        assert 'draw_polyline' in funcs
        assert 'draw_clipped_polyline' in funcs
        
    def test_drawing_funcs_callable(self):
        """Test drawing functions are callable."""
        funcs = store_drawing_funcs()
        
        # Most functions should be no-ops
        funcs['start_draw'](None)
        funcs['end_draw'](None)
        funcs['draw_line'](None, 0, 0, 1, 1)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_storage(self):
        """Test storage with no polylines."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
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
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_single_point_polyline(self):
        """Test polyline with single point."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
            
        try:
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
            
            vertices = np.array([[10.0, 20.0]])
            handler.draw_polyline(vertices)
            
            handler.end_store_plane()
            handler.end_store_save()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
