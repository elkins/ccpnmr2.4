"""
Peak List - Collection of NMR peaks with search and selection operations

This module provides a peak list container for managing collections of NMR peaks,
including peak finding/picking, region searches, and selection operations.

Python implementation of ccpnmr/analysis/peak_list.c

Original C implementation: Wayne Boucher and Tim Stevens (University of Cambridge)
Python conversion: 2024
"""

import numpy as np
from typing import Optional, Tuple, List
from .peak import Peak

# Constants
NCOLORS = 3
NALLOC = 50
DEFAULT_SYMBOL = 0
MAX_NDIM = 10


class DiagonalExclusion:
    """Diagonal exclusion region for peak picking
    
    Excludes peaks along diagonal lines (e.g., for NOESY diagonal)
    defined by: |a1*x[dim1] - a2*x[dim2] + b12| < d
    """
    
    def __init__(self, dim1: int, dim2: int, a1: float, a2: float, b12: float, d: float):
        self.dim1 = dim1
        self.dim2 = dim2
        self.a1 = a1
        self.a2 = a2
        self.b12 = b12
        self.d = d


class PeakList:
    """Collection of NMR peaks with search and selection operations
    
    Attributes:
        ndim: Number of dimensions
        npoints: Array of spectrum sizes (for aliasing calculations)
        color: RGB color array [r, g, b] in range [0, 1]
        symbol: Symbol type for peak display
        peaks: List of Peak objects
        npeaks: Current number of peaks
    """
    
    def __init__(self, ndim: int, npoints: np.ndarray):
        """Create a new peak list
        
        Args:
            ndim: Number of dimensions
            npoints: Array of spectrum sizes per dimension
        """
        self.ndim = ndim
        self.npoints = np.array(npoints, dtype=np.int32).copy()
        self.color = np.zeros(NCOLORS, dtype=np.float32)  # Black default
        self.symbol = DEFAULT_SYMBOL
        self.peaks: List[Peak] = []
        self.npeaks = 0
    
    def __del__(self):
        """Delete peak list and all contained peaks"""
        # Python's garbage collection handles this automatically
        pass
    
    def is_selected_peak_list(self, is_selected: bool):
        """Set selection state for all peaks in the list
        
        Args:
            is_selected: True to select all peaks, False to unselect
        """
        for peak in self.peaks:
            peak.set_is_selected(is_selected)
    
    def set_color_peak_list(self, color: np.ndarray):
        """Set the color for the peak list
        
        Args:
            color: RGB array [r, g, b] in range [0, 1]
        """
        self.color = np.array(color, dtype=np.float32).copy()
    
    def set_symbol_peak_list(self, symbol: int) -> bool:
        """Set the symbol type for peak display
        
        Args:
            symbol: Symbol type identifier
            
        Returns:
            True on success
        """
        self.symbol = symbol
        return True
    
    def add_peak_peak_list(self) -> Peak:
        """Add a new peak to the list
        
        Returns:
            The newly created Peak object
        """
        peak = Peak(self.ndim)
        self.peaks.append(peak)
        self.npeaks += 1
        return peak
    
    def remove_peak_peak_list(self, peak: Peak) -> bool:
        """Remove a specific peak from the list
        
        Args:
            peak: Peak to remove
            
        Returns:
            True if peak was found and removed, False otherwise
        """
        try:
            self.peaks.remove(peak)
            self.npeaks -= 1
            return True
        except ValueError:
            return False
    
    def remove_selected_peak_list(self):
        """Remove all selected peaks from the list"""
        self.peaks = [peak for peak in self.peaks if not peak.get_is_selected()]
        self.npeaks = len(self.peaks)
    
    def unselect_selected_peak_list(self):
        """Unselect all selected peaks"""
        for peak in self.peaks:
            peak.set_is_selected(False)
    
    def find_peak_list(self, first: np.ndarray, last: np.ndarray,
                      block_file,  # Type would be BlockFile
                      have_low: bool = False, have_high: bool = False,
                      low: float = 0.0, high: float = 0.0,
                      buffer: Optional[np.ndarray] = None,
                      nonadjacent: bool = True,
                      drop_factor: float = 0.0,
                      min_linewidth: Optional[np.ndarray] = None,
                      diagonal_exclusions: Optional[List[DiagonalExclusion]] = None,
                      excluded_regions: Optional[List[np.ndarray]] = None,
                      dim_checked: Optional[np.ndarray] = None,
                      ignore_peak: int = -1) -> bool:
        """Find peaks in a spectral region (automated peak picking)
        
        This is the main peak picking algorithm. It searches for local maxima/minima
        in the spectrum data, with various filtering criteria.
        
        Args:
            first: Starting indices for search region
            last: Ending indices for search region
            block_file: Spectral data file object
            have_low: Look for minima below threshold
            have_high: Look for maxima above threshold
            low: Minimum threshold value
            high: Maximum threshold value
            buffer: Minimum distance between peaks (per dimension)
            nonadjacent: Check all 3^n neighbors (True) or only 2n adjacent (False)
            drop_factor: Required fractional intensity drop from peak
            min_linewidth: Minimum linewidth per dimension
            diagonal_exclusions: List of diagonal exclusion regions
            excluded_regions: List of rectangular exclusion regions
            dim_checked: Which dimensions to check for extrema
            ignore_peak: Index of peak to ignore (for refinement)
            
        Returns:
            True on success
        """
        if not have_low and not have_high:
            return True
        
        if buffer is None:
            buffer = np.zeros(self.ndim, dtype=np.int32)
        
        if min_linewidth is None:
            min_linewidth = np.zeros(self.ndim, dtype=np.float32)
        
        if dim_checked is None:
            dim_checked = np.ones(self.ndim, dtype=bool)
        
        if diagonal_exclusions is None:
            diagonal_exclusions = []
        
        if excluded_regions is None:
            excluded_regions = []
        
        # Calculate cumulative products for index mapping
        cum_points = np.ones(self.ndim, dtype=np.int32)
        for i in range(self.ndim):
            if i > 0:
                cum_points[i] = cum_points[i-1] * (last[i-1] - first[i-1])
        
        npoints = cum_points[-1] * (last[-1] - first[-1])
        
        # Set up for nonadjacent checking (3^ndim neighbors)
        if nonadjacent:
            cumulative = np.array([3**i for i in range(self.ndim)], dtype=np.int32)
            nadj_points = 3**self.ndim
            zero_index = (nadj_points - 1) // 2
        else:
            cumulative = None
            nadj_points = 0
            zero_index = 0
        
        # Iterate through all points in region
        for n in range(npoints):
            # Convert linear index to multi-dimensional point
            point = self._find_point(n, cum_points, first)
            
            # Check diagonal exclusions
            if diagonal_exclusions:
                excluded = False
                for de in diagonal_exclusions:
                    delta = de.a1 * point[de.dim1] - de.a2 * point[de.dim2] + de.b12
                    if abs(delta) < de.d:
                        excluded = True
                        break
                if excluded:
                    continue
            
            # Check rectangular exclusion regions
            if excluded_regions:
                excluded = False
                for region in excluded_regions:
                    in_region = True
                    for k in range(self.ndim):
                        if point[k] < region[k][0] or point[k] > region[k][1]:
                            in_region = False
                            break
                    if in_region:
                        excluded = True
                        break
                if excluded:
                    continue
            
            # Get intensity value at point
            v = block_file.get_point(point)
            
            # Check if above/below threshold
            if have_high and v >= high:
                find_maximum = True
            elif have_low and v <= low:
                find_maximum = False
            else:
                continue
            
            # Check if local extremum
            if nonadjacent:
                ok_extreme = self._check_nonadjacent_points(
                    block_file, find_maximum, buffer, v, point, 
                    nadj_points, cumulative, dim_checked, zero_index
                )
            else:
                ok_extreme = self._check_adjacent_points(
                    block_file, find_maximum, buffer, v, point, dim_checked
                )
            
            if not ok_extreme:
                continue
            
            # Check intensity drop requirement
            if drop_factor > 0:
                ok_drop = self._check_drop(
                    block_file, find_maximum, drop_factor, v, point
                )
                if not ok_drop:
                    continue
            
            # Check linewidth requirements
            ok_linewidth = self._check_linewidth(
                block_file, find_maximum, min_linewidth, v, point
            )
            if not ok_linewidth:
                continue
            
            # Check if within buffer distance of existing peaks
            if not self._check_new_peak(buffer, point, ignore_peak):
                continue
            
            # Add new peak
            peak = self.add_peak_peak_list()
            position = point.astype(np.float32) + 1.0  # Positions start at 1
            peak.set_position(position)
        
        return True
    
    def search_region_peak_list(self, first: np.ndarray, last: np.ndarray,
                                allow_aliasing: Optional[np.ndarray] = None
                                ) -> Tuple[int, Optional[np.ndarray]]:
        """Search for peaks within a specified region
        
        Args:
            first: Lower bounds of search region
            last: Upper bounds of search region
            allow_aliasing: Per-dimension flag for aliasing
            
        Returns:
            Tuple of (number of peaks found, array of peak indices)
        """
        if self.npeaks == 0:
            return 0, None
        
        if allow_aliasing is None:
            allow_aliasing = np.zeros(self.ndim, dtype=bool)
        
        indices = []
        for i, peak in enumerate(self.peaks):
            if peak.is_in_region(first, last, self.npoints, allow_aliasing):
                indices.append(i)
        
        if indices:
            return len(indices), np.array(indices, dtype=np.int32)
        else:
            return 0, None
    
    def search_nearest_peak_list(self, xdim: int, ydim: int,
                                 xscale: float, yscale: float,
                                 first: np.ndarray, last: np.ndarray,
                                 allow_aliasing: Optional[np.ndarray] = None
                                 ) -> Tuple[int, float]:
        """Search for the nearest peak to a 2D region
        
        Used for interactive peak selection in spectrum displays.
        
        Args:
            xdim: X dimension index
            ydim: Y dimension index
            xscale: X dimension scale factor
            yscale: Y dimension scale factor
            first: Lower bounds of search region
            last: Upper bounds of search region
            allow_aliasing: Per-dimension flag for aliasing
            
        Returns:
            Tuple of (peak index or -1 if none, squared distance)
        """
        if allow_aliasing is None:
            allow_aliasing = np.zeros(self.ndim, dtype=bool)
        
        nearest = -1
        d2_min = 0.0
        
        # Get peak intensity/volume scaling
        intensity_max, volume_max = self.determine_peak_list_max()
        
        # Store original bounds
        xfirst, xlast = first[xdim], last[xdim]
        yfirst, ylast = first[ydim], last[ydim]
        
        for i, peak in enumerate(self.peaks):
            # Reset bounds
            first[xdim], last[xdim] = xfirst, xlast
            first[ydim], last[ydim] = yfirst, ylast
            
            # Scale search region by peak intensity/volume
            scale = self._determine_peak_scale(peak, intensity_max, volume_max)
            # For now, use scale = 1.0 (original code also does this)
            scale = 1.0
            
            # Find scaled region around peak
            first_region, last_region = peak.find_scaled_region(xdim, ydim, 
                                                                scale * xscale, 
                                                                scale * yscale)
            first = np.array(first_region, dtype=np.float32)
            last = np.array(last_region, dtype=np.float32)
            
            # Check if peak is in region
            d2_array = np.zeros(self.ndim, dtype=np.float32)
            if peak.is_in_region(first, last, self.npoints, 
                                allow_aliasing, d2_array):
                d2 = d2_array[xdim] + d2_array[ydim]
                if nearest < 0 or d2 < d2_min:
                    d2_min = d2
                    nearest = i
        
        return nearest, d2_min
    
    def determine_peak_list_max(self) -> Tuple[float, float]:
        """Determine maximum intensity and volume in peak list
        
        Returns:
            Tuple of (max intensity, max volume)
        """
        intensity_max = 0.0
        volume_max = 0.0
        
        for peak in self.peaks:
            intensity_max = max(intensity_max, abs(peak.intensity))
            volume_max = max(volume_max, abs(peak.volume))
        
        return intensity_max, volume_max
    
    # Helper methods
    
    def _find_point(self, n: int, cum_points: np.ndarray, 
                   offset: np.ndarray) -> np.ndarray:
        """Convert linear index to multi-dimensional point"""
        point = np.zeros(self.ndim, dtype=np.int32)
        remaining = n
        for i in range(self.ndim - 1, -1, -1):
            point[i] = remaining // cum_points[i]
            remaining %= cum_points[i]
        return point + offset
    
    def _peak_within_buffer(self, point: np.ndarray, peak: Peak, 
                           buffer: np.ndarray) -> bool:
        """Check if peak is within buffer distance of point"""
        if peak.position is None:
            return False
        
        for i in range(self.ndim):
            d = abs(point[i] - peak.position[i] + 1)  # +1 because positions start at 1
            if d > buffer[i]:
                return False
        
        return True
    
    def _check_new_peak(self, buffer: np.ndarray, point: np.ndarray, 
                       ignore_peak: int) -> bool:
        """Check if point is far enough from existing peaks"""
        for i, peak in enumerate(self.peaks):
            if ignore_peak == i:
                continue
            if self._peak_within_buffer(point, peak, buffer):
                return False
        return True
    
    def _check_nonadjacent_points(self, block_file, find_maximum: bool,
                                  buffer: np.ndarray, v: float, point: np.ndarray,
                                  npoints: int, cumulative: np.ndarray,
                                  dim_checked: np.ndarray, zero_index: int) -> bool:
        """Check if point is local extremum (all 3^n neighbors)"""
        # Check all neighbors in 3^ndim grid (-1, 0, +1 per dimension)
        for n in range(npoints):
            if n == zero_index:  # Skip center point
                continue
            
            # Convert to neighbor offset
            p = np.zeros(self.ndim, dtype=np.int32)
            remaining = n
            for i in range(self.ndim - 1, -1, -1):
                p[i] = remaining // cumulative[i]
                remaining %= cumulative[i]
                p[i] -= 1  # Convert from 0,1,2 to -1,0,1
            
            # Check if we should examine this neighbor
            do_point = True
            neighbor = np.copy(point)
            for i in range(self.ndim):
                if not dim_checked[i] and p[i] != 0:
                    do_point = False
                    break
                neighbor[i] += p[i]
                
                # Handle wrapping/boundaries
                if block_file.dim_wrapped[i]:
                    neighbor[i] %= block_file.points[i]
                elif neighbor[i] < 0 or neighbor[i] >= block_file.points[i]:
                    do_point = False
                    break
            
            if not do_point:
                continue
            
            # Get neighbor value and compare
            v2 = block_file.get_point(neighbor)
            if find_maximum:
                if v2 > v:
                    return False
            else:
                if v2 < v:
                    return False
        
        return True
    
    def _check_adjacent_points(self, block_file, find_maximum: bool,
                               buffer: np.ndarray, v: float, point: np.ndarray,
                               dim_checked: np.ndarray) -> bool:
        """Check if point is local extremum (only adjacent neighbors)"""
        for i in range(self.ndim):
            if not dim_checked[i]:
                continue
            
            # Check lower neighbor
            if block_file.dim_wrapped[i] or point[i] > 0:
                p = np.copy(point)
                if p[i] == 0:
                    p[i] = block_file.points[i] - 1
                else:
                    p[i] -= 1
                
                v2 = block_file.get_point(p)
                if find_maximum:
                    if v2 > v:
                        return False
                else:
                    if v2 < v:
                        return False
            
            # Check upper neighbor
            if block_file.dim_wrapped[i] or point[i] < block_file.points[i] - 1:
                p = np.copy(point)
                p[i] = (p[i] + 1) % block_file.points[i]
                
                v2 = block_file.get_point(p)
                if find_maximum:
                    if v2 > v:
                        return False
                else:
                    if v2 < v:
                        return False
        
        return True
    
    def _drops_in_direction(self, block_file, find_maximum: bool,
                           drop: float, v: float, point: np.ndarray,
                           dim: int, dirn: int) -> bool:
        """Check if intensity drops sufficiently in one direction"""
        if dirn == 1:
            i_start = point[dim] + 1
            if block_file.dim_wrapped[dim]:
                i_end = i_start + block_file.points[dim] - 1
            else:
                i_end = block_file.points[dim]
            i_step = 1
        else:
            i_start = point[dim] - 1
            if block_file.dim_wrapped[dim]:
                i_end = i_start - block_file.points[dim] + 1
            else:
                i_end = -1
            i_step = -1
        
        q = np.copy(point)
        v_prev = v
        
        i = i_start
        while i != i_end:
            q[dim] = (i + block_file.points[dim]) % block_file.points[dim]
            v_this = block_file.get_point(q)
            
            if find_maximum:
                if v_this > v_prev:
                    return False
                elif (v - v_this) >= drop:
                    break
            else:
                if v_this < v_prev:
                    return False
                elif (v_this - v) >= drop:
                    break
            
            v_prev = v_this
            i += i_step
        
        return True
    
    def _check_drop(self, block_file, find_maximum: bool,
                   drop_factor: float, v: float, point: np.ndarray) -> bool:
        """Check if peak has sufficient intensity drop in all directions"""
        if drop_factor <= 0:
            return True
        
        drop = drop_factor * abs(v)
        
        for i in range(self.ndim):
            # Check both directions
            if not self._drops_in_direction(block_file, find_maximum, 
                                           drop, v, point, i, 1):
                return False
            if not self._drops_in_direction(block_file, find_maximum, 
                                           drop, v, point, i, -1):
                return False
        
        return True
    
    def _check_linewidth(self, block_file, find_maximum: bool,
                        min_linewidth: np.ndarray, v: float, 
                        point: np.ndarray) -> bool:
        """Check if peak meets minimum linewidth requirements"""
        for i in range(self.ndim):
            if min_linewidth[i] <= 0:
                continue
            
            linewidth = block_file.linewidth(find_maximum, v, point, i)
            if linewidth < min_linewidth[i]:
                return False
        
        return True
    
    @staticmethod
    def _determine_peak_scale(peak: Peak, intensity_max: float, 
                             volume_max: float) -> float:
        """Determine logarithmic scale factor for peak based on intensity/volume"""
        z = abs(peak.volume)
        if z == 0:
            zmax = intensity_max
            z = abs(peak.intensity)
        else:
            zmax = volume_max
        
        if z == 0:
            scale = 0.5  # Arbitrary default
        elif z >= zmax:
            scale = 1.0
        else:
            log_ratio = np.log10(z / zmax)
            if log_ratio >= -0.01:  # Very close to 1.0, avoid division issues
                scale = 1.0
            else:
                scale = 1.0 / (1.0 - log_ratio)
        
        return scale


