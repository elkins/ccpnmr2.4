"""
Contour Style Configuration

Python implementation of contour_style.c for NMR contour display styling.

Manages colors and line styles for positive and negative contour levels.
Typically positive contours use solid lines and negative contours use
dashed lines, with different color schemes for each.

Original C implementation: ccpnmr2.4/c/ccpnmr/analysis/contour_style.c (78 lines)
"""

from typing import List, Tuple, Optional
import numpy as np


# Line style constants (matching C definitions)
NORMAL_LINE_STYLE = 0
DASHED_LINE_STYLE = 1
NLINE_STYLES = 2


class ContourStyle:
    """
    Contour display styling configuration.
    
    Manages colors and line styles for positive and negative contour levels
    in NMR spectrum display. Colors are RGB triplets in range [0, 1].
    
    Attributes:
        pos_colors: List of RGB color arrays for positive contours
        neg_colors: List of RGB color arrays for negative contours
        pos_line_style: Line style for positive contours (0=normal, 1=dashed)
        neg_line_style: Line style for negative contours (0=normal, 1=dashed)
    """
    
    def __init__(self, 
                 pos_colors: List[Tuple[float, float, float]],
                 neg_colors: List[Tuple[float, float, float]],
                 pos_line_style: int = NORMAL_LINE_STYLE,
                 neg_line_style: int = DASHED_LINE_STYLE):
        """
        Create a new contour style configuration.
        
        Args:
            pos_colors: List of RGB tuples for positive contours
            neg_colors: List of RGB tuples for negative contours
            pos_line_style: Line style for positive (default: normal)
            neg_line_style: Line style for negative (default: dashed)
            
        Raises:
            ValueError: If line styles are invalid or colors are malformed
        """
        if pos_line_style not in range(NLINE_STYLES):
            raise ValueError(f"pos_line_style must be 0 or 1, got {pos_line_style}")
        if neg_line_style not in range(NLINE_STYLES):
            raise ValueError(f"neg_line_style must be 0 or 1, got {neg_line_style}")
            
        # Store colors as numpy arrays for easy manipulation
        self.pos_colors = [np.array(color, dtype=np.float32) for color in pos_colors]
        self.neg_colors = [np.array(color, dtype=np.float32) for color in neg_colors]
        self.pos_line_style = pos_line_style
        self.neg_line_style = neg_line_style
        
        # Validate color arrays
        for i, color in enumerate(self.pos_colors):
            if color.shape != (3,):
                raise ValueError(f"pos_colors[{i}] must be RGB triplet, got shape {color.shape}")
        for i, color in enumerate(self.neg_colors):
            if color.shape != (3,):
                raise ValueError(f"neg_colors[{i}] must be RGB triplet, got shape {color.shape}")
    
    @property
    def npos_colors(self) -> int:
        """Number of positive contour colors."""
        return len(self.pos_colors)
    
    @property
    def nneg_colors(self) -> int:
        """Number of negative contour colors."""
        return len(self.neg_colors)
        
    def get_pos_color(self, index: int) -> np.ndarray:
        """
        Get positive contour color by index (cycles through colors).
        
        Args:
            index: Color index
            
        Returns:
            RGB color array [r, g, b]
        """
        if self.npos_colors == 0:
            return np.array([1.0, 0.0, 0.0], dtype=np.float32)  # Default red
        return self.pos_colors[index % self.npos_colors]
    
    def get_neg_color(self, index: int) -> np.ndarray:
        """
        Get negative contour color by index (cycles through colors).
        
        Args:
            index: Color index
            
        Returns:
            RGB color array [r, g, b]
        """
        if self.nneg_colors == 0:
            return np.array([0.0, 0.0, 1.0], dtype=np.float32)  # Default blue
        return self.neg_colors[index % self.nneg_colors]
        
    def __repr__(self) -> str:
        """String representation."""
        pos_style = "normal" if self.pos_line_style == NORMAL_LINE_STYLE else "dashed"
        neg_style = "normal" if self.neg_line_style == NORMAL_LINE_STYLE else "dashed"
        return (f"ContourStyle(pos={self.npos_colors} colors, {pos_style}; "
                f"neg={self.nneg_colors} colors, {neg_style})")


# C API compatibility functions
def new_contour_style(pos_colors: List[Tuple[float, float, float]],
                     neg_colors: List[Tuple[float, float, float]],
                     pos_line_style: int = NORMAL_LINE_STYLE,
                     neg_line_style: int = DASHED_LINE_STYLE) -> ContourStyle:
    """
    Create a new contour style (C API compatible).
    
    Args:
        pos_colors: List of RGB tuples for positive contours
        neg_colors: List of RGB tuples for negative contours
        pos_line_style: Line style for positive (0=normal, 1=dashed)
        neg_line_style: Line style for negative (0=normal, 1=dashed)
        
    Returns:
        New ContourStyle instance
        
    Note:
        In C, this function takes ownership of the color arrays.
        In Python, colors are copied into numpy arrays.
    """
    return ContourStyle(pos_colors, neg_colors, pos_line_style, neg_line_style)


def delete_contour_style(contour_style: ContourStyle) -> None:
    """
    Delete a contour style (C API compatible).
    
    Args:
        contour_style: Style to delete
        
    Note:
        In Python, this is a no-op as garbage collection handles cleanup.
        Provided for C API compatibility.
    """
    pass  # Python handles memory management
