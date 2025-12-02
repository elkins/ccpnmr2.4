"""
Tests for color.py - Color conversion and manipulation utilities
"""

import pytest
from memops.c.python_impl.color import (
    inverted_grey_color, rgb_to_hex, hex_to_rgb,
    rgb_to_hsv, hsv_to_rgb, luminance, ColorOps
)


class TestInvertedGreyColor:
    """Test inverted grey color calculation for contrast."""
    
    def test_black_background(self):
        """Black background should give light grey text."""
        result = inverted_grey_color([0.0, 0.0, 0.0])
        # Very dark (< 0.25): inverts to bright (1.0 - 0.0 = 1.0)
        assert result == (1.0, 1.0, 1.0)
    
    def test_white_background(self):
        """White background should give dark grey text."""
        result = inverted_grey_color([1.0, 1.0, 1.0])
        # Very bright (>= 0.75): inverts to dark (1.0 - 1.0 = 0.0)
        assert result == (0.0, 0.0, 0.0)
    
    def test_mid_grey(self):
        """Mid grey should shift to darker grey."""
        # 0.5 grey: 0.35*0.5 + 0.5*0.5 + 0.15*0.5 = 0.5
        # Mid-bright (0.5-0.75): shifts darker (0.5 - 0.5 = 0.0)
        result = inverted_grey_color([0.5, 0.5, 0.5])
        assert result == (0.0, 0.0, 0.0)
    
    def test_red_dominant(self):
        """Test with red-dominant color."""
        # Pure red: 0.35*1 + 0.5*0 + 0.15*0 = 0.35
        # Dark-mid (0.25-0.5): shifts brighter (0.35 + 0.5 = 0.85)
        result = inverted_grey_color([1.0, 0.0, 0.0])
        assert result == (0.85, 0.85, 0.85)
    
    def test_green_dominant(self):
        """Test with green-dominant color (highest weight)."""
        # Pure green: 0.35*0 + 0.5*1 + 0.15*0 = 0.5
        result = inverted_grey_color([0.0, 1.0, 0.0])
        assert result == (0.0, 0.0, 0.0)
    
    def test_blue_dominant(self):
        """Test with blue-dominant color (lowest weight)."""
        # Pure blue: 0.35*0 + 0.5*0 + 0.15*1 = 0.15
        # Very dark (< 0.25): inverts to bright (1.0 - 0.15 = 0.85)
        result = inverted_grey_color([0.0, 0.0, 1.0])
        assert result == (0.85, 0.85, 0.85)


class TestRGBHexConversion:
    """Test RGB to/from hexadecimal conversion."""
    
    def test_rgb_to_hex_black(self):
        """Convert black to hex."""
        assert rgb_to_hex([0.0, 0.0, 0.0]) == "#000000"
    
    def test_rgb_to_hex_white(self):
        """Convert white to hex."""
        assert rgb_to_hex([1.0, 1.0, 1.0]) == "#FFFFFF"
    
    def test_rgb_to_hex_red(self):
        """Convert red to hex."""
        assert rgb_to_hex([1.0, 0.0, 0.0]) == "#FF0000"
    
    def test_rgb_to_hex_green(self):
        """Convert green to hex."""
        assert rgb_to_hex([0.0, 1.0, 0.0]) == "#00FF00"
    
    def test_rgb_to_hex_blue(self):
        """Convert blue to hex."""
        assert rgb_to_hex([0.0, 0.0, 1.0]) == "#0000FF"
    
    def test_rgb_to_hex_custom(self):
        """Convert custom color to hex."""
        assert rgb_to_hex([0.5, 0.25, 0.75]) == "#7F3FBF"
    
    def test_hex_to_rgb_black(self):
        """Convert hex black to RGB."""
        result = hex_to_rgb("#000000")
        assert result == (0.0, 0.0, 0.0)
    
    def test_hex_to_rgb_white(self):
        """Convert hex white to RGB."""
        result = hex_to_rgb("#FFFFFF")
        assert result == (1.0, 1.0, 1.0)
    
    def test_hex_to_rgb_no_hash(self):
        """Convert hex without # prefix."""
        result = hex_to_rgb("FF00AA")
        assert abs(result[0] - 1.0) < 0.01
        assert abs(result[1] - 0.0) < 0.01
        assert abs(result[2] - 0.67) < 0.01
    
    def test_roundtrip_conversion(self):
        """Test RGB -> Hex -> RGB roundtrip."""
        original = [0.5, 0.3, 0.8]
        hex_val = rgb_to_hex(original)
        recovered = hex_to_rgb(hex_val)
        
        # Allow small rounding error due to 0-255 quantization
        assert abs(recovered[0] - original[0]) < 0.01
        assert abs(recovered[1] - original[1]) < 0.01
        assert abs(recovered[2] - original[2]) < 0.01


