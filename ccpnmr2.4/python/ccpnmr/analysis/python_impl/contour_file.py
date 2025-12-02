"""
Contour File - Contour data caching and rendering for NMR spectra

This module provides efficient contour caching and rendering for 2D slices
of multi-dimensional NMR spectra. It uses a hash table to cache contour data
blocks and a memory cache to manage memory usage.

Python implementation of ccpnmr/analysis/contour_file.c

Original C implementation: Wayne Boucher and Tim Stevens (University of Cambridge)
Python conversion: 2024
"""

import numpy as np
from typing import Optional, Tuple, Dict, Callable, Any
from .contour_levels import ContourLevels


class ContourFile:
    """Contour file for caching and rendering NMR spectrum contours
    
    Manages cached contour data for efficient rendering of 2D slices from
    multi-dimensional spectra. Uses hash table for block lookup and memory
    cache for automatic management.
    
    Attributes:
        xdim: X dimension index
        ydim: Y dimension index
        block_file: Optional block file data source
        store_file: Optional stored contour data source
        contour_levels: Current contour levels
        ncomponents: Number of shape file components (if applicable)
        components: Shape file component indices
        contour_table: Hash table mapping blocks to contour data
        mem_cache: Memory cache for contour data management
        transposed: Whether stored data is transposed
        clearing: Flag to prevent recursion during clearing
    """
    
    def __init__(self, xdim: int, ydim: int, 
                 block_file=None,  # Would be BlockFile type
                 store_file=None,  # Would be StoreFile type
                 mem_cache=None,   # Would be MemCache type
                 transposed: bool = False):
        """Create a contour file
        
        Args:
            xdim: X dimension index (horizontal)
            ydim: Y dimension index (vertical)
            block_file: Optional block file data source
            store_file: Optional stored contour data source
            mem_cache: Memory cache for managing contour data
            transposed: Whether stored data is transposed
            
        Raises:
            ValueError: If both or neither data sources specified, or invalid dimensions
        """
        # Validate inputs
        if block_file and store_file:
            raise ValueError("both block_file and store_file are set")
        
        if not block_file and not store_file:
            raise ValueError("neither block_file nor store_file is set")
        
        # Get dimensionality
        if block_file:
            ndim = block_file.ndim
        else:
            ndim = store_file.ndim
        
        # Validate dimensions
        if xdim < 0 or xdim >= ndim:
            raise ValueError(f"xdim = {xdim}, should be >= 0 and < {ndim}")
        
        if ydim < 0 or ydim >= ndim:
            raise ValueError(f"ydim = {ydim}, should be >= 0 and < {ndim}")
        
        if xdim == ydim:
            raise ValueError(f"xdim = ydim = {xdim}")
        
        # Initialize attributes
        self.xdim = xdim
        self.ydim = ydim
        self.block_file = block_file
        self.store_file = store_file
        self.mem_cache = mem_cache
        self.transposed = transposed
        self.contour_levels: Optional[ContourLevels] = None
        self.ncomponents = 0
        self.components: Optional[np.ndarray] = None
        self.clearing = False
        
        # Create contour cache (hash table)
        # Keys are block coordinates, values are ContourData objects
        self.contour_table: Dict[Tuple[int, ...], Any] = {}
    
    def __del__(self):
        """Delete contour file and cached data"""
        self.clear_cache()
    
    def clear_cache(self):
        """Clear all cached contour data"""
        self.clearing = True
        self.contour_table.clear()
        self.clearing = False
    
    def _equal_components(self, ncomponents: int, 
                         components: Optional[np.ndarray]) -> bool:
        """Check if components match current settings
        
        Args:
            ncomponents: Number of components
            components: Component indices array
            
        Returns:
            True if components match
        """
        # Both None or empty
        if self.components is None and (components is None or ncomponents == 0):
            return True
        
        # One is None/empty, other is not
        if self.components is None and components is not None and ncomponents > 0:
            return False
        if self.components is not None and (components is None or ncomponents == 0):
            return self.ncomponents == 0
        
        # Both have components
        if self.ncomponents != ncomponents:
            return False
        
        return np.array_equal(self.components, components[:ncomponents])
    
    def _set_components(self, ncomponents: int, 
                       components: Optional[np.ndarray]):
        """Set or update components
        
        Args:
            ncomponents: Number of components
            components: Component indices array
        """
        self.components = None
        self.ncomponents = 0
        
        if components is not None and ncomponents > 0:
            self.components = np.array(components[:ncomponents], dtype=np.int32).copy()
            self.ncomponents = ncomponents
    
    def _get_contour_data(self, block: Tuple[int, ...]):
        """Get or create contour data for a block
        
        Args:
            block: Block coordinate tuple
            
        Returns:
            ContourData object for the block
        """
        # Check cache
        if block in self.contour_table:
            return self.contour_table[block]
        
        # Create new contour data
        # In full implementation, this would call new_contour_data()
        # and calculate actual contours using marching squares
        contour_data = self._create_contour_data(block)
        
        # Cache it
        self.contour_table[block] = contour_data
        
        return contour_data
    
    def _create_contour_data(self, block: Tuple[int, ...]):
        """Create contour data for a block
        
        This is a placeholder for the actual contour generation
        which would use the marching squares algorithm.
        
        Args:
            block: Block coordinate tuple
            
        Returns:
            Mock ContourData object
        """
        # In full implementation, this would:
        # 1. Load data from block_file or store_file
        # 2. Run marching squares algorithm for each contour level
        # 3. Store resulting polylines
        
        class ContourData:
            def __init__(self):
                self.block = block
                self.npolylines = []
                self.polylines = []
        
        return ContourData()
    
    def region_contour_file(self, first: np.ndarray, last: np.ndarray,
                           abort_func: Optional[Callable[[], bool]] = None,
                           contour_levels: Optional[ContourLevels] = None,
                           contour_style=None,  # Would be ContourStyle type
                           ncomponents: int = 0,
                           components: Optional[np.ndarray] = None,
                           drawing_funcs=None,  # Would be DrawingFuncs type
                           data: Any = None) -> bool:
        """Draw contours in a specified region
        
        This is the main rendering function. It divides the region into blocks,
        retrieves or generates contour data for each block, and draws the contours.
        
        Args:
            first: Starting indices for region (inclusive)
            last: Ending indices for region (exclusive)
            abort_func: Optional function to check for abort signal
            contour_levels: Contour levels to draw
            contour_style: Drawing style parameters
            ncomponents: Number of shape file components
            components: Shape file component indices
            drawing_funcs: Drawing function callbacks
            data: User data passed to drawing functions
            
        Returns:
            True on success
            
        Raises:
            ValueError: If region parameters are invalid
        """
        if abort_func is None:
            abort_func = lambda: False
        
        # Get dimensions and block size
        if self.block_file:
            ndim = self.block_file.ndim
            points = self.block_file.points
            block_size = self.block_file.block_size
        else:
            ndim = self.store_file.ndim
            points = self.store_file.npoints
            block_size = self.store_file.block_size
        
        # Validate region
        for i in range(ndim):
            if first[i] < 0:
                raise ValueError(f"dim {i+1}: region min = {first[i]} < 0")
            
            if last[i] > points[i]:
                raise ValueError(f"dim {i+1}: region max = {last[i]} > points = {points[i]}")
            
            if first[i] >= last[i]:
                raise ValueError(f"dim {i+1}: region min = {first[i]} >= max = {last[i]}")
        
        # Handle store file region clipping
        if self.store_file:
            for i in range(ndim):
                if first[i] >= self.store_file.last[i]:
                    return True  # Nothing to draw
                if last[i] <= self.store_file.first[i]:
                    return True  # Nothing to draw
                
                first[i] = max(first[i], self.store_file.first[i])
                last[i] = min(last[i], self.store_file.last[i])
        
        # Update contour levels if changed (block_file only)
        if self.block_file:
            if self.contour_levels is None or self.contour_levels != contour_levels:
                self.clear_cache()
                self.contour_levels = contour_levels.copy() if contour_levels else None
            
            # Update components if changed
            if not self._equal_components(ncomponents, components):
                self.clear_cache()
                self._set_components(ncomponents, components)
        else:
            # Store file: set up default levels if needed
            if self.contour_levels is None:
                if self.store_file.have_neg and self.store_file.have_pos:
                    levels = np.array([-1.0, 1.0])
                elif self.store_file.have_neg:
                    levels = np.array([-1.0])
                else:
                    levels = np.array([1.0])
                
                self.contour_levels = ContourLevels(levels)
        
        # Calculate block range
        block_min = first // block_size
        block_max = (last - 1) // block_size
        nblocks = block_max - block_min + 1
        
        # Iterate through blocks
        total_blocks = np.prod(nblocks)
        
        for b in range(total_blocks):
            if abort_func():
                break
            
            # Convert linear index to block coordinates
            block = self._index_to_array(b, nblocks) + block_min
            block_tuple = tuple(block)
            
            # Get contour data for this block
            contour_data = self._get_contour_data(block_tuple)
            
            # Draw contours from this block
            if drawing_funcs and contour_data:
                self._draw_block_contours(contour_data, contour_style, 
                                         drawing_funcs, data)
        
        return True
    
    def _index_to_array(self, index: int, shape: np.ndarray) -> np.ndarray:
        """Convert linear index to multi-dimensional array indices
        
        Args:
            index: Linear index
            shape: Array shape
            
        Returns:
            Array of indices
        """
        result = np.zeros(len(shape), dtype=np.int32)
        remaining = index
        
        for i in range(len(shape) - 1, -1, -1):
            cum_prod = np.prod(shape[:i]) if i > 0 else 1
            result[i] = remaining // cum_prod
            remaining %= cum_prod
        
        return result
    
    def _draw_block_contours(self, contour_data, contour_style, 
                            drawing_funcs, data):
        """Draw contours from a block of data
        
        This is a placeholder for the actual drawing logic which would
        iterate through planes and levels, calling drawing callbacks.
        
        Args:
            contour_data: ContourData object
            contour_style: Drawing style parameters
            drawing_funcs: Drawing function callbacks
            data: User data
        """
        # In full implementation, this would:
        # 1. Iterate through planes in the block
        # 2. For each plane, iterate through contour levels
        # 3. Call drawing_funcs to render polylines
        # 4. Handle color/style based on positive/negative levels
        pass


