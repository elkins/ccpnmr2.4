"""
Pure Python implementation of color utilities.

This module implements color conversion and manipulation functions used
in the original C code (color.c) for NMR visualization.

The primary function calculates an inverted grey color suitable for
contrasting with a given RGB color, useful for overlaying text or
graphics on colored backgrounds.

Author: CCPN Team
License: LGPL
"""


def inverted_grey_color(rgb):
    """
    Calculate an inverted grey color for contrast against a given RGB color.
    
    This function computes a perceptually-weighted luminance from the RGB values,
    then applies a contrast inversion algorithm to ensure the grey value provides
    good visual contrast. This is useful for determining text colors that will be
    readable on colored backgrounds.
    
    The algorithm uses perceptual weights:
    - Red: 0.35 (lower sensitivity)
    - Green: 0.50 (highest sensitivity)
    - Blue: 0.15 (lowest sensitivity)
    
    Then applies contrast rules:
    - Very dark (< 0.25): Use bright (1 - m)
    - Dark-mid (0.25-0.5): Use brighter (m + 0.5)
    - Mid-bright (0.5-0.75): Use darker (m - 0.5)
    - Very bright (>= 0.75): Use dark (1 - m)
    
    Args:
        rgb: RGB color as tuple/list [r, g, b] with values in [0, 1]
        
    Returns:
        Tuple of (grey, grey, grey) representing the inverted grey color
        
    Example:
        >>> inverted_grey_color([0.0, 0.0, 0.0])  # Black background
        (0.75, 0.75, 0.75)  # Light grey text
        >>> inverted_grey_color([1.0, 1.0, 1.0])  # White background
        (0.0, 0.0, 0.0)  # Black text
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    
    # Calculate perceptually-weighted luminance
    # Green dominates human perception, red less so, blue least
    m = 0.35 * r + 0.5 * g + 0.15 * b
    
    # Apply contrast inversion based on luminance level
    if m < 0.25:
        # Very dark: invert to bright
        m = 1.0 - m
    elif m < 0.5:
        # Dark-mid: shift brighter
        m = m + 0.5
    elif m < 0.75:
        # Mid-bright: shift darker
        m = m - 0.5
    else:
        # Very bright: invert to dark
        m = 1.0 - m
    
    return (m, m, m)


def rgb_to_hex(rgb):
    """
    Convert RGB color to hexadecimal string.
    
    Args:
        rgb: RGB color as tuple/list [r, g, b] with values in [0, 1]
        
    Returns:
        Hex color string like "#FF00AA"
    """
    r = int(rgb[0] * 255)
    g = int(rgb[1] * 255)
    b = int(rgb[2] * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_color):
    """
    Convert hexadecimal color string to RGB.
    
    Args:
        hex_color: Hex string like "#FF00AA" or "FF00AA"
        
    Returns:
        Tuple (r, g, b) with values in [0, 1]
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Parse hex values
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    return (r, g, b)


def rgb_to_hsv(rgb):
    """
    Convert RGB to HSV color space.
    
    HSV (Hue, Saturation, Value) is often more intuitive for color manipulation.
    
    Args:
        rgb: RGB color as tuple/list [r, g, b] with values in [0, 1]
        
    Returns:
        Tuple (h, s, v) where:
        - h: Hue in [0, 360) degrees
        - s: Saturation in [0, 1]
        - v: Value (brightness) in [0, 1]
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    delta = max_val - min_val
    
    # Value is the maximum
    v = max_val
    
    # Saturation
    if max_val == 0:
        s = 0
    else:
        s = delta / max_val
    
    # Hue
    if delta == 0:
        h = 0  # Achromatic (grey)
    elif max_val == r:
        h = 60 * (((g - b) / delta) % 6)
    elif max_val == g:
        h = 60 * (((b - r) / delta) + 2)
    else:  # max_val == b
        h = 60 * (((r - g) / delta) + 4)
    
    return (h, s, v)


def hsv_to_rgb(hsv):
    """
    Convert HSV to RGB color space.
    
    Args:
        hsv: HSV color as tuple/list [h, s, v] where:
            - h: Hue in [0, 360) degrees
            - s: Saturation in [0, 1]
            - v: Value in [0, 1]
            
    Returns:
        Tuple (r, g, b) with values in [0, 1]
    """
    h, s, v = hsv[0], hsv[1], hsv[2]
    
    if s == 0:
        # Achromatic (grey)
        return (v, v, v)
    
    h = h / 60.0  # Sector 0 to 5
    i = int(h)
    f = h - i  # Fractional part
    
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    
    if i == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    else:  # i == 5
        return (v, p, q)


def luminance(rgb):
    """
    Calculate perceptual luminance of an RGB color.
    
    Uses the same weights as inverted_grey_color for consistency.
    
    Args:
        rgb: RGB color as tuple/list [r, g, b] with values in [0, 1]
        
    Returns:
        Luminance value in [0, 1]
    """
    return 0.35 * rgb[0] + 0.5 * rgb[1] + 0.15 * rgb[2]


class ColorOps:
    """
    Wrapper class for color operations.
    
    Provides a convenient interface for color conversions and manipulations.
    """
    
    @staticmethod
    def inverted_grey(rgb):
        """Calculate inverted grey color for contrast."""
        return inverted_grey_color(rgb)
    
    @staticmethod
    def to_hex(rgb):
        """Convert RGB to hex string."""
        return rgb_to_hex(rgb)
    
    @staticmethod
    def from_hex(hex_color):
        """Convert hex string to RGB."""
        return hex_to_rgb(hex_color)
    
    @staticmethod
    def to_hsv(rgb):
        """Convert RGB to HSV."""
        return rgb_to_hsv(rgb)
    
    @staticmethod
    def from_hsv(hsv):
        """Convert HSV to RGB."""
        return hsv_to_rgb(hsv)
    
    @staticmethod
    def get_luminance(rgb):
        """Calculate perceptual luminance."""
        return luminance(rgb)
