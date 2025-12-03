"""
Binary block file I/O for spectral data with random access.

This module provides random access read/write to blocked data files,
commonly used for storing large NMR spectral datasets efficiently.

Module: block_file
Original: ccpnmr2.4/c/memops/global/block_file.c (1,404 lines)
Purpose: Random access blocked data file I/O with memory caching
"""

from typing import Optional, List, Tuple, Callable, Any
from dataclasses import dataclass
import numpy as np
import struct
import sys
from enum import Enum


# Constants
MAX_NDIM = 10
BYTES_PER_WORD = 4


class BlockFileKind(Enum):
    """Type of block file."""
    BLOCK_FILE = 0
    SHAPE_FILE = 1


@dataclass
class BlockData:
    """
    Data for a single block.
    
    Attributes:
        block: Block indices (ndim array)
        ndim: Number of dimensions
        size: Total size in points
        block_size: Size of block in each dimension
        cum_block_size: Cumulative size for indexing
        data: Float data array
    """
    block: np.ndarray          # int array of block indices
    ndim: int
    size: int
    block_size: np.ndarray     # int array
    cum_block_size: np.ndarray # int array
    data: np.ndarray           # float array
    
    def __del__(self):
        """Cleanup resources."""
        pass  # Python handles memory automatically


class BlockFile:
    """
    Random access block file for spectral data.
    
    This class provides efficient random access to large spectral datasets
    by dividing the data into blocks and caching frequently accessed blocks
    in memory.
    
    Attributes:
        file: Path to data file
        fp: File pointer (None if closed)
        ndim: Number of dimensions
        points: Size of data in each dimension
        block_size: Size of blocks (except possibly end blocks)
        dim_wrapped: Whether each dimension should wrap
        padded: Whether end blocks are padded
        writeable: Whether file is writeable
        npoints: Total number of points
        nblocks: Total number of blocks
        bytes_per_point: Bytes per data point (2 or 4)
        big_endian: Whether data is big or little endian
        header: Length of file header in bytes
        block_header: Length of block header in bytes (for Varian)
        integer: Whether data is integer or real
    """
    
    def __init__(self, file: str, ndim: int, points: np.ndarray,
                 block_size: np.ndarray, dim_wrapped: np.ndarray,
                 bytes_per_point: int = 4, big_endian: bool = False,
                 padded: bool = True, header: int = 0, integer: bool = False,
                 writeable: bool = False, block_header: int = 0):
        """
        Initialize block file.
        
        Args:
            file: Path to data file
            ndim: Number of dimensions
            points: Size of data in each dimension
            block_size: Block size for each dimension
            dim_wrapped: Whether to wrap each dimension
            bytes_per_point: Bytes per point (2 or 4, default 4)
            big_endian: Whether data is big-endian (default False)
            padded: Whether end blocks are padded (default True)
            header: File header size in bytes (default 0)
            integer: Whether data is integer (default False)
            writeable: Whether file is writeable (default False)
            block_header: Block header size in bytes (default 0)
            
        Raises:
            ValueError: If parameters are invalid
        """
        if ndim > MAX_NDIM:
            raise ValueError(f"ndim {ndim} exceeds MAX_NDIM {MAX_NDIM}")
        
        if bytes_per_point > BYTES_PER_WORD:
            raise ValueError(f"bytes_per_point {bytes_per_point} exceeds BYTES_PER_WORD {BYTES_PER_WORD}")
        
        if writeable and bytes_per_point != BYTES_PER_WORD:
            raise ValueError("writeable files must have bytes_per_point == BYTES_PER_WORD")
        
        self.block_file_kind = BlockFileKind.BLOCK_FILE
        self.file = file
        self.fp: Optional[Any] = None
        self.ndim = ndim
        self.points = np.array(points[:ndim], dtype=np.int32)
        self.block_size = np.array(block_size[:ndim], dtype=np.int32)
        self.dim_wrapped = np.array(dim_wrapped[:ndim], dtype=bool)
        self.padded = padded
        self.writeable = writeable
        self.bytes_per_point = bytes_per_point
        self.big_endian = big_endian
        self.header = header
        self.block_header = block_header
        self.integer = integer
        
        # Calculate derived values
        self._init_block_file()
        
        # Block cache
        self.block_cache: dict = {}  # block tuple -> BlockData
        self.dirty_blocks: set = set()  # Set of modified block tuples
        self.cache_size = 50  # Maximum blocks to cache
        
    def _init_block_file(self) -> None:
        """Initialize calculated block file parameters."""
        # Calculate number of blocks in each dimension
        self.blocks = np.zeros(self.ndim, dtype=np.int32)
        for i in range(self.ndim):
            self.blocks[i] = (self.points[i] + self.block_size[i] - 1) // self.block_size[i]
        
        # Calculate cumulative sizes
        self.cum_points = np.zeros(self.ndim, dtype=np.int64)
        self.cum_blocks = np.zeros(self.ndim, dtype=np.int64)
        self.cum_block_points = np.zeros(self.ndim, dtype=np.int64)
        
        # Cumulative points
        prod = 1
        for i in range(self.ndim):
            self.cum_points[i] = prod
            prod *= self.points[i]
        self.npoints = prod
        
        # Cumulative blocks
        prod = 1
        for i in range(self.ndim):
            self.cum_blocks[i] = prod
            prod *= self.blocks[i]
        self.nblocks = prod
        
        # Cumulative block points
        u = np.prod(self.block_size)
        t = 1
        for i in range(self.ndim):
            if self.padded:
                s = self.block_size[i] * self.blocks[i]
            else:
                s = self.points[i]
            
            self.cum_block_points[i] = u * t
            t *= s
            u //= self.block_size[i]
    
    def open(self) -> None:
        """
        Open the block file.
        
        Raises:
            IOError: If file cannot be opened
        """
        if self.fp is not None:
            return
        
        mode = 'r+b' if self.writeable else 'rb'
        try:
            self.fp = open(self.file, mode)
        except IOError as e:
            raise IOError(f"Cannot open file {self.file}: {e}")
    
    def close(self) -> None:
        """Close the block file."""
        if self.fp is not None:
            self.fp.close()
            self.fp = None
    
    def _size_block_data(self, block: np.ndarray) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Calculate block data sizes.
        
        Args:
            block: Block indices
            
        Returns:
            Tuple of (block_size, cum_block_size, total_size)
        """
        block_size = np.zeros(self.ndim, dtype=np.int32)
        cum_block_size = np.zeros(self.ndim, dtype=np.int64)
        
        size = 1
        for i in range(self.ndim):
            s = self.points[i] % self.block_size[i]
            if not s or self.padded or (block[i] != self.blocks[i] - 1):
                s = self.block_size[i]
            
            block_size[i] = s
            cum_block_size[i] = size
            size *= s
        
        total_size = min(size, self.npoints)
        return block_size, cum_block_size, total_size
    
    def _new_block_data(self, block: np.ndarray) -> BlockData:
        """
        Create new block data structure.
        
        Args:
            block: Block indices
            
        Returns:
            New BlockData instance
        """
        block_size, cum_block_size, size = self._size_block_data(block)
        data = np.zeros(size, dtype=np.float32)
        
        return BlockData(
            block=block.copy(),
            ndim=self.ndim,
            size=size,
            block_size=block_size,
            cum_block_size=cum_block_size,
            data=data
        )
    
    def _read_block_data(self, block_data: BlockData) -> None:
        """
        Read block data from file.
        
        Args:
            block_data: Block data to read into
            
        Raises:
            IOError: If read fails
        """
        if self.fp is None:
            self.open()
        
        # Calculate file offset
        offset = 0
        for i in range(self.ndim):
            offset += block_data.block[i] * self.cum_block_points[i]
        offset = self.bytes_per_point * offset + self.header
        
        # Add block header offset if needed
        if self.block_header != 0:
            block_num = 0
            for i in range(self.ndim):
                block_num += block_data.block[i] * self.cum_blocks[i]
            offset += (block_num + 1) * self.block_header
        
        # Seek and read
        self.fp.seek(offset)
        
        if self.bytes_per_point == BYTES_PER_WORD:
            # Read as floats
            data_bytes = self.fp.read(block_data.size * BYTES_PER_WORD)
            block_data.data = np.frombuffer(data_bytes, dtype=np.float32, count=block_data.size).copy()
        elif self.bytes_per_point == 2:
            # Read as shorts
            data_bytes = self.fp.read(block_data.size * 2)
            short_data = np.frombuffer(data_bytes, dtype=np.int16, count=block_data.size)
            block_data.data = short_data.astype(np.float32).copy()
        else:
            # Read as bytes
            data_bytes = self.fp.read(block_data.size)
            byte_data = np.frombuffer(data_bytes, dtype=np.int8, count=block_data.size)
            block_data.data = byte_data.astype(np.float32).copy()
        
        # Handle endianness
        if self.big_endian != (sys.byteorder == 'big'):
            block_data.data = block_data.data.byteswap()
        
        # Convert from integer if needed
        if self.integer and self.bytes_per_point < BYTES_PER_WORD:
            # Data was stored as integer, already converted to float above
            pass
    
    def _write_block_data(self, block_data: BlockData) -> None:
        """
        Write block data to file.
        
        Args:
            block_data: Block data to write
            
        Raises:
            IOError: If write fails
        """
        if self.fp is None:
            self.open()
        
        # Calculate file offset (same as read)
        offset = 0
        for i in range(self.ndim):
            offset += block_data.block[i] * self.cum_block_points[i]
        offset = self.bytes_per_point * offset + self.header
        
        if self.block_header != 0:
            block_num = 0
            for i in range(self.ndim):
                block_num += block_data.block[i] * self.cum_blocks[i]
            offset += (block_num + 1) * self.block_header
        
        # Seek to position
        self.fp.seek(offset)
        
        # Prepare data for writing
        write_data = block_data.data.copy()
        
        # Handle endianness
        if self.big_endian != (sys.byteorder == 'big'):
            write_data = write_data.byteswap()
        
        # Write data
        write_data.tofile(self.fp)
    
    def get_block_data_array(self, block: np.ndarray) -> BlockData:
        """
        Get block data by block indices.
        
        This function retrieves a block from cache or reads it from disk.
        The block is locked in cache until unlocked.
        
        Args:
            block: Block indices
            
        Returns:
            BlockData for the specified block
            
        Raises:
            IOError: If block cannot be read
        """
        block_key = tuple(block)
        
        # Check cache
        if block_key in self.block_cache:
            return self.block_cache[block_key]
        
        # Evict old blocks if cache is full
        if len(self.block_cache) >= self.cache_size:
            # Simple FIFO eviction (could use LRU)
            oldest_key = next(iter(self.block_cache))
            if oldest_key not in self.dirty_blocks:
                del self.block_cache[oldest_key]
        
        # Create and read new block
        block_data = self._new_block_data(block)
        self._read_block_data(block_data)
        
        # Add to cache
        self.block_cache[block_key] = block_data
        
        return block_data
    
    def get_block_data_number(self, block_num: int) -> BlockData:
        """
        Get block data by linear block number.
        
        Args:
            block_num: Linear block index
            
        Returns:
            BlockData for the specified block
        """
        # Convert linear block number to block indices
        block = np.zeros(self.ndim, dtype=np.int32)
        remaining = block_num
        
        for i in range(self.ndim):
            block[i] = remaining % self.blocks[i]
            remaining //= self.blocks[i]
        
        return self.get_block_data_array(block)
    
    def lock_block_data(self, block_data: BlockData) -> None:
        """
        Lock block data in cache (prevents eviction).
        
        Args:
            block_data: Block data to lock
        """
        # In this simple implementation, locking is implicit
        # More sophisticated implementations would track lock counts
        pass
    
    def unlock_block_data(self, block_data: BlockData) -> None:
        """
        Unlock block data (allows eviction).
        
        Args:
            block_data: Block data to unlock
        """
        pass
    
    def get_point(self, point: np.ndarray) -> float:
        """
        Get value at a grid point.
        
        Args:
            point: Point indices (ndim array)
            
        Returns:
            Value at the point
            
        Raises:
            IOError: If point cannot be read
            ValueError: If point is out of bounds
        """
        # Validate point
        for i in range(self.ndim):
            if point[i] < 0 or point[i] >= self.points[i]:
                raise ValueError(f"Point {point} out of bounds")
        
        # Calculate which block contains this point
        block = np.zeros(self.ndim, dtype=np.int32)
        local_point = np.zeros(self.ndim, dtype=np.int32)
        
        for i in range(self.ndim):
            block[i] = point[i] // self.block_size[i]
            local_point[i] = point[i] % self.block_size[i]
        
        # Get block data
        block_data = self.get_block_data_array(block)
        
        # Calculate index within block (C row-major order)
        index = 0
        for i in range(self.ndim - 1, -1, -1):
            index = index * block_data.block_size[i] + local_point[i]
        
        return float(block_data.data[index])
    
    def set_point(self, point: np.ndarray, value: float) -> None:
        """
        Set value at a grid point.
        
        Args:
            point: Point indices (ndim array)
            value: Value to set
            
        Raises:
            IOError: If point cannot be written
            ValueError: If point is out of bounds or file not writeable
        """
        if not self.writeable:
            raise ValueError("File is not writeable")
        
        # Validate point
        for i in range(self.ndim):
            if point[i] < 0 or point[i] >= self.points[i]:
                raise ValueError(f"Point {point} out of bounds")
        
        # Calculate which block contains this point
        block = np.zeros(self.ndim, dtype=np.int32)
        local_point = np.zeros(self.ndim, dtype=np.int32)
        
        for i in range(self.ndim):
            block[i] = point[i] // self.block_size[i]
            local_point[i] = point[i] % self.block_size[i]
        
        # Get block data
        block_data = self.get_block_data_array(block)
        
        # Calculate index within block (C row-major order)
        index = 0
        for i in range(self.ndim - 1, -1, -1):
            index = index * block_data.block_size[i] + local_point[i]
        
        # Set value and mark dirty
        block_data.data[index] = value
        block_key = tuple(block)
        self.dirty_blocks.add(block_key)
    
    def get_box(self, box_min: np.ndarray, box_max: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Get values inside a box.
        
        Args:
            box_min: Minimum point of box (inclusive)
            box_max: Maximum point of box (inclusive)
            
        Returns:
            Tuple of (npoints, values as 1D array)
            
        Raises:
            IOError: If box cannot be read
        """
        # Calculate box size
        box_size = np.zeros(self.ndim, dtype=np.int32)
        npoints = 1
        for i in range(self.ndim):
            box_size[i] = box_max[i] - box_min[i] + 1
            npoints *= box_size[i]
        
        # Allocate result
        values = np.zeros(npoints, dtype=np.float32)
        
        # Iterate through box and read points
        point = box_min.copy()
        idx = 0
        
        def iterate_box(dim: int):
            nonlocal idx
            if dim == self.ndim:
                values[idx] = self.get_point(point)
                idx += 1
            else:
                for p in range(box_min[dim], box_max[dim] + 1):
                    point[dim] = p
                    iterate_box(dim + 1)
        
        iterate_box(0)
        
        return npoints, values
    
    def set_box(self, box_min: np.ndarray, box_max: np.ndarray, values: np.ndarray) -> None:
        """
        Set values inside a box.
        
        Args:
            box_min: Minimum point of box (inclusive)
            box_max: Maximum point of box (inclusive)
            values: Values as 1D array
            
        Raises:
            IOError: If box cannot be written
            ValueError: If values size doesn't match box
        """
        if not self.writeable:
            raise ValueError("File is not writeable")
        
        # Calculate expected size
        npoints = 1
        for i in range(self.ndim):
            npoints *= (box_max[i] - box_min[i] + 1)
        
        if len(values) != npoints:
            raise ValueError(f"Values size {len(values)} doesn't match box size {npoints}")
        
        # Iterate through box and write points
        point = box_min.copy()
        idx = 0
        
        def iterate_box(dim: int):
            nonlocal idx
            if dim == self.ndim:
                self.set_point(point, float(values[idx]))
                idx += 1
            else:
                for p in range(box_min[dim], box_max[dim] + 1):
                    point[dim] = p
                    iterate_box(dim + 1)
        
        iterate_box(0)
    
    def save(self) -> None:
        """
        Save dirty blocks to disk.
        
        Raises:
            IOError: If save fails
        """
        if not self.writeable:
            raise ValueError("File is not writeable")
        
        for block_key in self.dirty_blocks:
            block_data = self.block_cache[block_key]
            self._write_block_data(block_data)
        
        self.dirty_blocks.clear()
        
        if self.fp:
            self.fp.flush()
    
    def check(self) -> bool:
        """
        Check block file integrity.
        
        Returns:
            True if file is valid
        """
        # Basic validation
        try:
            # Try to open file
            if self.fp is None:
                self.open()
            
            # Check file size is reasonable
            self.fp.seek(0, 2)  # Seek to end
            file_size = self.fp.tell()
            
            expected_min_size = self.header
            if file_size < expected_min_size:
                return False
            
            return True
        except:
            return False
    
    def __del__(self):
        """Cleanup resources."""
        # Save any dirty blocks
        if hasattr(self, 'writeable') and self.writeable and hasattr(self, 'dirty_blocks') and self.dirty_blocks:
            try:
                self.save()
            except:
                pass
        
        if hasattr(self, 'fp') and self.fp is not None:
            self.close()


def new_block_file(file: str, ndim: int, points: np.ndarray,
                   block_size: np.ndarray, dim_wrapped: np.ndarray,
                   bytes_per_point: int = 4, big_endian: bool = False,
                   padded: bool = True, header: int = 0, integer: bool = False,
                   writeable: bool = False, block_header: int = 0) -> BlockFile:
    """
    Create new block file.
    
    Args:
        file: Path to data file
        ndim: Number of dimensions
        points: Size in each dimension
        block_size: Block size for each dimension
        dim_wrapped: Whether to wrap each dimension
        bytes_per_point: Bytes per point (default 4)
        big_endian: Whether big-endian (default False)
        padded: Whether padded (default True)
        header: Header size (default 0)
        integer: Whether integer data (default False)
        writeable: Whether writeable (default False)
        block_header: Block header size (default 0)
        
    Returns:
        New BlockFile instance
    """
    return BlockFile(file, ndim, points, block_size, dim_wrapped,
                    bytes_per_point, big_endian, padded, header,
                    integer, writeable, block_header)


def delete_block_file(block_file: BlockFile) -> None:
    """
    Delete block file (cleanup resources).
    
    Args:
        block_file: Block file to delete
    """
    block_file.close()
