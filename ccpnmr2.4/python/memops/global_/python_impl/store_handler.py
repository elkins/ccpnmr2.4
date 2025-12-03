"""
Contour storage handler for disk-based contour caching.

Saves/loads contour polylines in binary format with header and directory structure.
Used for caching computed contours to avoid recomputation.
"""

from typing import List, Tuple, Optional, BinaryIO
import struct
import numpy as np

# Constants from store_consts.h
STORE_MAGIC = 0x5354524F  # 'STRO' in hex
STORE_VERSION = 1
STORE_DRAWING = 3  # Drawing function type identifier

# Header components (in 4-byte words)
HEADER0 = 7  # magic, version, header_size, ndim, xdim, ydim, nlevels
HEADER1 = 4  # per dimension: npoints, first, last, block_size
HEADER2 = 1  # per level: level value (as float = 1 word)

BYTES_PER_WORD = 4
MAX_NDIM = 10


class StoreHandler:
    """
    Contour storage handler for saving contours to binary files.
    
    Format:
    - Header: metadata (ndim, dimensions, blocks, levels)
    - Directory: file offsets for each block/plane/level
    - Data: polylines as coordinate sequences
    
    Attributes:
        fp: File pointer
        swap: Whether to byte-swap for endianness
        header_size: Size of header in words
        dir_size: Size of directory in words
        directory: Array of file offsets
        ndim: Number of dimensions
        xdim, ydim: Display dimensions
        have_pos, have_neg: Whether positive/negative contours exist
        block_size: Size of blocks in each dimension
        cumul_dir: Cumulative directory sizes for indexing
        block, plane: Current block and plane indices
        offset: Current data offset
        is_pos: Current level is positive
        npos_polys, nneg_polys: Polyline counts
    """
    
    def __init__(self, file_name: str, swap: bool = False):
        """
        Create contour storage handler.
        
        Args:
            file_name: Output file path
            swap: Whether to byte-swap for different endianness
            
        Raises:
            IOError: If file cannot be opened
        """
        try:
            self.fp = open(file_name, 'wb')
        except IOError as e:
            raise IOError(f"could not open '{file_name}' for writing: {e}")
            
        self.swap = swap
        self.directory: Optional[np.ndarray] = None
        
        # Initialized by init_store_save
        self.header_size = 0
        self.dir_size = 0
        self.ndim = 0
        self.xdim = 0
        self.ydim = 0
        self.have_pos = False
        self.have_neg = False
        self.block_size = np.zeros(MAX_NDIM, dtype=np.int32)
        self.cumul_dir = np.zeros(MAX_NDIM, dtype=np.int32)
        
        # Working storage
        self.block = np.zeros(MAX_NDIM, dtype=np.int32)
        self.plane = np.zeros(MAX_NDIM, dtype=np.int32)
        self.first_plane = np.zeros(MAX_NDIM, dtype=np.int32)
        self.offset = 0
        self.is_pos = False
        self.npos_polys = 0
        self.nneg_polys = 0
        
    def __del__(self):
        """Close file on deletion."""
        if hasattr(self, 'fp') and self.fp:
            self.fp.close()
            
    def close(self):
        """Explicitly close the file."""
        if self.fp:
            self.fp.close()
            self.fp = None
            
    def _get_dir_index(self) -> int:
        """
        Calculate directory index for current block/plane/level.
        
        Directory is multi-dimensional array indexed by:
        - Block indices for display dimensions (xdim, ydim)
        - Plane indices for other dimensions
        - Level sign (if both pos and neg contours)
        
        Returns:
            Directory index
        """
        array = np.zeros(self.ndim, dtype=np.int32)
        
        for i in range(self.ndim):
            if i == self.xdim or i == self.ydim:
                # Display dimensions use block index
                a = self.block[i]
            elif self.block[i] == 0:
                # First block in non-display dim uses plane index
                a = self.plane[i]
            else:
                # Other blocks: offset from first plane
                a = (self.block_size[i] * self.block[i] + 
                     self.plane[i] - self.first_plane[i])
            array[i] = a
        
        # Calculate linear index from multi-dimensional indices
        dir_index = 0
        for i in range(self.ndim):
            dir_index += array[i] * self.cumul_dir[i]
        
        # If both positive and negative contours, directory is doubled
        # Negative contours come first
        if self.have_pos and self.have_neg:
            dir_index *= 2
            if self.is_pos:
                dir_index += 1
                
        return dir_index
        
    def _write_int(self, value: int) -> None:
        """Write integer with optional byte swapping."""
        data = struct.pack('i' if not self.swap else '>i', value)
        self.fp.write(data)
        
    def _write_float(self, value: float) -> None:
        """Write float with optional byte swapping."""
        data = struct.pack('f' if not self.swap else '>f', value)
        self.fp.write(data)
        
    def _write_int_array(self, arr: np.ndarray) -> None:
        """Write integer array with optional byte swapping."""
        for val in arr:
            self._write_int(int(val))
            
    def init_store_save(self, ndim: int, xdim: int, ydim: int,
                       npoints: np.ndarray, first: np.ndarray, last: np.ndarray,
                       block_size: np.ndarray, nblocks: np.ndarray,
                       nlevels: int, levels: np.ndarray) -> None:
        """
        Initialize storage and write header.
        
        Args:
            ndim: Number of dimensions
            xdim, ydim: Display dimension indices
            npoints: Number of points in each dimension
            first, last: First and last points to store
            block_size: Block size in each dimension
            nblocks: Number of blocks in each dimension
            nlevels: Number of contour levels
            levels: Contour level values
            
        Raises:
            ValueError: If parameters are inconsistent
        """
        # Calculate header size
        header_size = HEADER0 + ndim * HEADER1 + HEADER2 * nlevels
        
        # Build header
        header = []
        header.append(STORE_MAGIC)
        header.append(STORE_VERSION)
        header.append(header_size)
        header.append(ndim)
        header.append(xdim)
        header.append(ydim)
        
        header.extend(npoints[:ndim])
        header.extend(first[:ndim])
        header.extend(last[:ndim])
        header.extend(block_size[:ndim])
        
        header.append(nlevels)
        
        # Header without levels (integers only)
        if len(header) != HEADER0 + ndim * HEADER1:
            raise ValueError(f"inconsistent header int count: {len(header)} vs {HEADER0 + ndim * HEADER1}")
        
        # Verify total header size including levels
        if len(header) + nlevels != header_size:
            raise ValueError(f"inconsistent header size: {len(header) + nlevels} vs {header_size}")
        
        # Determine if we have positive and/or negative contours
        have_pos = np.any(levels >= 0)
        have_neg = np.any(levels < 0)
        
        # Calculate directory size
        dir_size = 1
        cumul_dir = np.zeros(ndim, dtype=np.int32)
        
        for i in range(ndim):
            if i == xdim or i == ydim:
                p = nblocks[i]
            else:
                p = last[i] - first[i]
            
            cumul_dir[i] = dir_size
            dir_size *= p
        
        if have_pos and have_neg:
            dir_size *= 2
        
        # Initialize directory (all -1 means no data)
        directory = np.full(dir_size, -1, dtype=np.int32)
        
        # Write header integers
        for val in header:
            self._write_int(int(val))
        
        # Write levels as part of header
        for val in levels:
            self._write_float(float(val))
        
        # Write directory (will be updated at end)
        self._write_int_array(directory)
        
        # Store state
        self.ndim = ndim
        self.xdim = xdim
        self.ydim = ydim
        self.header_size = header_size
        self.dir_size = dir_size
        self.directory = directory
        self.cumul_dir = cumul_dir
        self.block_size[:ndim] = block_size[:ndim]
        self.first_plane[:ndim] = first[:ndim]
        self.have_pos = have_pos
        self.have_neg = have_neg
        self.offset = 0
        
    def init_store_block(self, block: np.ndarray) -> None:
        """
        Set current block indices.
        
        Args:
            block: Block indices (relative to block_min)
        """
        self.block[:self.ndim] = block[:self.ndim]
        
    def init_store_plane(self, plane: np.ndarray) -> None:
        """
        Set current plane indices and reset polyline counts.
        
        Args:
            plane: Plane indices within current block
        """
        self.plane[:self.ndim] = plane[:self.ndim]
        self.npos_polys = 0
        self.nneg_polys = 0
        
    def init_store_level(self, level: float) -> None:
        """
        Set whether current level is positive or negative.
        
        Args:
            level: Contour level value
        """
        self.is_pos = level >= 0
        
    def draw_polyline(self, vertices: np.ndarray, closed: bool = False) -> None:
        """
        Write polyline to storage.
        
        Args:
            vertices: Nx2 array of (x, y) coordinates
            closed: Whether polyline forms closed loop
        """
        n = len(vertices)
        dir_index = self._get_dir_index()
        
        # If first polyline for this block/plane/level, write placeholder for count
        if self.directory[dir_index] == -1:
            self.directory[dir_index] = self.offset
            self._write_int(0)  # Placeholder for polyline count
            self.offset += 1
        
        # Write vertex count (negative if closed)
        m = -n if closed else n
        self._write_int(m)
        
        # Write coordinates
        for i in range(n):
            self._write_float(float(vertices[i, 0]))
            self._write_float(float(vertices[i, 1]))
        
        self.offset += 1 + 2 * n
        
        if self.is_pos:
            self.npos_polys += 1
        else:
            self.nneg_polys += 1
            
    def end_store_plane(self) -> None:
        """
        Finalize current plane by updating polyline counts.
        
        Seeks back to update the placeholder polyline count written at start.
        """
        # Update negative polyline count
        if self.nneg_polys > 0:
            self.is_pos = False
            dir_index = self._get_dir_index()
            offset = self.directory[dir_index]
            file_offset = (self.header_size + self.dir_size + offset) * BYTES_PER_WORD
            self.fp.seek(file_offset)
            self._write_int(self.nneg_polys)
        
        # Update positive polyline count
        if self.npos_polys > 0:
            self.is_pos = True
            dir_index = self._get_dir_index()
            offset = self.directory[dir_index]
            file_offset = (self.header_size + self.dir_size + offset) * BYTES_PER_WORD
            self.fp.seek(file_offset)
            self._write_int(self.npos_polys)
        
        # Seek to end for next data
        if self.npos_polys > 0 or self.nneg_polys > 0:
            file_offset = (self.header_size + self.dir_size + self.offset) * BYTES_PER_WORD
            self.fp.seek(file_offset)
            
    def end_store_save(self) -> None:
        """
        Finalize storage by writing updated directory.
        
        Seeks back to directory location and writes all offsets.
        """
        # Seek to directory location (after header)
        file_offset = self.header_size * BYTES_PER_WORD
        self.fp.seek(file_offset)
        
        # Write updated directory
        self._write_int_array(self.directory)
        
        # Close file
        self.close()


