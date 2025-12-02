"""
Tests for symbol module.

Tests the peak symbol drawing functions.
"""

import pytest
from ccpnmr.analysis.python_impl.symbol import (
    draw_symbol, draw_cross, draw_plus, draw_circle, draw_disk, draw_box,
    SymbolType, CROSS_SYMBOL, PLUS_SYMBOL, CIRCLE_SYMBOL, DISK_SYMBOL, BOX_SYMBOL,
    DEFAULT_SYMBOL, NUMBER_SYMBOLS, NORMAL_LINE_STYLE, DASHED_LINE_STYLE
)


class DrawingRecorder:
    """Mock drawing functions that record calls."""
    
    def __init__(self):
        self.lines = []
        self.ellipses = []
        self.filled_ellipses = []
        self.line_styles = []
        
    def draw_line(self, data, x1, y1, x2, y2):
        """Record line drawing."""
        self.lines.append((x1, y1, x2, y2))
        
    def draw_ellipse(self, data, x, y, rx, ry):
        """Record ellipse drawing."""
        self.ellipses.append((x, y, rx, ry))
        
    def fill_ellipse(self, data, x, y, rx, ry):
        """Record filled ellipse drawing."""
        self.filled_ellipses.append((x, y, rx, ry))
        
    def set_line_style(self, data, style):
        """Record line style changes."""
        self.line_styles.append(style)
        
    def get_funcs(self):
        """Get drawing functions dictionary."""
        return {
            'draw_line': self.draw_line,
            'draw_ellipse': self.draw_ellipse,
            'fill_ellipse': self.fill_ellipse,
            'set_line_style': self.set_line_style
        }
        
    def reset(self):
        """Clear all recorded calls."""
        self.lines.clear()
        self.ellipses.clear()
        self.filled_ellipses.clear()
        self.line_styles.clear()


class TestSymbolConstants:
    """Test symbol type constants."""
    
    def test_symbol_values(self):
        """Test that symbol constants have correct values."""
        assert CROSS_SYMBOL == 0
        assert PLUS_SYMBOL == 1
        assert CIRCLE_SYMBOL == 2
        assert DISK_SYMBOL == 3
        assert BOX_SYMBOL == 4
        
    def test_default_symbol(self):
        """Test default symbol is CROSS."""
        assert DEFAULT_SYMBOL == CROSS_SYMBOL
        
    def test_number_symbols(self):
        """Test number of symbols constant."""
        assert NUMBER_SYMBOLS == 5
        
    def test_line_styles(self):
        """Test line style constants."""
        assert NORMAL_LINE_STYLE == 0
        assert DASHED_LINE_STYLE == 1
        
    def test_symbol_type_enum(self):
        """Test SymbolType enum."""
        assert SymbolType.CROSS == 0
        assert SymbolType.PLUS == 1
        assert SymbolType.CIRCLE == 2
        assert SymbolType.DISK == 3
        assert SymbolType.BOX == 4


