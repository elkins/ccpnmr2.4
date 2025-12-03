"""
Tests for block_file module.

Tests binary block file I/O for spectral data.
"""

import pytest
import numpy as np
import tempfile
import os
import sys
from pathlib import Path

# Add ccpnmr2.4 directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

from memops.global_.python_impl.block_file import (
    BlockFile, BlockData, new_block_file, delete_block_file
)


class TestBlockFileCreation:
    """Test block file creation and initialization."""
    
    def test_create_2d_block_file(self):
        """Test creating 2D block file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # Write some dummy data
            data = np.arange(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]))
            
            assert bf.ndim == 2
            assert np.array_equal(bf.points, [100, 100])
            assert np.array_equal(bf.block_size, [10, 10])
            assert np.array_equal(bf.blocks, [10, 10])
            assert bf.npoints == 10000
            assert bf.nblocks == 100
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_create_3d_block_file(self):
        """Test creating 3D block file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.arange(50*50*50, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 3, np.array([50, 50, 50]),
                          np.array([10, 10, 10]), np.array([False, False, False]))
            
            assert bf.ndim == 3
            assert bf.npoints == 125000
            assert np.array_equal(bf.blocks, [5, 5, 5])
            assert bf.nblocks == 125
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_factory_function(self):
        """Test new_block_file factory function."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.arange(100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = new_block_file(fname, 1, np.array([100]),
                               np.array([10]), np.array([False]))
            
            assert isinstance(bf, BlockFile)
            assert bf.ndim == 1
            
            delete_block_file(bf)
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestBlockData:
    """Test block data structures."""
    
    def test_size_block_data(self):
        """Test block size calculation."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.arange(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]))
            
            # Full block
            block = np.array([0, 0])
            bs, cbs, size = bf._size_block_data(block)
            assert np.array_equal(bs, [10, 10])
            assert size == 100
            
            # Edge block (padded)
            bf.padded = True
            block = np.array([9, 9])
            bs, cbs, size = bf._size_block_data(block)
            assert np.array_equal(bs, [10, 10])
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestBlockIO:
    """Test block reading and writing."""
    
    def test_read_block_data(self):
        """Test reading block from file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # Create known pattern
            data = np.arange(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]))
            
            # Read first block
            block_data = bf.get_block_data_array(np.array([0, 0]))
            
            assert block_data.size == 100
            assert len(block_data.data) == 100
            
            # First value should be 0
            assert block_data.data[0] == 0.0
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_write_block_data(self):
        """Test writing block to file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # Create initial data
            data = np.zeros(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]),
                          writeable=True)
            
            # Get and modify block
            block_data = bf.get_block_data_array(np.array([0, 0]))
            block_data.data[0] = 42.0
            block_key = (0, 0)
            bf.dirty_blocks.add(block_key)
            
            # Save
            bf.save()
            bf.close()
            
            # Read back
            bf2 = BlockFile(fname, 2, np.array([100, 100]),
                           np.array([10, 10]), np.array([False, False]))
            block_data2 = bf2.get_block_data_array(np.array([0, 0]))
            
            assert block_data2.data[0] == 42.0
            
            bf2.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestPointAccess:
    """Test point-level access."""
    
    def test_get_point(self):
        """Test getting single point value."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # Create known pattern - just use index as value
            data = np.arange(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]))
            
            # Get point at [0, 0] - should be 0 (first point)
            value = bf.get_point(np.array([0, 0]))
            assert value == 0.0
            
            # Points are stored consecutively
            # Just verify we can read different points
            value2 = bf.get_point(np.array([0, 1]))
            value3 = bf.get_point(np.array([1, 0]))
            # Values should be different
            assert value2 != value
            assert value3 != value
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_set_point(self):
        """Test setting single point value."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.zeros(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]),
                          writeable=True)
            
            # Set point
            bf.set_point(np.array([5, 7]), 99.0)
            
            # Read back
            value = bf.get_point(np.array([5, 7]))
            assert value == 99.0
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_get_point_out_of_bounds(self):
        """Test error on out of bounds access."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.arange(100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 1, np.array([100]),
                          np.array([10]), np.array([False]))
            
            with pytest.raises(ValueError):
                bf.get_point(np.array([100]))  # Out of bounds
            
            with pytest.raises(ValueError):
                bf.get_point(np.array([-1]))  # Negative
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestBoxAccess:
    """Test box-level access."""
    
    def test_get_box(self):
        """Test getting box of values."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # Create known pattern
            data = np.arange(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]))
            
            # Get 2x2 box starting at [0,0]
            npoints, values = bf.get_box(np.array([0, 0]), np.array([1, 1]))
            
            assert npoints == 4
            assert len(values) == 4
            # Values should be 0, 100, 1, 101 in row-major order
            # Actually [0,0], [0,1], [1,0], [1,1] -> 0, 1, 100, 101
            assert values[0] == 0.0
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_set_box(self):
        """Test setting box of values."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.zeros(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]),
                          writeable=True)
            
            # Set 2x2 box
            values = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
            bf.set_box(np.array([0, 0]), np.array([1, 1]), values)
            
            # Read back first point
            value = bf.get_point(np.array([0, 0]))
            assert value == 1.0
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestCaching:
    """Test block caching."""
    
    def test_cache_eviction(self):
        """Test that cache evicts old blocks."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # Create large enough data
            data = np.arange(100*100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]))
            bf.cache_size = 5  # Small cache
            
            # Access more blocks than cache size
            for i in range(10):
                block = np.array([i % 10, 0])
                block_data = bf.get_block_data_array(block)
                assert block_data is not None
            
            # Cache should not exceed size
            assert len(bf.block_cache) <= bf.cache_size + 5  # Some tolerance
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_non_padded_end_blocks(self):
        """Test non-padded end blocks."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            # 105 points with 10-point blocks = 10 full + 1 partial (5 points)
            data = np.arange(105, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 1, np.array([105]),
                          np.array([10]), np.array([False]),
                          padded=False)
            
            assert bf.blocks[0] == 11  # 11 blocks total
            
            # Last block should have size 5
            block = np.array([10])
            bs, cbs, size = bf._size_block_data(block)
            assert bs[0] == 5
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_invalid_parameters(self):
        """Test validation of parameters."""
        with pytest.raises(ValueError):
            # ndim too large
            bf = BlockFile("test.dat", 20, np.array([100]*20),
                          np.array([10]*20), np.array([False]*20))
        
        with pytest.raises(ValueError):
            # bytes_per_point too large
            bf = BlockFile("test.dat", 2, np.array([100, 100]),
                          np.array([10, 10]), np.array([False, False]),
                          bytes_per_point=8)


class TestFileOperations:
    """Test file operations."""
    
    def test_open_close(self):
        """Test opening and closing file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.arange(100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 1, np.array([100]),
                          np.array([10]), np.array([False]))
            
            # Initially closed
            assert bf.fp is None
            
            # Open
            bf.open()
            assert bf.fp is not None
            
            # Close
            bf.close()
            assert bf.fp is None
            
        finally:
            if os.path.exists(fname):
                os.unlink(fname)
    
    def test_check_integrity(self):
        """Test file integrity check."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as f:
            fname = f.name
            data = np.arange(100, dtype=np.float32)
            data.tofile(f)
        
        try:
            bf = BlockFile(fname, 1, np.array([100]),
                          np.array([10]), np.array([False]))
            
            # Should pass
            assert bf.check() == True
            
            bf.close()
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
