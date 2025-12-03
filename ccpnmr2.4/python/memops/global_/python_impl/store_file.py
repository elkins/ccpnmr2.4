"""
Contour storage file reader for loading cached contours.

Reads binary contour files created by store_handler and processes polylines
via callback functions.
"""

from typing import List, Tuple, Optional, Callable, Any
import struct
import numpy as np

# Import constants from store_handler
from memops.global_.python_impl.store_handler import (
    STORE_MAGIC, STORE_VERSION, BYTES_PER_WORD, MAX_NDIM
)


class Polyline:
    """
    Simple polyline structure.
    
    Attributes:
        vertices: Nx2 array of (x, y) coordinates
        closed: Whether polyline forms closed loop
        nvertices: Number of vertices
    """
    def __init__(self, vertices: np.ndarray, closed: bool):
        self.vertices = vertices
        self.closed = closed
        self.nvertices = len(vertices)


# Callback function type
# Takes: user_data, block, plane, level (0=neg/1=pos), npolylines, polylines, error_msg
# Returns: success status (True/False)
StorePolyFunc = Callable[[Any, np.ndarray, np.ndarray, int, int, List[Polyline], str], bool]


class StoreFile:
    """
    Contour storage file reader.
    
    Reads binary files created by StoreHandler and processes polylines
    through user-provided callback functions.
    
    Attributes:
        fp: File pointer
        swap: Whether to byte-swap for endianness
        header_size: Size of header in words
        dir_size: Size of directory in words
        directory: Array of file offsets
        ndim: Number of dimensions
        xdim, ydim: Display dimensions
        have_pos, have_neg: Whether positive/negative contours exist
        block_size: Block size in each dimension
        npoints: Number of points in each dimension
        first, last: First and last point indices
        nblocks: Number of blocks in each dimension
        block_min: Minimum block index in each dimension
        cumul_dir: Cumulative directory sizes for indexing
    """
    
    def __init__(self, file_name: str, ndim: int, xdim: int, ydim: int,
                 block_size: np.ndarray):
        """
        Open and initialize contour storage file.
        
        Args:
            file_name: Path to contour storage file
            ndim: Number of dimensions
            xdim, ydim: Display dimension indices
            block_size: Expected block size in each dimension
            
        Raises:
            IOError: If file cannot be opened or read
            ValueError: If file format is invalid or parameters don't match
        """
        try:
            self.fp = open(file_name, 'rb')
        except IOError as e:
            raise IOError(f"could not open '{file_name}' for reading: {e}")
        
        self.ndim = ndim
        self.xdim = xdim
        self.ydim = ydim
        self.block_size = np.array(block_size[:ndim], dtype=np.int32)
        
        # Initialize arrays
        self.npoints = np.zeros(MAX_NDIM, dtype=np.int32)
        self.first = np.zeros(MAX_NDIM, dtype=np.int32)
        self.last = np.zeros(MAX_NDIM, dtype=np.int32)
        self.nblocks = np.zeros(MAX_NDIM, dtype=np.int32)
        self.block_min = np.zeros(MAX_NDIM, dtype=np.int32)
        self.cumul_dir = np.zeros(MAX_NDIM, dtype=np.int32)
        
        self.have_pos = False
        self.have_neg = False
        self.swap = False
        
        # Read and validate header
        self._init_store_file()
        
    def __del__(self):
        """Close file on deletion."""
        if hasattr(self, 'fp') and self.fp:
            self.fp.close()
            
    def close(self):
        """Explicitly close the file."""
        if self.fp:
            self.fp.close()
            self.fp = None
            
    def _read_int(self) -> int:
        """Read integer with optional byte swapping."""
        data = self.fp.read(4)
        if len(data) < 4:
            raise IOError("unexpected end of file")
        fmt = '>i' if self.swap else 'i'
        return struct.unpack(fmt, data)[0]
        
    def _read_float(self) -> float:
        """Read float with optional byte swapping."""
        data = self.fp.read(4)
        if len(data) < 4:
            raise IOError("unexpected end of file")
        fmt = '>f' if self.swap else 'f'
        return struct.unpack(fmt, data)[0]
        
    def _read_int_array(self, n: int) -> np.ndarray:
        """Read array of integers."""
        return np.array([self._read_int() for _ in range(n)], dtype=np.int32)
        
    def _init_store_file(self) -> None:
        """
        Read and validate file header.
        
        Raises:
            IOError: If file cannot be read
            ValueError: If header values don't match expected values
        """
        # Read magic word to detect byte ordering
        magic = self._read_int()
        
        if magic != STORE_MAGIC:
            # Try byte-swapped
            magic_bytes = struct.pack('i', magic)
            magic_swapped = struct.unpack('>i', magic_bytes)[0]
            if magic_swapped != STORE_MAGIC:
                raise ValueError("first word of file is not magic word (normal order or byte swapped)")
            self.swap = True
            magic = magic_swapped
        
        # Read version
        version = self._read_int()
        if version != STORE_VERSION:
            raise ValueError(f"version number: got {version}, expected {STORE_VERSION}")
        
        # Read header size
        self.header_size = self._read_int()
        
        # Read dimensions
        ndim = self._read_int()
        if ndim != self.ndim:
            raise ValueError(f"ndim: got {ndim}, expected {self.ndim}")
        
        xdim = self._read_int()
        if xdim != self.xdim:
            raise ValueError(f"xdim: got {xdim}, expected {self.xdim}")
        
        ydim = self._read_int()
        if ydim != self.ydim:
            raise ValueError(f"ydim: got {ydim}, expected {self.ydim}")
        
        # Read arrays
        self.npoints[:ndim] = self._read_int_array(ndim)
        self.first[:ndim] = self._read_int_array(ndim)
        self.last[:ndim] = self._read_int_array(ndim)
        
        # Read and validate block size
        block_size = self._read_int_array(ndim)
        if not np.array_equal(block_size, self.block_size[:ndim]):
            raise ValueError(f"block_size mismatch: got {block_size}, expected {self.block_size[:ndim]}")
        
        # Read levels to determine pos/neg
        nlevels = self._read_int()
        for i in range(nlevels):
            level = self._read_float()
            if level >= 0:
                self.have_pos = True
            else:
                self.have_neg = True
        
        # Calculate directory parameters
        dir_size = 1
        for i in range(ndim):
            bmin = self.first[i] // self.block_size[i]
            
            if i == self.xdim or i == self.ydim:
                bmax = (self.last[i] - 1) // self.block_size[i]
                p = bmax - bmin + 1
            else:
                p = self.last[i] - self.first[i]
            
            self.cumul_dir[i] = dir_size
            dir_size *= p
            
            self.block_min[i] = bmin
            self.nblocks[i] = 1 + (self.npoints[i] - 1) // self.block_size[i]
        
        if self.have_pos and self.have_neg:
            dir_size *= 2
        
        self.dir_size = dir_size
        
        # Read directory
        self.directory = self._read_int_array(dir_size)
        
    def _get_dir_index(self, block: np.ndarray, plane: np.ndarray) -> int:
        """
        Calculate directory index for given block and plane.
        
        Args:
            block: Block indices
            plane: Plane indices
            
        Returns:
            Directory index
        """
        array = np.zeros(self.ndim, dtype=np.int32)
        
        for i in range(self.ndim):
            if i == self.xdim or i == self.ydim:
                a = block[i]
            else:
                a = self.block_size[i] * block[i] + plane[i]
            array[i] = a
        
        # Calculate linear index
        dir_index = 0
        for i in range(self.ndim):
            dir_index += array[i] * self.cumul_dir[i]
        
        if self.have_pos and self.have_neg:
            dir_index *= 2
        
        return dir_index
        
    def _read_polylines(self, npolylines: int, transposed: bool) -> List[Polyline]:
        """
        Read polylines from file.
        
        Args:
            npolylines: Number of polylines to read
            transposed: Whether to swap x and y coordinates
            
        Returns:
            List of Polyline objects
        """
        polylines = []
        
        for i in range(npolylines):
            # Read vertex count (negative if closed)
            m = self._read_int()
            n = abs(m)
            closed = m < 0
            
            # Read vertices
            vertices = np.zeros((n, 2), dtype=np.float32)
            for j in range(n):
                x = self._read_float()
                y = self._read_float()
                if transposed:
                    vertices[j] = [y, x]
                else:
                    vertices[j] = [x, y]
            
            polylines.append(Polyline(vertices, closed))
        
        return polylines
        
    def _process_contours(self, block: np.ndarray, plane: np.ndarray,
                         dir_index: int, level: int,
                         poly_func: StorePolyFunc, user_data: Any,
                         transposed: bool) -> bool:
        """
        Process contours for a specific directory entry.
        
        Args:
            block: Block indices
            plane: Plane indices
            dir_index: Directory index
            level: Level indicator (0=negative, 1=positive)
            poly_func: Callback function for polylines
            user_data: User data for callback
            transposed: Whether to transpose coordinates
            
        Returns:
            True if successful
        """
        offset = self.directory[dir_index]
        
        if offset >= 0:
            # Seek to data location
            file_offset = (offset + self.header_size + self.dir_size) * BYTES_PER_WORD
            self.fp.seek(file_offset)
            
            # Read number of polylines
            npolylines = self._read_int()
            
            # Read all polylines
            polylines = self._read_polylines(npolylines, transposed)
        else:
            # No data for this block/plane/level
            npolylines = 0
            polylines = []
        
        # Call user callback
        error_msg = ""
        return poly_func(user_data, block, plane, level, npolylines, polylines, error_msg)
        
    def process_contours(self, block: np.ndarray, plane: np.ndarray,
                        poly_func: StorePolyFunc, user_data: Any = None,
                        transposed: bool = False) -> bool:
        """
        Process contours for a given block and plane.
        
        Reads polylines from storage and calls user-provided function for processing.
        Handles both positive and negative contours if present.
        
        Args:
            block: Block indices (file block, not offset by block_min)
            plane: Plane indices (block plane, not offset by first)
            poly_func: Callback function to process polylines
            user_data: Optional user data passed to callback
            transposed: Whether to transpose x/y coordinates
            
        Returns:
            True if successful
        """
        blk = np.zeros(self.ndim, dtype=np.int32)
        pln = np.zeros(self.ndim, dtype=np.int32)
        
        # Adjust block relative to block_min
        for i in range(self.ndim):
            blk[i] = block[i] - self.block_min[i]
            
            # Adjust plane for non-display dimensions
            if i != self.xdim and i != self.ydim:
                p = block[i] * self.block_size[i]
                p = self.first[i] - p
                p = max(0, p)
                pln[i] = plane[i] - p
            else:
                pln[i] = 0
        
        # Process negative contours (or positive if no negative)
        dir_index = self._get_dir_index(blk, pln)
        if not self._process_contours(block, plane, dir_index, 0,
                                     poly_func, user_data, transposed):
            return False
        
        # Process positive contours if both exist
        if self.have_pos and self.have_neg:
            dir_index += 1
            if not self._process_contours(block, plane, dir_index, 1,
                                         poly_func, user_data, transposed):
                return False
        
        return True


def new_store_file(file_name: str, ndim: int, xdim: int, ydim: int,
                  block_size: np.ndarray) -> StoreFile:
    """
    Open contour storage file for reading.
    
    Args:
        file_name: Path to storage file
        ndim: Number of dimensions
        xdim, ydim: Display dimension indices
        block_size: Expected block size
        
    Returns:
        StoreFile instance
        
    Raises:
        IOError: If file cannot be opened
        ValueError: If file format is invalid
    """
    return StoreFile(file_name, ndim, xdim, ydim, block_size)


def delete_store_file(store_file: StoreFile) -> None:
    """
    Close and delete store file.
    
    Args:
        store_file: File to close
    """
    store_file.close()
