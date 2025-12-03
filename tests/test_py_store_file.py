"""
Tests for py_store_file module.

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

from memops.global_.python_impl.py_store_file import StoreFile, error
from memops.global_.python_impl.store_handler import StoreHandler


class TestStoreFileWrapper:
    """Test StoreFile wrapper interface."""
    
    def test_create_from_file(self):
        """Test creating StoreFile wrapper from file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create file
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
            
            # Open with wrapper
            store = StoreFile(fname, ndim, 0, 1, [100, 100])
            
            assert hasattr(store, 'have_pos')
            assert hasattr(store, 'have_neg')
            assert hasattr(store, 'dir_size')
            
            assert store.have_pos == True
            assert store.have_neg == False
            assert store.dir_size == 1
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_attributes(self):
        """Test wrapper attributes."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create minimal file
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
            handler.end_store_save()
            
            # Test attributes
            store = StoreFile(fname, ndim, 0, 1, block_size)
            
            assert store.have_pos == True
            assert store.have_neg == True
            assert isinstance(store.dir_size, int)
            assert store.dir_size > 0
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestProcessContours:
    """Test contour processing via wrapper."""
    
    def test_process_contours_callback(self):
        """Test processing contours with callback."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create file with data
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
            
            vertices = np.array([[10.0, 20.0], [30.0, 40.0], [50.0, 60.0]])
            handler.draw_polyline(vertices)
            
            handler.end_store_plane()
            handler.end_store_save()
            
            # Process via wrapper
            store = StoreFile(fname, ndim, 0, 1, block_size)
            
            results = []
            def callback(user_data, block, plane, level, npolylines, polylines, error_msg):
                results.append({
                    'npolylines': npolylines,
                    'polylines': polylines
                })
                return True
            
            success = store.process_contours([0, 0], [0, 0], callback)
            
            assert success == True
            assert len(results) == 1
            assert results[0]['npolylines'] == 1
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_process_with_numpy_arrays(self):
        """Test process_contours accepts numpy arrays."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create file
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
            
            # Process with numpy arrays
            store = StoreFile(fname, ndim, 0, 1, block_size)
            
            called = []
            def callback(user_data, block, plane, level, npolylines, polylines, error_msg):
                called.append(True)
                return True
            
            block = np.array([0, 0], dtype=np.int32)
            plane = np.array([0, 0], dtype=np.int32)
            
            success = store.process_contours(block, plane, callback)
            assert success == True
            assert len(called) == 1
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
                
    def test_process_with_lists(self):
        """Test process_contours accepts lists."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create file
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
            
            # Process with lists
            store = StoreFile(fname, ndim, 0, 1, [100, 100])
            
            called = []
            def callback(user_data, block, plane, level, npolylines, polylines, error_msg):
                called.append(True)
                return True
            
            success = store.process_contours([0, 0], [0, 0], callback)
            assert success == True
            assert len(called) == 1
            
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
        """Test StoreFile factory function."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.store') as f:
            fname = f.name
            
        try:
            # Create minimal file
            handler = StoreHandler(fname)
            handler.init_store_save(2, 0, 1, np.array([100, 100]),
                                  np.array([0, 0]), np.array([100, 100]),
                                  np.array([100, 100]), np.array([1, 1]),
                                  1, np.array([1.0]))
            handler.end_store_save()
            
            # Test factory
            store = StoreFile(fname, 2, 0, 1, [100, 100])
            assert store is not None
            assert hasattr(store, 'have_pos')
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