class TestDrawCross:
    """Test cross symbol drawing."""
    
    def test_draw_cross_basic(self):
        """Test basic cross drawing."""
        recorder = DrawingRecorder()
        draw_cross(10.0, 20.0, 1.0, 1.0, recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2
        # First diagonal: (9, 19) to (11, 21)
        assert recorder.lines[0] == (9.0, 19.0, 11.0, 21.0)
        # Second diagonal: (9, 21) to (11, 19)
        assert recorder.lines[1] == (9.0, 21.0, 11.0, 19.0)
        
    def test_draw_cross_scaled(self):
        """Test cross with scaling."""
        recorder = DrawingRecorder()
        draw_cross(0.0, 0.0, 2.0, 3.0, recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2
        # Scale: dx=2.0, dy=3.0
        assert recorder.lines[0] == (-2.0, -3.0, 2.0, 3.0)
        assert recorder.lines[1] == (-2.0, 3.0, 2.0, -3.0)


class TestDrawPlus:
    """Test plus symbol drawing."""
    
    def test_draw_plus_basic(self):
        """Test basic plus drawing."""
        recorder = DrawingRecorder()
        draw_plus(10.0, 20.0, 1.0, 1.0, recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2
        # Vertical: (10, 19) to (10, 21)
        assert recorder.lines[0] == (10.0, 19.0, 10.0, 21.0)
        # Horizontal: (9, 20) to (11, 20)
        assert recorder.lines[1] == (9.0, 20.0, 11.0, 20.0)
        
    def test_draw_plus_scaled(self):
        """Test plus with scaling."""
        recorder = DrawingRecorder()
        draw_plus(0.0, 0.0, 2.0, 3.0, recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2
        assert recorder.lines[0] == (0.0, -3.0, 0.0, 3.0)  # Vertical
        assert recorder.lines[1] == (-2.0, 0.0, 2.0, 0.0)  # Horizontal


class TestDrawCircle:
    """Test circle symbol drawing."""
    
    def test_draw_circle_basic(self):
        """Test basic circle drawing."""
        recorder = DrawingRecorder()
        draw_circle(10.0, 20.0, 1.0, 1.0, recorder.get_funcs(), None)
        
        assert len(recorder.ellipses) == 1
        assert recorder.ellipses[0] == (10.0, 20.0, 1.0, 1.0)
        
    def test_draw_circle_scaled(self):
        """Test circle with anisotropic scaling."""
        recorder = DrawingRecorder()
        draw_circle(5.0, 10.0, 2.0, 3.0, recorder.get_funcs(), None)
        
        assert len(recorder.ellipses) == 1
        assert recorder.ellipses[0] == (5.0, 10.0, 2.0, 3.0)


class TestDrawDisk:
    """Test disk symbol drawing."""
    
    def test_draw_disk_basic(self):
        """Test basic disk drawing."""
        recorder = DrawingRecorder()
        draw_disk(10.0, 20.0, 1.0, 1.0, recorder.get_funcs(), None)
        
        assert len(recorder.filled_ellipses) == 1
        assert recorder.filled_ellipses[0] == (10.0, 20.0, 1.0, 1.0)
        
    def test_draw_disk_scaled(self):
        """Test disk with anisotropic scaling."""
        recorder = DrawingRecorder()
        draw_disk(5.0, 10.0, 2.0, 3.0, recorder.get_funcs(), None)
        
        assert len(recorder.filled_ellipses) == 1
        assert recorder.filled_ellipses[0] == (5.0, 10.0, 2.0, 3.0)


class TestDrawBox:
    """Test box symbol drawing."""
    
    def test_draw_box_basic(self):
        """Test basic box drawing."""
        recorder = DrawingRecorder()
        draw_box(10.0, 20.0, 1.0, 1.0, recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 4
        # Four sides of rectangle
        assert recorder.lines[0] == (9.0, 19.0, 11.0, 19.0)   # Bottom
        assert recorder.lines[1] == (11.0, 19.0, 11.0, 21.0)  # Right
        assert recorder.lines[2] == (11.0, 21.0, 9.0, 21.0)   # Top
        assert recorder.lines[3] == (9.0, 21.0, 9.0, 19.0)    # Left
        
    def test_draw_box_scaled(self):
        """Test box with scaling."""
        recorder = DrawingRecorder()
        draw_box(0.0, 0.0, 2.0, 3.0, recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 4
        assert recorder.lines[0] == (-2.0, -3.0, 2.0, -3.0)   # Bottom
        assert recorder.lines[1] == (2.0, -3.0, 2.0, 3.0)     # Right
        assert recorder.lines[2] == (2.0, 3.0, -2.0, 3.0)     # Top
        assert recorder.lines[3] == (-2.0, 3.0, -2.0, -3.0)   # Left


class TestDrawSymbol:
    """Test main draw_symbol function."""
    
    def test_draw_symbol_cross(self):
        """Test drawing CROSS symbol."""
        recorder = DrawingRecorder()
        draw_symbol(CROSS_SYMBOL, 10.0, 20.0, 1.0, 1.0, False, 
                   recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2  # Cross has 2 lines
        assert len(recorder.line_styles) == 0  # No aliasing
        
    def test_draw_symbol_plus(self):
        """Test drawing PLUS symbol."""
        recorder = DrawingRecorder()
        draw_symbol(PLUS_SYMBOL, 10.0, 20.0, 1.0, 1.0, False,
                   recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2  # Plus has 2 lines
        
    def test_draw_symbol_circle(self):
        """Test drawing CIRCLE symbol."""
        recorder = DrawingRecorder()
        draw_symbol(CIRCLE_SYMBOL, 10.0, 20.0, 1.0, 1.0, False,
                   recorder.get_funcs(), None)
        
        assert len(recorder.ellipses) == 1
        
    def test_draw_symbol_disk(self):
        """Test drawing DISK symbol."""
        recorder = DrawingRecorder()
        draw_symbol(DISK_SYMBOL, 10.0, 20.0, 1.0, 1.0, False,
                   recorder.get_funcs(), None)
        
        assert len(recorder.filled_ellipses) == 1
        
    def test_draw_symbol_box(self):
        """Test drawing BOX symbol."""
        recorder = DrawingRecorder()
        draw_symbol(BOX_SYMBOL, 10.0, 20.0, 1.0, 1.0, False,
                   recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 4  # Box has 4 lines
        
    def test_draw_symbol_aliased(self):
        """Test drawing aliased symbol with dashed lines."""
        recorder = DrawingRecorder()
        draw_symbol(CROSS_SYMBOL, 10.0, 20.0, 1.0, 1.0, True,
                   recorder.get_funcs(), None)
        
        assert len(recorder.lines) == 2
        # Should set dashed, then restore normal
        assert len(recorder.line_styles) == 2
        assert recorder.line_styles[0] == DASHED_LINE_STYLE
        assert recorder.line_styles[1] == NORMAL_LINE_STYLE
        
    def test_draw_symbol_not_aliased(self):
        """Test drawing non-aliased symbol."""
        recorder = DrawingRecorder()
        draw_symbol(CROSS_SYMBOL, 10.0, 20.0, 1.0, 1.0, False,
                   recorder.get_funcs(), None)
        
        # Should not change line style
        assert len(recorder.line_styles) == 0
        
    def test_draw_symbol_invalid(self):
        """Test drawing with invalid symbol type."""
        recorder = DrawingRecorder()
        draw_symbol(999, 10.0, 20.0, 1.0, 1.0, False,
                   recorder.get_funcs(), None)
        
        # Should not draw anything
        assert len(recorder.lines) == 0
        assert len(recorder.ellipses) == 0
        assert len(recorder.filled_ellipses) == 0


class TestSymbolIntegration:
    """Test symbols in realistic scenarios."""
    
    def test_multiple_symbols(self):
        """Test drawing multiple different symbols."""
        recorder = DrawingRecorder()
        funcs = recorder.get_funcs()
        
        # Draw all symbol types
        draw_symbol(CROSS_SYMBOL, 0.0, 0.0, 1.0, 1.0, False, funcs, None)
        draw_symbol(PLUS_SYMBOL, 5.0, 5.0, 1.0, 1.0, False, funcs, None)
        draw_symbol(CIRCLE_SYMBOL, 10.0, 10.0, 1.0, 1.0, False, funcs, None)
        draw_symbol(DISK_SYMBOL, 15.0, 15.0, 1.0, 1.0, False, funcs, None)
        draw_symbol(BOX_SYMBOL, 20.0, 20.0, 1.0, 1.0, False, funcs, None)
        
        # Should have lines from cross, plus, and box
        assert len(recorder.lines) == 2 + 2 + 4  # 8 total
        # Circle and disk
        assert len(recorder.ellipses) == 1
        assert len(recorder.filled_ellipses) == 1
        
    def test_mixed_aliasing(self):
        """Test mixture of aliased and non-aliased symbols."""
        recorder = DrawingRecorder()
        funcs = recorder.get_funcs()
        
        draw_symbol(CROSS_SYMBOL, 0.0, 0.0, 1.0, 1.0, False, funcs, None)
        draw_symbol(CROSS_SYMBOL, 5.0, 5.0, 1.0, 1.0, True, funcs, None)
        draw_symbol(CROSS_SYMBOL, 10.0, 10.0, 1.0, 1.0, False, funcs, None)
        
        # Three crosses = 6 lines
        assert len(recorder.lines) == 6
        # Only middle one sets line style (2 calls: dashed + normal)
        assert len(recorder.line_styles) == 2
        
    def test_different_scales(self):
        """Test symbols with different scale factors."""
        recorder = DrawingRecorder()
        funcs = recorder.get_funcs()
        
        # Small scale
        draw_symbol(CROSS_SYMBOL, 0.0, 0.0, 0.5, 0.5, False, funcs, None)
        # Large scale
        draw_symbol(CROSS_SYMBOL, 10.0, 10.0, 3.0, 2.0, False, funcs, None)
        
        assert len(recorder.lines) == 4
        # First cross: scale 0.5
        assert recorder.lines[0] == (-0.5, -0.5, 0.5, 0.5)
        # Second cross: scale 3.0, 2.0
        assert recorder.lines[2] == (7.0, 8.0, 13.0, 12.0)


class TestMissingDrawingFunctions:
    """Test behavior when drawing functions are missing."""
    
    def test_missing_draw_line(self):
        """Test cross with missing draw_line."""
        funcs = {}  # Empty - no functions
        # Should not crash
        draw_cross(10.0, 20.0, 1.0, 1.0, funcs, None)
        
    def test_missing_draw_ellipse(self):
        """Test circle with missing draw_ellipse."""
        funcs = {}
        # Should not crash
        draw_circle(10.0, 20.0, 1.0, 1.0, funcs, None)
        
    def test_missing_fill_ellipse(self):
        """Test disk with missing fill_ellipse."""
        funcs = {}
        # Should not crash
        draw_disk(10.0, 20.0, 1.0, 1.0, funcs, None)
        
    def test_missing_set_line_style(self):
        """Test aliased symbol with missing set_line_style."""
        recorder = DrawingRecorder()
        funcs = {'draw_line': recorder.draw_line}  # No set_line_style
        
        # Should draw but not crash on style setting
        draw_symbol(CROSS_SYMBOL, 10.0, 20.0, 1.0, 1.0, True, funcs, None)
        assert len(recorder.lines) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