# C API compatibility functions

def new_contour_file(xdim: int, ydim: int,
                    block_file=None, store_file=None,
                    mem_cache=None, transposed: bool = False) -> ContourFile:
    """Create a new contour file
    
    Args:
        xdim: X dimension index
        ydim: Y dimension index
        block_file: Optional block file data source
        store_file: Optional stored contour data source
        mem_cache: Memory cache
        transposed: Whether data is transposed
        
    Returns:
        ContourFile object
    """
    return ContourFile(xdim, ydim, block_file, store_file, mem_cache, transposed)


def delete_contour_file(contour_file: ContourFile):
    """Delete a contour file
    
    Args:
        contour_file: ContourFile to delete
    """
    del contour_file


def region_contour_file(contour_file: ContourFile, 
                       first: np.ndarray, last: np.ndarray,
                       abort_func: Optional[Callable[[], bool]] = None,
                       contour_levels: Optional[ContourLevels] = None,
                       contour_style=None,
                       ncomponents: int = 0,
                       components: Optional[np.ndarray] = None,
                       drawing_funcs=None,
                       data: Any = None) -> bool:
    """Draw contours in a region
    
    Args:
        contour_file: ContourFile object
        first: Starting indices
        last: Ending indices
        abort_func: Abort check function
        contour_levels: Contour levels
        contour_style: Drawing style
        ncomponents: Number of components
        components: Component indices
        drawing_funcs: Drawing callbacks
        data: User data
        
    Returns:
        True on success
    """
    return contour_file.region_contour_file(
        first, last, abort_func, contour_levels, contour_style,
        ncomponents, components, drawing_funcs, data
    )