def new_store_handler(file_name: str, swap: bool = False) -> StoreHandler:
    """
    Create new contour storage handler.
    
    Args:
        file_name: Output file path
        swap: Whether to byte-swap for different endianness
        
    Returns:
        Store handler instance
        
    Raises:
        IOError: If file cannot be opened
    """
    return StoreHandler(file_name, swap)


def delete_store_handler(store_handler: StoreHandler) -> None:
    """
    Delete store handler and close file.
    
    Args:
        store_handler: Handler to delete
    """
    store_handler.close()


# Drawing functions implementation (mostly stubs for storage)
def store_drawing_funcs():
    """
    Return drawing functions dict for storage backend.
    
    Most functions are no-ops since we only care about polylines.
    """
    return {
        'type': STORE_DRAWING,
        'start_draw': lambda data: None,
        'end_draw': lambda data: None,
        'new_draw_range': lambda data, x0, y0, x1, y1, clip: None,
        'draw_line': lambda data, x0, y0, x1, y1: None,
        'draw_clipped_line': lambda data, x0, y0, x1, y1: None,
        'draw_polyline': lambda data, vertices, closed: data.draw_polyline(vertices, closed),
        'draw_clipped_polyline': lambda data, vertices, closed: data.draw_polyline(vertices, closed),
        'draw_text': lambda data, text, x, y, a, b: None,
        'set_draw_color': lambda data, color: None,
        'set_draw_font': lambda data, name, size: None,
        'set_line_style': lambda data, style: None,
        'set_line_width': lambda data, width: None,
        'fill_circle': lambda data, x, y, r: None,
        'draw_circle': lambda data, x, y, r: None,
        'get_background': lambda data: None,
        'get_region': lambda data: None,
    }
