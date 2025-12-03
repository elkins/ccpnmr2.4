"""
Tests for py_store_handler module.

Tests Python wrapper that mimics C extension interface.
"""

import pytest
import numpy as np
import tempfile
import os
import sys
from pathlib import Path

# Add ccpnmr2.4 directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from memops.global_.python_impl.py_store_handler import StoreHandler, error


class TestStoreHandlerWrapper:
    """Test StoreHandler wrapper interface."""
    
    def test_create_handler(self):
        """Test creating StoreHandler wrapper."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            assert handler is not None
            
            # Test that we can call methods
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
            
            # File should exist
            assert os.path.exists(fname)
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_create_with_swap(self):
        """Test creating handler with byte swapping."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname, swap=True)
            assert handler is not None
            
            # Initialize and close
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
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestAttributeForwarding:
    """Test that wrapper forwards attributes correctly."""
    
    def test_method_forwarding(self):
        """Test that methods are forwarded to underlying handler."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            # These methods should be available via forwarding
            assert hasattr(handler, 'init_store_save')
            assert hasattr(handler, 'init_store_block')
            assert hasattr(handler, 'init_store_plane')
            assert hasattr(handler, 'init_store_level')
            assert hasattr(handler, 'draw_polyline')
            assert hasattr(handler, 'end_store_plane')
            assert hasattr(handler, 'end_store_save')
            assert hasattr(handler, 'close')
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_attribute_access(self):
        """Test accessing attributes via wrapper."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            
            # Initialize
            ndim = 2
            npoints = np.array([100, 100])
            first = np.array([0, 0])
            last = np.array([100, 100])
            block_size = np.array([100, 100])
            nblocks = np.array([1, 1])
            levels = np.array([1.0])
            
            handler.init_store_save(ndim, 0, 1, npoints, first, last,
                                  block_size, nblocks, 1, levels)
            
            # Can access underlying attributes
            assert handler.ndim == 2
            assert handler.xdim == 0
            assert handler.ydim == 1
            
            handler.end_store_save()
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestWritingData:
    """Test writing data via wrapper."""
    
    def test_write_polylines(self):
        """Test writing polylines via wrapper."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
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
            
            # Write polylines
            vertices = np.array([[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]])
            handler.draw_polyline(vertices)
            
            vertices2 = np.array([[15.0, 25.0], [35.0, 45.0]])
            handler.draw_polyline(vertices2, closed=True)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # File should have data
            assert os.path.exists(fname)
            assert os.path.getsize(fname) > 64  # More than just header
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_multiple_levels(self):
        """Test writing multiple contour levels."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
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
            
            assert os.path.exists(fname)
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestModuleInterface:
    """Test module-level interface."""
    
    def test_error_class_exists(self):
        """Test module error class."""
        assert error is not None
        
        # Can instantiate and raise
        with pytest.raises(error):
            raise error("test error")
            
    def test_factory_function(self):
        """Test StoreHandler factory function."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            handler = StoreHandler(fname)
            assert handler is not None
            
            # Test it works
            handler.init_store_save(2, 0, 1, np.array([100, 100]),
                                  np.array([0, 0]), np.array([100, 100]),
                                  np.array([100, 100]), np.array([1, 1]),
                                  1, np.array([1.0]))
            handler.end_store_save()
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