# C API compatibility functions

def new_peak_list(ndim: int, npoints: np.ndarray) -> PeakList:
    """Create a new peak list"""
    return PeakList(ndim, npoints)


def delete_peak_list(peak_list: PeakList):
    """Delete a peak list"""
    del peak_list


def is_selected_peak_list(peak_list: PeakList, is_selected: bool):
    """Set selection state for all peaks"""
    peak_list.is_selected_peak_list(is_selected)


def set_color_peak_list(peak_list: PeakList, color: np.ndarray):
    """Set peak list color"""
    peak_list.set_color_peak_list(color)


def set_symbol_peak_list(peak_list: PeakList, symbol: int) -> bool:
    """Set peak list symbol"""
    return peak_list.set_symbol_peak_list(symbol)


def add_peak_peak_list(peak_list: PeakList) -> Peak:
    """Add a new peak to the list"""
    return peak_list.add_peak_peak_list()


def remove_peak_peak_list(peak_list: PeakList, peak: Peak) -> bool:
    """Remove a peak from the list"""
    return peak_list.remove_peak_peak_list(peak)


def remove_selected_peak_list(peak_list: PeakList):
    """Remove all selected peaks"""
    peak_list.remove_selected_peak_list()


def unselect_selected_peak_list(peak_list: PeakList):
    """Unselect all peaks"""
    peak_list.unselect_selected_peak_list()


def search_region_peak_list(peak_list: PeakList, first: np.ndarray, 
                           last: np.ndarray, 
                           allow_aliasing: Optional[np.ndarray] = None
                           ) -> Tuple[int, Optional[np.ndarray]]:
    """Search for peaks in a region"""
    return peak_list.search_region_peak_list(first, last, allow_aliasing)


def search_nearest_peak_list(peak_list: PeakList, xdim: int, ydim: int,
                             xscale: float, yscale: float,
                             first: np.ndarray, last: np.ndarray,
                             allow_aliasing: Optional[np.ndarray] = None
                             ) -> Tuple[int, float]:
    """Search for nearest peak to a 2D region"""
    return peak_list.search_nearest_peak_list(xdim, ydim, xscale, yscale, 
                                             first, last, allow_aliasing)


def determine_peak_scale(peak: Peak, intensity_max: float, 
                        volume_max: float) -> float:
    """Determine peak scale factor"""
    return PeakList._determine_peak_scale(peak, intensity_max, volume_max)


def determine_peak_list_max(peak_list: PeakList) -> Tuple[float, float]:
    """Determine maximum intensity and volume"""
    return peak_list.determine_peak_list_max()
