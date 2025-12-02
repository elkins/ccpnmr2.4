"""
Peak Cluster Management

Python implementation of peak_cluster.c for grouping related NMR peaks.

A peak cluster represents a collection of related peaks that share some relationship:
- MULTIPLET: Peaks that are part of a multiplet splitting pattern
- SHIFT: Peaks that represent the same resonance at different chemical shifts
- STATIC: User-defined static grouping
- SYMMETRY: Peaks related by molecular symmetry

This module provides:
- PeakCluster class for managing collections of related peaks
- Addition/removal of peaks with dimension validation
- Text labels for the cluster and each dimension
- Bounding box calculation for visualization
- Drawing functions for cluster representation

Original C implementation: ccpnmr2.4/c/ccpnmr/analysis/peak_cluster.c (240 lines)
"""

from enum import IntEnum
from typing import List, Optional, Tuple, Callable, Any
import numpy as np


class PeakClusterType(IntEnum):
    """Types of peak clusters representing different relationships."""
    MULTIPLET = 0   # Peaks in a multiplet splitting pattern
    SHIFT = 1       # Peaks representing same resonance at different shifts
    STATIC = 2      # User-defined static grouping
    SYMMETRY = 3    # Peaks related by molecular symmetry


class PeakCluster:
    """
    Collection of related NMR peaks with optional labels.
    
    Peak clusters group peaks that share some relationship such as
    multiplet splitting, shift differences, or molecular symmetry.
    Each cluster can have text labels for the overall cluster and
    for individual dimensions.
    
    Attributes:
        ndim: Number of dimensions
        cluster_type: Type of cluster relationship (PeakClusterType)
        text: Overall label for the cluster
        dim_text: Labels for each dimension
        peaks: List of Peak objects in this cluster
    """
    
    def __init__(self, ndim: int, cluster_type: int):
        """
        Create a new peak cluster.
        
        Args:
            ndim: Number of dimensions (must be positive)
            cluster_type: Type of cluster (0-3, see PeakClusterType)
            
        Raises:
            ValueError: If ndim <= 0 or cluster_type invalid
        """
        if ndim <= 0:
            raise ValueError(f"ndim must be positive, got {ndim}")
        if cluster_type not in range(4):
            raise ValueError(f"cluster_type must be 0-3, got {cluster_type}")
            
        self.ndim = ndim
        self.cluster_type = PeakClusterType(cluster_type)
        self.text = ""
        self.dim_text = ["" for _ in range(ndim)]
        self.peaks: List[Any] = []  # List of Peak objects
        
    def add_peak(self, peak) -> None:
        """
        Add a peak to this cluster.
        
        Args:
            peak: Peak object to add
            
        Raises:
            ValueError: If peak.ndim != self.ndim
        """
        if peak.ndim != self.ndim:
            raise ValueError(
                f"peak_cluster ndim = {self.ndim} != {peak.ndim} = peak ndim"
            )
        self.peaks.append(peak)
        
    def remove_peak(self, peak) -> None:
        """
        Remove a peak from this cluster.
        
        Args:
            peak: Peak object to remove
            
        Note:
            If peak is not in cluster, silently does nothing (matches C behavior)
        """
        try:
            self.peaks.remove(peak)
        except ValueError:
            pass  # Peak not in list, ignore
            
    def set_peaks(self, peaks: List[Any]) -> None:
        """
        Replace all peaks in cluster with new list.
        
        Args:
            peaks: New list of Peak objects
            
        Note:
            Takes ownership of the provided list (matches C behavior)
        """
        self.peaks = peaks
        
    def clear_peaks(self) -> None:
        """Remove all peaks from cluster."""
        self.peaks.clear()
        
    def set_text(self, text: str) -> None:
        """
        Set overall label text for cluster.
        
        Args:
            text: Label text (will be copied)
        """
        self.text = str(text)
        
    def set_dim_text(self, dim: int, text: str) -> None:
        """
        Set label text for a specific dimension.
        
        Args:
            dim: Dimension index (0-based)
            text: Label text (will be copied)
            
        Raises:
            ValueError: If dim out of range
        """
        if dim < 0 or dim >= self.ndim:
            raise ValueError(
                f"dim = {dim}, must be between 0 and {self.ndim - 1}"
            )
        self.dim_text[dim] = str(text)
        
    def get_bounding_box(self, xdim: int, ydim: int) -> Optional[Tuple[float, float, float, float]]:
        """
        Calculate bounding box of all peaks in cluster.
        
        Args:
            xdim: X dimension index
            ydim: Y dimension index
            
        Returns:
            Tuple of (xmin, xmax, ymin, ymax) or None if no peaks or dims invalid
        """
        if len(self.peaks) == 0:
            return None
            
        if xdim < 0 or xdim >= self.ndim:
            return None
            
        if ydim < 0 or ydim >= self.ndim:
            return None
            
        # Get positions for all peaks
        x_positions = [peak.position[xdim] for peak in self.peaks]
        y_positions = [peak.position[ydim] for peak in self.peaks]
        
        xmin = min(x_positions)
        xmax = max(x_positions)
        ymin = min(y_positions)
        ymax = max(y_positions)
        
        return (xmin, xmax, ymin, ymax)
        
    def draw(self, xdim: int, ydim: int, 
             drawing_funcs: dict, data: Any) -> None:
        """
        Draw cluster as bounding box with labels.
        
        Args:
            xdim: X dimension index
            ydim: Y dimension index
            drawing_funcs: Dictionary with 'draw_line' and 'draw_text' callbacks
            data: User data passed to drawing callbacks
            
        Note:
            Draws rectangle around peaks with labels at edges and center.
            Labels are only drawn if text is non-empty.
        """
        bbox = self.get_bounding_box(xdim, ydim)
        if bbox is None:
            return
            
        xmin, xmax, ymin, ymax = bbox
        
        # Draw bounding box
        draw_line = drawing_funcs.get('draw_line')
        if draw_line:
            draw_line(data, xmin, ymin, xmax, ymin)  # Bottom
            draw_line(data, xmax, ymin, xmax, ymax)  # Right
            draw_line(data, xmax, ymax, xmin, ymax)  # Top
            draw_line(data, xmin, ymax, xmin, ymin)  # Left
            
        # Calculate center
        x_center = 0.5 * (xmin + xmax)
        y_center = 0.5 * (ymin + ymax)
        
        draw_text = drawing_funcs.get('draw_text')
        if draw_text:
            # Draw dimension labels
            xdim_text = self.dim_text[xdim]
            if xdim_text:
                # Label at top center
                draw_text(data, xdim_text, x_center, ymax, 0.0, 0.0)
                
            ydim_text = self.dim_text[ydim]
            if ydim_text:
                # Label at right center
                draw_text(data, ydim_text, xmax, y_center, 0.0, 0.0)
                
            # Draw cluster label at center
            if self.text:
                draw_text(data, self.text, x_center, y_center, 0.0, 0.0)
    
    def __len__(self) -> int:
        """Return number of peaks in cluster."""
        return len(self.peaks)
        
    def __repr__(self) -> str:
        """String representation of cluster."""
        type_name = self.cluster_type.name
        label = f" '{self.text}'" if self.text else ""
        return f"PeakCluster({type_name}, {len(self.peaks)} peaks{label})"


