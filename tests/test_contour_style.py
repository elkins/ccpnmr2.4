"""
Tests for contour_style module.

Tests the ContourStyle class for NMR contour display styling.
"""

import pytest
import numpy as np
from ccpnmr.analysis.python_impl.contour_style import (
    ContourStyle, new_contour_style, delete_contour_style,
    NORMAL_LINE_STYLE, DASHED_LINE_STYLE, NLINE_STYLES
)


class TestContourStyleConstants:
    """Test contour style constants."""
    
    def test_line_style_values(self):
        """Test line style constant values."""
        assert NORMAL_LINE_STYLE == 0
        assert DASHED_LINE_STYLE == 1
        assert NLINE_STYLES == 2


class TestContourStyleCreation:
    """Test contour style creation."""
    
    def test_create_basic(self):
        """Test creating basic contour style."""
        pos_colors = [(1.0, 0.0, 0.0)]  # Red
        neg_colors = [(0.0, 0.0, 1.0)]  # Blue
        
        style = ContourStyle(pos_colors, neg_colors)
        
        assert style.npos_colors == 1
        assert style.nneg_colors == 1
        assert style.pos_line_style == NORMAL_LINE_STYLE
        assert style.neg_line_style == DASHED_LINE_STYLE
        
    def test_create_multiple_colors(self):
        """Test creating style with multiple colors."""
        pos_colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        neg_colors = [(1.0, 1.0, 0.0), (0.0, 1.0, 1.0)]
        
        style = ContourStyle(pos_colors, neg_colors)
        
        assert style.npos_colors == 3
        assert style.nneg_colors == 2
        
    def test_create_custom_line_styles(self):
        """Test creating style with custom line styles."""
        pos_colors = [(1.0, 0.0, 0.0)]
        neg_colors = [(0.0, 0.0, 1.0)]
        
        style = ContourStyle(pos_colors, neg_colors,
                           pos_line_style=DASHED_LINE_STYLE,
                           neg_line_style=NORMAL_LINE_STYLE)
        
        assert style.pos_line_style == DASHED_LINE_STYLE
        assert style.neg_line_style == NORMAL_LINE_STYLE
        
    def test_create_empty_colors(self):
        """Test creating style with no colors."""
        style = ContourStyle([], [])
        
        assert style.npos_colors == 0
        assert style.nneg_colors == 0
        
    def test_create_invalid_pos_line_style(self):
        """Test that invalid pos line style raises error."""
        with pytest.raises(ValueError, match="pos_line_style must be 0 or 1"):
            ContourStyle([(1.0, 0.0, 0.0)], [(0.0, 0.0, 1.0)],
                        pos_line_style=2)
            
    def test_create_invalid_neg_line_style(self):
        """Test that invalid neg line style raises error."""
        with pytest.raises(ValueError, match="neg_line_style must be 0 or 1"):
            ContourStyle([(1.0, 0.0, 0.0)], [(0.0, 0.0, 1.0)],
                        neg_line_style=-1)
            
    def test_create_invalid_color_shape(self):
        """Test that invalid color shape raises error."""
        with pytest.raises(ValueError, match="must be RGB triplet"):
            ContourStyle([(1.0, 0.0)], [(0.0, 0.0, 1.0)])  # Only 2 values


