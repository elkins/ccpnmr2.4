"""
Contour Levels - Contour level management for NMR spectra

This module provides contour level storage and manipulation, organizing
levels into negative and positive groups for spectral display.

Python implementation of ccpnmr/analysis/contour_levels.c

Original C implementation: Wayne Boucher and Tim Stevens (University of Cambridge)
Python conversion: 2024
"""

import numpy as np
from typing import Optional, List


class ContourLevels:
    """Contour levels for NMR spectrum display
    
    Stores contour levels organized as negative levels first, then positive levels.
    This ordering is useful for efficient contour drawing where negative and positive
    contours are typically drawn in different colors.
    
    Attributes:
        nlevels: Total number of contour levels
        levels: Array of contour level values (negative first, then positive)
    """
    
    def __init__(self, levels: np.ndarray):
        """Create contour levels from input array
        
        Automatically sorts levels with negative values first, then positive values.
        This matches the C implementation's ordering for efficient display.
        
        Args:
            levels: Array of contour level values (any order)
        """
        levels_array = np.asarray(levels, dtype=np.float32)
        
        # Separate negative and positive levels
        negative = levels_array[levels_array < 0]
        positive = levels_array[levels_array >= 0]
        
        # Concatenate: negative first, then positive
        self.levels = np.concatenate([negative, positive])
        self.nlevels = len(self.levels)
    
    def __del__(self):
        """Delete contour levels"""
        # Python's garbage collection handles this automatically
        pass
    
    def copy(self) -> 'ContourLevels':
        """Create a copy of the contour levels
        
        Returns:
            New ContourLevels object with copied data
        """
        return ContourLevels(self.levels.copy())
    
    def __eq__(self, other: 'ContourLevels') -> bool:
        """Check if two contour levels are equal
        
        Args:
            other: Another ContourLevels object
            
        Returns:
            True if levels match exactly, False otherwise
        """
        if not isinstance(other, ContourLevels):
            return False
        
        if self.nlevels != other.nlevels:
            return False
        
        return np.array_equal(self.levels, other.levels)
    
    def have_neg_contour_levels(self) -> bool:
        """Check if there are any negative contour levels
        
        Returns:
            True if at least one level is negative
        """
        return np.any(self.levels < 0)
    
    def have_pos_contour_levels(self) -> bool:
        """Check if there are any positive contour levels
        
        Returns:
            True if at least one level is positive or zero
        """
        return np.any(self.levels >= 0)
    
    def get_negative_levels(self) -> np.ndarray:
        """Get only the negative contour levels
        
        Returns:
            Array of negative levels (may be empty)
        """
        return self.levels[self.levels < 0]
    
    def get_positive_levels(self) -> np.ndarray:
        """Get only the positive contour levels
        
        Returns:
            Array of positive/zero levels (may be empty)
        """
        return self.levels[self.levels >= 0]


# C API compatibility functions

def new_contour_levels(levels: np.ndarray) -> ContourLevels:
    """Create new contour levels
    
    Args:
        levels: Array of contour level values
        
    Returns:
        ContourLevels object
    """
    return ContourLevels(levels)


def delete_contour_levels(contour_levels: ContourLevels):
    """Delete contour levels
    
    Args:
        contour_levels: ContourLevels object to delete
    """
    del contour_levels


def copy_contour_levels(contour_levels: ContourLevels) -> ContourLevels:
    """Copy contour levels
    
    Args:
        contour_levels: ContourLevels object to copy
        
    Returns:
        New ContourLevels object with copied data
    """
    return contour_levels.copy()


def equal_contour_levels(contour_levels1: ContourLevels, 
                         contour_levels2: ContourLevels) -> bool:
    """Check if two contour levels are equal
    
    Args:
        contour_levels1: First ContourLevels object
        contour_levels2: Second ContourLevels object
        
    Returns:
        True if equal, False otherwise
    """
    return contour_levels1 == contour_levels2


def have_neg_contour_levels(contour_levels: ContourLevels) -> bool:
    """Check if contour levels include negative values
    
    Args:
        contour_levels: ContourLevels object
        
    Returns:
        True if at least one level is negative
    """
    return contour_levels.have_neg_contour_levels()


def have_pos_contour_levels(contour_levels: ContourLevels) -> bool:
    """Check if contour levels include positive values
    
    Args:
        contour_levels: ContourLevels object
        
    Returns:
        True if at least one level is positive or zero
    """
    return contour_levels.have_pos_contour_levels()
