"""
Slice file drawing for spectral data visualization.

This module handles drawing 1D slices through multi-dimensional NMR spectral data
with interpolation and customizable rendering. It's used for displaying cross-sections
of 2D/3D spectra.

Key features:
- Interpolated slicing at arbitrary positions
- Horizontal and vertical slice orientations
- Component-wise extraction for complex data
- Integration with block_file for data access
- Drawing callback interface for rendering flexibility

Original C: ccpnmr2.4/c/ccpnmr/analysis/slice_file.c (265 lines)
Python implementation: Simplified with NumPy
"""

import numpy as np
from typing import Callable, Optional, Any, List, Tuple, Protocol
from dataclasses import dataclass

# Import block_file module (assuming it's available)
try:
    from memops.global_.python_impl.block_file import BlockFile
except ImportError:
    BlockFile = Any  # Fallback for type hints

MAX_NDIM = 10


class DrawingFuncs(Protocol):
    """Protocol for drawing callback functions."""
    
    def draw_line(self, data: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        """Draw a line from (x0, y0) to (x1, y1)."""
        ...


@dataclass
class SliceFile:
    """
    Slice file for drawing 1D slices through multi-dimensional spectral data.
    
    A slice file represents a 1D cross-section through a multi-dimensional
    spectrum, with specified orientation (horizontal/vertical) and dimension.
    """
    orient: int  # Orientation: 1 = horizontal, 0 = vertical
    dim: int  # Dimension along which to slice
    block_file: BlockFile  # Block file containing spectral data
    mem_cache: Optional[Any] = None  # Memory cache (currently unused in Python)
    
    def __post_init__(self):
        """Validate parameters."""
        ndim = self.block_file.ndim
        if self.dim < 0 or self.dim >= ndim:
            raise ValueError(f"dim {self.dim} out of range [0, {ndim})")
    
    def draw_slice(self,
                   first: int,
                   last: int,
                   position: np.ndarray,
                   drawing_funcs: DrawingFuncs,
                   data: Any) -> None:
        """
        Draw a single slice with interpolation at specified position.
        
        This function draws a 1D slice through the multi-dimensional data,
        interpolating at the specified position in the non-slice dimensions.
        
        Args:
            first: First point along slice dimension to draw
            last: Last point along slice dimension to draw (exclusive)
            position: Position in each non-slice dimension (length ndim)
            drawing_funcs: Drawing callback interface
            data: User data passed to drawing callbacks
        
        Raises:
            ValueError: If parameters are out of range
        """
        block_file = self.block_file
        ndim = block_file.ndim
        dim = self.dim
        points = block_file.points
        
        # Validate parameters
        if first < 0:
            raise ValueError(f"first = {first} < 0")
        
        if last > points[dim]:
            raise ValueError(f"last = {last} > points[{dim}] = {points[dim]}")
        
        if first >= last:
            raise ValueError(f"first = {first} >= last = {last}")
        
        for i in range(ndim):
            if i == dim:
                continue
            
            if position[i] < 0:
                raise ValueError(f"dim {i+1}: position = {position[i]:.3f} < 0")
            
            if position[i] >= points[i]:
                raise ValueError(
                    f"dim {i+1}: position = {position[i]:.3f} >= points = {points[i]}"
                )
        
        # Compute interpolation structure
        cumul = np.zeros(ndim, dtype=np.int32)
        total = 1
        
        for i in range(ndim):
            if i == dim or position[i] >= points[i] - 1:
                m = 1
            else:
                m = 2
            
            cumul[i] = total
            total *= m
        
        # Draw the slice
        a0, b0 = 0.0, 0.0
        
        for p in range(first, last):
            point = np.zeros(ndim, dtype=np.int32)
            point[dim] = p
            
            # Interpolate value at this slice position
            value = 0.0
            
            for t in range(total):
                weight = 1.0
                
                # Convert linear index to multi-dimensional array indices
                array = np.zeros(ndim, dtype=np.int32)
                temp = t
                for i in range(ndim):
                    if cumul[i] > 0:
                        array[i] = temp // cumul[i]
                        temp = temp % cumul[i]
                
                # Compute interpolation weights and point coordinates
                for i in range(ndim):
                    if i == dim:
                        continue
                    
                    point[i] = int(np.floor(position[i]))
                    
                    if array[i]:
                        point[i] += 1
                        weight *= position[i] - np.floor(position[i])
                    else:
                        weight *= 1.0 - (position[i] - np.floor(position[i]))
                
                # Get data value
                v = block_file.get_point(point)
                value += weight * v
            
            # Draw line segment
            a1 = float(p)
            b1 = value
            
            if p > first:
                if self.orient:  # Horizontal
                    drawing_funcs.draw_line(data, a0, b0, a1, b1)
                else:  # Vertical
                    drawing_funcs.draw_line(data, b0, a0, b1, a1)
            
            a0 = a1
            b0 = b1
    
    def draw_all_slices(self,
                        first: np.ndarray,
                        last: np.ndarray,
                        ncomponents: int,
                        components: np.ndarray,
                        drawing_funcs: DrawingFuncs,
                        data: Any) -> None:
        """
        Draw all slices in specified region with component extraction.
        
        This function draws multiple parallel slices covering a rectangular
        region in the non-slice dimensions, extracting specific components
        (e.g., real/imaginary parts of complex data).
        
        Args:
            first: First point in each dimension (length ndim)
            last: Last point in each dimension (exclusive, length ndim)
            ncomponents: Number of components to extract
            components: Component indices to extract
            drawing_funcs: Drawing callback interface
            data: User data passed to drawing callbacks
        
        Raises:
            ValueError: If parameters are out of range
        """
        block_file = self.block_file
        ndim = block_file.ndim
        dim = self.dim
        points = block_file.points
        
        # Validate parameters
        for i in range(ndim):
            if first[i] < 0:
                raise ValueError(f"dim {i+1}: first = {first[i]} < 0")
            
            if last[i] > points[i]:
                raise ValueError(
                    f"dim {i+1}: last = {last[i]} > points = {points[i]}"
                )
            
            if first[i] >= last[i]:
                raise ValueError(
                    f"dim {i+1}: first = {first[i]} >= last = {last[i]}"
                )
        
        # Compute iteration structure
        cumul = np.zeros(ndim, dtype=np.int32)
        total = 1
        
        for i in range(ndim):
            if i == dim:
                m = 1
            else:
                m = last[i] - first[i]
            
            cumul[i] = total
            total *= m
        
        # Draw all slices
        for t in range(total):
            # Convert linear index to multi-dimensional point
            point = np.zeros(ndim, dtype=np.int32)
            temp = t
            
            for i in range(ndim):
                if cumul[i] > 0:
                    point[i] = (temp // cumul[i]) + first[i]
                    temp = temp % cumul[i]
            
            # Draw this slice
            a0, b0 = 0.0, 0.0
            
            for p in range(first[dim], last[dim]):
                point[dim] = p
                
                # Get component-extracted value
                v = self._get_components_point(point, ncomponents, components)
                
                a1 = float(p)
                b1 = v
                
                if p > first[dim]:
                    if self.orient:  # Horizontal
                        drawing_funcs.draw_line(data, a0, b0, a1, b1)
                    else:  # Vertical
                        drawing_funcs.draw_line(data, b0, a0, b1, a1)
                
                a0 = a1
                b0 = b1
    
    def _get_components_point(self,
                              point: np.ndarray,
                              ncomponents: int,
                              components: np.ndarray) -> float:
        """
        Get value at point with component extraction.
        
        For complex data, this extracts specific components (real, imaginary, etc.)
        and combines them according to the component specification.
        
        Args:
            point: Point coordinates
            ncomponents: Number of components
            components: Component indices
        
        Returns:
            Combined component value
        """
        # Get the data value
        v = self.block_file.get_point(point)
        
        # For now, just return the value
        # In a full implementation, this would handle complex data components
        # (real, imaginary, magnitude, phase) based on components array
        return v


# Factory functions for C API compatibility

def new_slice_file(orient: int,
                   dim: int,
                   block_file: BlockFile,
                   mem_cache: Optional[Any] = None) -> SliceFile:
    """
    Create a new slice file.
    
    Args:
        orient: Orientation (1 = horizontal, 0 = vertical)
        dim: Dimension along which to slice
        block_file: Block file containing spectral data
        mem_cache: Optional memory cache
    
    Returns:
        New SliceFile instance
    
    Raises:
        ValueError: If dim is out of range
    """
    return SliceFile(orient, dim, block_file, mem_cache)


def delete_slice_file(slice_file: SliceFile) -> None:
    """
    Delete a slice file.
    
    In Python, this is a no-op as garbage collection handles cleanup.
    
    Args:
        slice_file: Slice file to delete
    """
    pass


def draw_slice_file(slice_file: SliceFile,
                    first: int,
                    last: int,
                    position: np.ndarray,
                    drawing_funcs: DrawingFuncs,
                    data: Any) -> None:
    """
    Draw a slice (C API wrapper).
    
    Args:
        slice_file: Slice file instance
        first: First point along slice dimension
        last: Last point along slice dimension (exclusive)
        position: Position in non-slice dimensions
        drawing_funcs: Drawing callback interface
        data: User data for callbacks
    """
    slice_file.draw_slice(first, last, position, drawing_funcs, data)


def draw_all_slice_file(slice_file: SliceFile,
                        first: np.ndarray,
                        last: np.ndarray,
                        ncomponents: int,
                        components: np.ndarray,
                        drawing_funcs: DrawingFuncs,
                        data: Any) -> None:
    """
    Draw all slices in region (C API wrapper).
    
    Args:
        slice_file: Slice file instance
        first: First point in each dimension
        last: Last point in each dimension (exclusive)
        ncomponents: Number of components
        components: Component indices
        drawing_funcs: Drawing callback interface
        data: User data for callbacks
    """
    slice_file.draw_all_slices(first, last, ncomponents, components, drawing_funcs, data)