class TestGetColors:
    """Test color retrieval."""
    
    def test_get_pos_color_single(self):
        """Test getting positive color with single color."""
        pos_colors = [(1.0, 0.0, 0.0)]
        style = ContourStyle(pos_colors, [(0.0, 0.0, 1.0)])
        
        color = style.get_pos_color(0)
        np.testing.assert_array_almost_equal(color, [1.0, 0.0, 0.0])
        
    def test_get_neg_color_single(self):
        """Test getting negative color with single color."""
        neg_colors = [(0.0, 0.0, 1.0)]
        style = ContourStyle([(1.0, 0.0, 0.0)], neg_colors)
        
        color = style.get_neg_color(0)
        np.testing.assert_array_almost_equal(color, [0.0, 0.0, 1.0])
        
    def test_get_pos_color_cycling(self):
        """Test that positive colors cycle through list."""
        pos_colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        style = ContourStyle(pos_colors, [(0.0, 0.0, 0.0)])
        
        # Test cycling
        np.testing.assert_array_almost_equal(style.get_pos_color(0), [1.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(style.get_pos_color(1), [0.0, 1.0, 0.0])
        np.testing.assert_array_almost_equal(style.get_pos_color(2), [0.0, 0.0, 1.0])
        np.testing.assert_array_almost_equal(style.get_pos_color(3), [1.0, 0.0, 0.0])  # Cycles
        np.testing.assert_array_almost_equal(style.get_pos_color(4), [0.0, 1.0, 0.0])
        
    def test_get_neg_color_cycling(self):
        """Test that negative colors cycle through list."""
        neg_colors = [(1.0, 1.0, 0.0), (0.0, 1.0, 1.0)]
        style = ContourStyle([(0.0, 0.0, 0.0)], neg_colors)
        
        # Test cycling
        np.testing.assert_array_almost_equal(style.get_neg_color(0), [1.0, 1.0, 0.0])
        np.testing.assert_array_almost_equal(style.get_neg_color(1), [0.0, 1.0, 1.0])
        np.testing.assert_array_almost_equal(style.get_neg_color(2), [1.0, 1.0, 0.0])  # Cycles
        
    def test_get_pos_color_empty(self):
        """Test getting positive color when list is empty."""
        style = ContourStyle([], [(0.0, 0.0, 1.0)])
        
        # Should return default red
        color = style.get_pos_color(0)
        np.testing.assert_array_almost_equal(color, [1.0, 0.0, 0.0])
        
    def test_get_neg_color_empty(self):
        """Test getting negative color when list is empty."""
        style = ContourStyle([(1.0, 0.0, 0.0)], [])
        
        # Should return default blue
        color = style.get_neg_color(0)
        np.testing.assert_array_almost_equal(color, [0.0, 0.0, 1.0])


class TestColorStorage:
    """Test color storage and numpy arrays."""
    
    def test_colors_stored_as_numpy(self):
        """Test that colors are stored as numpy arrays."""
        pos_colors = [(1.0, 0.0, 0.0)]
        style = ContourStyle(pos_colors, [(0.0, 0.0, 1.0)])
        
        assert isinstance(style.pos_colors[0], np.ndarray)
        assert style.pos_colors[0].dtype == np.float32
        
    def test_colors_are_copied(self):
        """Test that modifying input doesn't affect stored colors."""
        pos_list = [(1.0, 0.0, 0.0)]
        style = ContourStyle(pos_list, [(0.0, 0.0, 1.0)])
        
        # Modify input list
        pos_list.append((0.0, 1.0, 0.0))
        
        # Style should still have 1 color
        assert style.npos_colors == 1


class TestRepr:
    """Test string representation."""
    
    def test_repr_basic(self):
        """Test basic repr."""
        style = ContourStyle([(1.0, 0.0, 0.0)], [(0.0, 0.0, 1.0)])
        repr_str = repr(style)
        
        assert "pos=1 colors" in repr_str
        assert "neg=1 colors" in repr_str
        assert "normal" in repr_str
        assert "dashed" in repr_str
        
    def test_repr_multiple_colors(self):
        """Test repr with multiple colors."""
        pos_colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        neg_colors = [(0.0, 0.0, 1.0), (1.0, 1.0, 0.0), (0.0, 1.0, 1.0)]
        style = ContourStyle(pos_colors, neg_colors)
        
        repr_str = repr(style)
        assert "pos=2 colors" in repr_str
        assert "neg=3 colors" in repr_str
        
    def test_repr_custom_styles(self):
        """Test repr with custom line styles."""
        style = ContourStyle([(1.0, 0.0, 0.0)], [(0.0, 0.0, 1.0)],
                           pos_line_style=DASHED_LINE_STYLE,
                           neg_line_style=NORMAL_LINE_STYLE)
        
        repr_str = repr(style)
        # Should show pos as dashed, neg as normal
        assert "dashed" in repr_str
        assert "normal" in repr_str


class TestCAPIFunctions:
    """Test C API compatibility functions."""
    
    def test_new_contour_style(self):
        """Test new_contour_style function."""
        pos_colors = [(1.0, 0.0, 0.0)]
        neg_colors = [(0.0, 0.0, 1.0)]
        
        style = new_contour_style(pos_colors, neg_colors)
        
        assert isinstance(style, ContourStyle)
        assert style.npos_colors == 1
        assert style.nneg_colors == 1
        
    def test_new_contour_style_with_styles(self):
        """Test new_contour_style with custom line styles."""
        style = new_contour_style(
            [(1.0, 0.0, 0.0)],
            [(0.0, 0.0, 1.0)],
            pos_line_style=DASHED_LINE_STYLE,
            neg_line_style=NORMAL_LINE_STYLE
        )
        
        assert style.pos_line_style == DASHED_LINE_STYLE
        assert style.neg_line_style == NORMAL_LINE_STYLE
        
    def test_delete_contour_style(self):
        """Test delete_contour_style function."""
        style = new_contour_style([(1.0, 0.0, 0.0)], [(0.0, 0.0, 1.0)])
        delete_contour_style(style)  # Should not error


class TestTypicalUsage:
    """Test typical NMR contour styling scenarios."""
    
    def test_standard_positive_negative_style(self):
        """Test standard positive (red, solid) and negative (blue, dashed)."""
        style = ContourStyle(
            pos_colors=[(1.0, 0.0, 0.0)],  # Red
            neg_colors=[(0.0, 0.0, 1.0)],  # Blue
            pos_line_style=NORMAL_LINE_STYLE,
            neg_line_style=DASHED_LINE_STYLE
        )
        
        # Positive: red, solid
        pos_color = style.get_pos_color(0)
        np.testing.assert_array_almost_equal(pos_color, [1.0, 0.0, 0.0])
        assert style.pos_line_style == NORMAL_LINE_STYLE
        
        # Negative: blue, dashed
        neg_color = style.get_neg_color(0)
        np.testing.assert_array_almost_equal(neg_color, [0.0, 0.0, 1.0])
        assert style.neg_line_style == DASHED_LINE_STYLE
        
    def test_multi_color_gradient(self):
        """Test gradient from red through orange to yellow."""
        pos_colors = [
            (1.0, 0.0, 0.0),  # Red
            (1.0, 0.5, 0.0),  # Orange
            (1.0, 1.0, 0.0),  # Yellow
        ]
        style = ContourStyle(pos_colors, [(0.0, 0.0, 1.0)])
        
        assert style.npos_colors == 3
        # Should cycle through gradient
        for i in range(6):
            color = style.get_pos_color(i)
            expected_idx = i % 3
            np.testing.assert_array_almost_equal(color, pos_colors[expected_idx])
            
    def test_hsqc_style(self):
        """Test typical HSQC spectrum styling (black/red)."""
        style = ContourStyle(
            pos_colors=[(0.0, 0.0, 0.0)],  # Black
            neg_colors=[(1.0, 0.0, 0.0)],  # Red
            pos_line_style=NORMAL_LINE_STYLE,
            neg_line_style=NORMAL_LINE_STYLE  # Both solid
        )
        
        pos = style.get_pos_color(0)
        neg = style.get_neg_color(0)
        
        np.testing.assert_array_almost_equal(pos, [0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(neg, [1.0, 0.0, 0.0])
        assert style.pos_line_style == NORMAL_LINE_STYLE
        assert style.neg_line_style == NORMAL_LINE_STYLE


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_zero_zero_color(self):
        """Test black color (0, 0, 0)."""
        style = ContourStyle([(0.0, 0.0, 0.0)], [(0.0, 0.0, 0.0)])
        
        pos = style.get_pos_color(0)
        np.testing.assert_array_almost_equal(pos, [0.0, 0.0, 0.0])
        
    def test_one_one_one_color(self):
        """Test white color (1, 1, 1)."""
        style = ContourStyle([(1.0, 1.0, 1.0)], [(1.0, 1.0, 1.0)])
        
        pos = style.get_pos_color(0)
        np.testing.assert_array_almost_equal(pos, [1.0, 1.0, 1.0])
        
    def test_large_index(self):
        """Test color cycling with large index."""
        pos_colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        style = ContourStyle(pos_colors, [(0.0, 0.0, 1.0)])
        
        # Index 100 should cycle correctly
        color = style.get_pos_color(100)
        expected = pos_colors[100 % 2]  # Should be (1.0, 0.0, 0.0)
        np.testing.assert_array_almost_equal(color, expected)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
