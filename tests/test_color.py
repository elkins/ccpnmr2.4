"""
Tests for color.py module

Test coverage:
- inverted_grey_color: Contrast grey calculation
- RGB/HSV conversions: Round-trip correctness
- RGB/Hex conversions: Format validation
- Luminance: Perceptual brightness
- ColorOps class: Wrapper functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.c.python_impl.color import (
    inverted_grey_color,
    rgb_to_hex, hex_to_rgb,
    rgb_to_hsv, hsv_to_rgb,
    luminance,
    ColorOps
)


def test_inverted_grey_color_black():
    """Black should invert to white."""
    result = inverted_grey_color((0.0, 0.0, 0.0))
    assert result == (1.0, 1.0, 1.0), f"Expected white, got {result}"


def test_inverted_grey_color_white():
    """White should invert to black."""
    result = inverted_grey_color((1.0, 1.0, 1.0))
    assert result == (0.0, 0.0, 0.0), f"Expected black, got {result}"


def test_inverted_grey_color_mid():
    """Mid-grey should invert based on perceptual luminance."""
    # RGB (0.5, 0.5, 0.5) has luminance 0.5
    # Algorithm: 0.5 < 0.75 so m = m - 0.5 = 0.0
    result = inverted_grey_color((0.5, 0.5, 0.5))
    expected = (0.0, 0.0, 0.0)
    assert all(abs(a - b) < 0.01 for a, b in zip(result, expected)), \
        f"Expected {expected}, got {result}"


def test_inverted_grey_color_red():
    """Pure red has luminance 0.35, should invert to 0.85."""
    # 0.35 < 0.5, so m = m + 0.5 = 0.85
    result = inverted_grey_color((1.0, 0.0, 0.0))
    expected = (0.85, 0.85, 0.85)
    assert all(abs(a - b) < 0.01 for a, b in zip(result, expected)), \
        f"Expected {expected}, got {result}"


def test_inverted_grey_color_green():
    """Pure green has luminance 0.50, should invert to 0.0."""
    # 0.5 < 0.75, so m = m - 0.5 = 0.0
    result = inverted_grey_color((0.0, 1.0, 0.0))
    expected = (0.0, 0.0, 0.0)
    assert all(abs(a - b) < 0.01 for a, b in zip(result, expected)), \
        f"Expected {expected}, got {result}"


def test_inverted_grey_color_blue():
    """Pure blue has luminance 0.15, should invert to 0.85."""
    result = inverted_grey_color((0.0, 0.0, 1.0))
    expected = (0.85, 0.85, 0.85)
    assert all(abs(a - b) < 0.01 for a, b in zip(result, expected)), \
        f"Expected {expected}, got {result}"


def test_rgb_to_hex():
    """Test RGB to hex conversion."""
    assert rgb_to_hex((1.0, 0.0, 0.0)) == "#FF0000"
    assert rgb_to_hex((0.0, 1.0, 0.0)) == "#00FF00"
    assert rgb_to_hex((0.0, 0.0, 1.0)) == "#0000FF"
    assert rgb_to_hex((1.0, 1.0, 1.0)) == "#FFFFFF"
    assert rgb_to_hex((0.0, 0.0, 0.0)) == "#000000"


def test_hex_to_rgb():
    """Test hex to RGB conversion."""
    r, g, b = hex_to_rgb("#ff0000")
    assert abs(r - 1.0) < 0.01 and abs(g) < 0.01 and abs(b) < 0.01
    
    r, g, b = hex_to_rgb("#00ff00")
    assert abs(r) < 0.01 and abs(g - 1.0) < 0.01 and abs(b) < 0.01
    
    r, g, b = hex_to_rgb("#0000ff")
    assert abs(r) < 0.01 and abs(g) < 0.01 and abs(b - 1.0) < 0.01


def test_rgb_hex_round_trip():
    """Test RGB -> hex -> RGB round trip."""
    colors = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (0.5, 0.5, 0.5),
        (0.2, 0.4, 0.8)
    ]
    
    for rgb in colors:
        hex_str = rgb_to_hex(rgb)
        rgb2 = hex_to_rgb(hex_str)
        assert all(abs(a - b) < 0.01 for a, b in zip(rgb, rgb2)), \
            f"Round trip failed: {rgb} -> {hex_str} -> {rgb2}"


def test_rgb_to_hsv_red():
    """Test RGB to HSV for pure red."""
    h, s, v = rgb_to_hsv((1.0, 0.0, 0.0))
    assert abs(h - 0.0) < 0.01
    assert abs(s - 1.0) < 0.01
    assert abs(v - 1.0) < 0.01


def test_rgb_to_hsv_green():
    """Test RGB to HSV for pure green."""
    h, s, v = rgb_to_hsv((0.0, 1.0, 0.0))
    assert abs(h - 120.0) < 0.01
    assert abs(s - 1.0) < 0.01
    assert abs(v - 1.0) < 0.01


def test_rgb_to_hsv_blue():
    """Test RGB to HSV for pure blue."""
    h, s, v = rgb_to_hsv((0.0, 0.0, 1.0))
    assert abs(h - 240.0) < 0.01
    assert abs(s - 1.0) < 0.01
    assert abs(v - 1.0) < 0.01


def test_rgb_to_hsv_grey():
    """Test RGB to HSV for grey (zero saturation)."""
    h, s, v = rgb_to_hsv((0.5, 0.5, 0.5))
    assert abs(s) < 0.01  # Saturation should be 0
    assert abs(v - 0.5) < 0.01


def test_hsv_to_rgb_red():
    """Test HSV to RGB for pure red."""
    r, g, b = hsv_to_rgb((0.0, 1.0, 1.0))
    assert abs(r - 1.0) < 0.01
    assert abs(g) < 0.01
    assert abs(b) < 0.01


def test_hsv_to_rgb_green():
    """Test HSV to RGB for pure green."""
    r, g, b = hsv_to_rgb((120.0, 1.0, 1.0))
    assert abs(r) < 0.01
    assert abs(g - 1.0) < 0.01
    assert abs(b) < 0.01


def test_rgb_hsv_round_trip():
    """Test RGB -> HSV -> RGB round trip."""
    colors = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (1.0, 1.0, 0.0),
        (0.5, 0.3, 0.8)
    ]
    
    for rgb in colors:
        hsv = rgb_to_hsv(rgb)
        rgb2 = hsv_to_rgb(hsv)
        assert all(abs(a - b) < 0.01 for a, b in zip(rgb, rgb2)), \
            f"Round trip failed: {rgb} -> {hsv} -> {rgb2}"


def test_luminance():
    """Test luminance calculation."""
    assert abs(luminance((1.0, 0.0, 0.0)) - 0.35) < 0.01
    assert abs(luminance((0.0, 1.0, 0.0)) - 0.50) < 0.01
    assert abs(luminance((0.0, 0.0, 1.0)) - 0.15) < 0.01
    assert abs(luminance((1.0, 1.0, 1.0)) - 1.0) < 0.01
    assert abs(luminance((0.0, 0.0, 0.0)) - 0.0) < 0.01


def test_color_ops_class():
    """Test ColorOps wrapper class."""
    ops = ColorOps()
    
    # Test inverted grey
    grey = ops.inverted_grey((0.0, 0.0, 0.0))
    assert grey == (1.0, 1.0, 1.0)
    
    # Test conversions
    hex_str = ops.to_hex((1.0, 0.0, 0.0))
    assert hex_str == "#FF0000"
    
    rgb = ops.from_hex("#ff0000")
    assert abs(rgb[0] - 1.0) < 0.01
    
    hsv = ops.to_hsv((1.0, 0.0, 0.0))
    assert abs(hsv[1] - 1.0) < 0.01
    
    lum = ops.get_luminance((0.5, 0.5, 0.5))
    assert abs(lum - 0.5) < 0.01


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_inverted_grey_color_black,
        test_inverted_grey_color_white,
        test_inverted_grey_color_mid,
        test_inverted_grey_color_red,
        test_inverted_grey_color_green,
        test_inverted_grey_color_blue,
        test_rgb_to_hex,
        test_hex_to_rgb,
        test_rgb_hex_round_trip,
        test_rgb_to_hsv_red,
        test_rgb_to_hsv_green,
        test_rgb_to_hsv_blue,
        test_rgb_to_hsv_grey,
        test_hsv_to_rgb_red,
        test_hsv_to_rgb_green,
        test_rgb_hsv_round_trip,
        test_luminance,
        test_color_ops_class
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Color Tests: {passed} passed, {failed} failed")
    print(f"{'='*60}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