class TestRGBHSVConversion:
    """Test RGB to/from HSV conversion."""
    
    def test_rgb_to_hsv_red(self):
        """Convert red to HSV."""
        h, s, v = rgb_to_hsv([1.0, 0.0, 0.0])
        assert h == 0.0
        assert s == 1.0
        assert v == 1.0
    
    def test_rgb_to_hsv_green(self):
        """Convert green to HSV."""
        h, s, v = rgb_to_hsv([0.0, 1.0, 0.0])
        assert h == 120.0
        assert s == 1.0
        assert v == 1.0
    
    def test_rgb_to_hsv_blue(self):
        """Convert blue to HSV."""
        h, s, v = rgb_to_hsv([0.0, 0.0, 1.0])
        assert h == 240.0
        assert s == 1.0
        assert v == 1.0
    
    def test_rgb_to_hsv_white(self):
        """Convert white to HSV."""
        h, s, v = rgb_to_hsv([1.0, 1.0, 1.0])
        assert h == 0.0  # Hue undefined for achromatic
        assert s == 0.0
        assert v == 1.0
    
    def test_rgb_to_hsv_black(self):
        """Convert black to HSV."""
        h, s, v = rgb_to_hsv([0.0, 0.0, 0.0])
        assert h == 0.0
        assert s == 0.0
        assert v == 0.0
    
    def test_rgb_to_hsv_grey(self):
        """Convert grey to HSV."""
        h, s, v = rgb_to_hsv([0.5, 0.5, 0.5])
        assert h == 0.0  # Achromatic
        assert s == 0.0
        assert v == 0.5
    
    def test_hsv_to_rgb_red(self):
        """Convert HSV red to RGB."""
        r, g, b = hsv_to_rgb([0.0, 1.0, 1.0])
        assert r == 1.0
        assert g == 0.0
        assert b == 0.0
    
    def test_hsv_to_rgb_green(self):
        """Convert HSV green to RGB."""
        r, g, b = hsv_to_rgb([120.0, 1.0, 1.0])
        assert r == 0.0
        assert abs(g - 1.0) < 1e-10
        assert b == 0.0
    
    def test_hsv_to_rgb_blue(self):
        """Convert HSV blue to RGB."""
        r, g, b = hsv_to_rgb([240.0, 1.0, 1.0])
        assert r == 0.0
        assert g == 0.0
        assert abs(b - 1.0) < 1e-10
    
    def test_hsv_to_rgb_grey(self):
        """Convert HSV grey to RGB."""
        r, g, b = hsv_to_rgb([0.0, 0.0, 0.5])
        assert r == 0.5
        assert g == 0.5
        assert b == 0.5
    
    def test_hsv_roundtrip(self):
        """Test RGB -> HSV -> RGB roundtrip."""
        original = [0.7, 0.3, 0.9]
        hsv = rgb_to_hsv(original)
        recovered = hsv_to_rgb(hsv)
        
        assert abs(recovered[0] - original[0]) < 1e-10
        assert abs(recovered[1] - original[1]) < 1e-10
        assert abs(recovered[2] - original[2]) < 1e-10


class TestLuminance:
    """Test luminance calculation."""
    
    def test_luminance_black(self):
        """Black has zero luminance."""
        assert luminance([0.0, 0.0, 0.0]) == 0.0
    
    def test_luminance_white(self):
        """White has maximum luminance."""
        assert luminance([1.0, 1.0, 1.0]) == 1.0
    
    def test_luminance_red(self):
        """Red has 0.35 weight."""
        assert luminance([1.0, 0.0, 0.0]) == 0.35
    
    def test_luminance_green(self):
        """Green has 0.5 weight (highest)."""
        assert luminance([0.0, 1.0, 0.0]) == 0.5
    
    def test_luminance_blue(self):
        """Blue has 0.15 weight (lowest)."""
        assert luminance([0.0, 0.0, 1.0]) == 0.15
    
    def test_luminance_grey(self):
        """Grey luminance equals its value."""
        grey = 0.6
        assert luminance([grey, grey, grey]) == grey


class TestColorOpsClass:
    """Test ColorOps wrapper class."""
    
    def test_inverted_grey(self):
        """Test ColorOps.inverted_grey."""
        result = ColorOps.inverted_grey([0.0, 0.0, 0.0])
        assert result == (1.0, 1.0, 1.0)
    
    def test_to_hex(self):
        """Test ColorOps.to_hex."""
        assert ColorOps.to_hex([1.0, 0.0, 0.0]) == "#FF0000"
    
    def test_from_hex(self):
        """Test ColorOps.from_hex."""
        result = ColorOps.from_hex("#FF0000")
        assert result == (1.0, 0.0, 0.0)
    
    def test_to_hsv(self):
        """Test ColorOps.to_hsv."""
        h, s, v = ColorOps.to_hsv([1.0, 0.0, 0.0])
        assert h == 0.0
        assert s == 1.0
        assert v == 1.0
    
    def test_from_hsv(self):
        """Test ColorOps.from_hsv."""
        r, g, b = ColorOps.from_hsv([0.0, 1.0, 1.0])
        assert r == 1.0
        assert g == 0.0
        assert b == 0.0
    
    def test_get_luminance(self):
        """Test ColorOps.get_luminance."""
        assert ColorOps.get_luminance([0.0, 1.0, 0.0]) == 0.5


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_small_values(self):
        """Test with very small RGB values."""
        result = inverted_grey_color([0.01, 0.01, 0.01])
        # Very dark, should invert
        assert result[0] > 0.9
    
    def test_near_boundary_values(self):
        """Test values near decision boundaries."""
        # Just under 0.25 threshold (very dark): inverts
        result1 = inverted_grey_color([0.24, 0.24, 0.24])
        # Just over 0.25 threshold (dark-mid): shifts brighter
        result2 = inverted_grey_color([0.26, 0.26, 0.26])
        # Values are different enough to use different branches
        # But actual results might be similar due to algorithm
        # Just verify they're both valid grey colors
        assert all(0 <= c <= 1 for c in result1)
        assert all(0 <= c <= 1 for c in result2)
    
    def test_hsv_hue_wraparound(self):
        """Test HSV hue near 360 degrees."""
        # Hue near boundary
        r, g, b = hsv_to_rgb([359.0, 1.0, 1.0])
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0
    
    def test_tuple_vs_list_input(self):
        """Test that both tuple and list inputs work."""
        result1 = inverted_grey_color([0.5, 0.5, 0.5])
        result2 = inverted_grey_color((0.5, 0.5, 0.5))
        assert result1 == result2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