# C API compatibility functions
def new_peak_cluster(ndim: int, cluster_type: int) -> PeakCluster:
    """
    Create a new peak cluster (C API compatible).
    
    Args:
        ndim: Number of dimensions
        cluster_type: Cluster type (0-3)
        
    Returns:
        New PeakCluster instance
    """
    return PeakCluster(ndim, cluster_type)


def delete_peak_cluster(peak_cluster: PeakCluster) -> None:
    """
    Delete a peak cluster (C API compatible).
    
    Args:
        peak_cluster: Cluster to delete
        
    Note:
        In Python, this is a no-op as garbage collection handles cleanup.
        Provided for C API compatibility.
    """
    pass  # Python handles memory management


def add_peak_peak_cluster(peak_cluster: PeakCluster, peak, 
                          error_msg: Optional[list] = None) -> bool:
    """
    Add peak to cluster with error handling (C API compatible).
    
    Args:
        peak_cluster: Cluster to add to
        peak: Peak to add
        error_msg: Optional list to receive error message
        
    Returns:
        True on success, False on error
    """
    try:
        peak_cluster.add_peak(peak)
        return True
    except ValueError as e:
        if error_msg is not None:
            error_msg.append(str(e))
        return False


def remove_peak_peak_cluster(peak_cluster: PeakCluster, peak) -> None:
    """
    Remove peak from cluster (C API compatible).
    
    Args:
        peak_cluster: Cluster to remove from
        peak: Peak to remove
    """
    peak_cluster.remove_peak(peak)


def set_peaks_peak_cluster(peak_cluster: PeakCluster, peaks: List[Any]) -> None:
    """
    Replace all peaks in cluster (C API compatible).
    
    Args:
        peak_cluster: Cluster to modify
        peaks: New list of peaks
    """
    peak_cluster.set_peaks(peaks)


def clear_peaks_peak_cluster(peak_cluster: PeakCluster) -> None:
    """
    Clear all peaks from cluster (C API compatible).
    
    Args:
        peak_cluster: Cluster to clear
    """
    peak_cluster.clear_peaks()


def set_text_peak_cluster(peak_cluster: PeakCluster, text: str,
                          error_msg: Optional[list] = None) -> bool:
    """
    Set cluster text label (C API compatible).
    
    Args:
        peak_cluster: Cluster to modify
        text: Label text
        error_msg: Optional list to receive error message
        
    Returns:
        True on success, False on error
    """
    try:
        peak_cluster.set_text(text)
        return True
    except Exception as e:
        if error_msg is not None:
            error_msg.append(str(e))
        return False


def set_dim_text_peak_cluster(peak_cluster: PeakCluster, dim: int, text: str,
                               error_msg: Optional[list] = None) -> bool:
    """
    Set dimension text label (C API compatible).
    
    Args:
        peak_cluster: Cluster to modify
        dim: Dimension index
        text: Label text
        error_msg: Optional list to receive error message
        
    Returns:
        True on success, False on error
    """
    try:
        peak_cluster.set_dim_text(dim, text)
        return True
    except ValueError as e:
        if error_msg is not None:
            error_msg.append(str(e))
        return False


def draw_peak_cluster(peak_cluster: PeakCluster, xdim: int, ydim: int,
                      drawing_funcs: dict, data: Any) -> None:
    """
    Draw cluster visualization (C API compatible).
    
    Args:
        peak_cluster: Cluster to draw
        xdim: X dimension index
        ydim: Y dimension index
        drawing_funcs: Drawing function callbacks
        data: User data for callbacks
    """
    peak_cluster.draw(xdim, ydim, drawing_funcs, data)
