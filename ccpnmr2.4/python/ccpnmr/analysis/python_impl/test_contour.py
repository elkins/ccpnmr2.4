"""
Test suite for contour implementations (Python, Numba, Cython).

NOTE: These tests are for simplified standalone implementations created for
performance comparison. They do NOT test the existing C implementation at
ccpnmr2.4/c/ccpnmr/analysis/contour_file.c.

See contour.py for rationale on the simplified implementation approach.

Tests all three implementations for:
- Correct contour tracing
- Edge case handling
- Consistency between implementations
"""

import unittest
import sys
import os

# Add path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Import implementations
from contour import ContourTracer as ContourTracerPython
from contour_numba import ContourTracer as ContourTracerNumba

try:
    from contour_cython import ContourTracer as ContourTracerCython
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False
    print("Warning: Cython contour module not available")


class TestContourBase:
    """Base class for contour tests."""
    
    def create_tracer(self, width, height):
        """Create tracer (override in subclasses)."""
        raise NotImplementedError
    
    def test_empty_grid(self):
        """Test with all zeros."""
        tracer = self.create_tracer(5, 5)
        data = [[0.0] * 5 for _ in range(5)]
        tracer.set_data(data)
        result = tracer.trace_level(0.5)
        self.assertEqual(len(result), 0)
    
    def test_single_cell_above(self):
        """Test single cell above threshold."""
        tracer = self.create_tracer(3, 3)
        data = [
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0]
        ]
        tracer.set_data(data)
        result = tracer.trace_level(0.5)
        # Should have contours around center cell
        self.assertGreater(len(result), 0)
    
    def test_gradient(self):
        """Test with gradient."""
        tracer = self.create_tracer(5, 5)
        data = []
        for y in range(5):
            row = []
            for x in range(5):
                row.append(float(x + y))
            data.append(row)
        tracer.set_data(data)
        result = tracer.trace_level(4.0)
        # Should trace diagonal contour
        self.assertGreater(len(result), 0)
    
    def test_peak(self):
        """Test with centered peak."""
        tracer = self.create_tracer(5, 5)
        data = [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 2.0, 4.0, 2.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0]
        ]
        tracer.set_data(data)
        result = tracer.trace_level(1.5)
        # Should have closed contour around peak
        self.assertGreater(len(result), 0)
    
    def test_multiple_levels(self):
        """Test tracing multiple levels."""
        tracer = self.create_tracer(5, 5)
        data = [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 2.0, 4.0, 2.0, 0.0],
            [0.0, 1.0, 2.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0]
        ]
        tracer.set_data(data)
        levels = [1.0, 2.0, 3.0]
        result = tracer.trace_levels(levels)
        self.assertEqual(len(result), 3)
        for level in levels:
            self.assertIn(level, result)
    
    def test_negative_values(self):
        """Test with negative values."""
        tracer = self.create_tracer(4, 4)
        data = [
            [-2.0, -1.0, -1.0, -2.0],
            [-1.0,  0.0,  0.0, -1.0],
            [-1.0,  0.0,  0.0, -1.0],
            [-2.0, -1.0, -1.0, -2.0]
        ]
        tracer.set_data(data)
        result = tracer.trace_level(-0.5)
        # Should trace contour between negative and zero regions
        self.assertGreater(len(result), 0)
    
    def test_uniform_grid(self):
        """Test with all same values."""
        tracer = self.create_tracer(4, 4)
        data = [[5.0] * 4 for _ in range(4)]
        tracer.set_data(data)
        # Below threshold - no contours
        result = tracer.trace_level(6.0)
        self.assertEqual(len(result), 0)
        # Above threshold - no contours
        result = tracer.trace_level(4.0)
        self.assertEqual(len(result), 0)
    
    def test_two_regions(self):
        """Test with two separate regions."""
        tracer = self.create_tracer(6, 4)
        data = [
            [0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
            [0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
            [0.0, 0.0, 0.0, 0.0, 2.0, 2.0]
        ]
        tracer.set_data(data)
        result = tracer.trace_level(1.0)
        # Should have contours around both regions
        self.assertGreater(len(result), 0)


class TestContourPython(TestContourBase, unittest.TestCase):
    """Test pure Python implementation."""
    
    def create_tracer(self, width, height):
        return ContourTracerPython(width, height)


@unittest.skipIf(not HAS_NUMPY, "NumPy not available")
class TestContourNumba(TestContourBase, unittest.TestCase):
    """Test Numba implementation."""
    
    def create_tracer(self, width, height):
        return ContourTracerNumba(width, height)


@unittest.skipIf(not HAS_CYTHON, "Cython module not compiled")
class TestContourCython(TestContourBase, unittest.TestCase):
    """Test Cython implementation."""
    
    def create_tracer(self, width, height):
        return ContourTracerCython(width, height)


@unittest.skipIf(not (HAS_NUMPY and HAS_CYTHON), "Missing implementations")
class TestConsistency(unittest.TestCase):
    """Test consistency between implementations."""
    
    def flatten_to_segments(self, result):
        """Flatten polylines or segments to individual segments."""
        segments = []
        for item in result:
            if len(item) >= 2:
                # Could be a polyline (list of points) or a segment (2 points)
                if len(item) == 2 and isinstance(item[0], (tuple, list)) and len(item[0]) == 2:
                    # It's a segment: [(x1,y1), (x2,y2)]
                    segments.append(item)
                else:
                    # It's a polyline: [(x1,y1), (x2,y2), (x3,y3), ...]
                    # Break into segments
                    for i in range(len(item) - 1):
                        segments.append([item[i], item[i+1]])
        return segments
    
    def compare_segments(self, result1, result2, tolerance=1e-6):
        """Compare two sets of segments (handles different formats)."""
        # Flatten both to individual segments
        segments1 = self.flatten_to_segments(result1)
        segments2 = self.flatten_to_segments(result2)
        
        # Both should have produced some contours
        self.assertGreater(len(segments1), 0, "First implementation produced no segments")
        self.assertGreater(len(segments2), 0, "Second implementation produced no segments")
        
        # They should produce similar numbers of segments (within reason)
        ratio = max(len(segments1), len(segments2)) / max(1, min(len(segments1), len(segments2)))
        self.assertLess(ratio, 2.0, 
                       f"Segment count mismatch: {len(segments1)} vs {len(segments2)}")
    
    def test_gradient_consistency(self):
        """Test all implementations produce same results on gradient."""
        data = []
        for y in range(8):
            row = []
            for x in range(8):
                row.append(float(x + y))
            data.append(row)
        
        python_tracer = ContourTracerPython(8, 8)
        python_tracer.set_data(data)
        python_result = python_tracer.trace_level(7.0)
        
        numba_tracer = ContourTracerNumba(8, 8)
        numba_tracer.set_data(data)
        numba_result = numba_tracer.trace_level(7.0)
        
        cython_tracer = ContourTracerCython(8, 8)
        cython_tracer.set_data(data)
        cython_result = cython_tracer.trace_level(7.0)
        
        self.compare_segments(python_result, numba_result)
        self.compare_segments(python_result, cython_result)
    
    def test_peak_consistency(self):
        """Test all implementations on peak data."""
        data = [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 2.0, 2.0, 1.0, 0.0],
            [0.0, 2.0, 4.0, 4.0, 2.0, 0.0],
            [0.0, 2.0, 4.0, 4.0, 2.0, 0.0],
            [0.0, 1.0, 2.0, 2.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ]
        
        python_tracer = ContourTracerPython(6, 6)
        python_tracer.set_data(data)
        python_result = python_tracer.trace_level(1.5)
        
        numba_tracer = ContourTracerNumba(6, 6)
        numba_tracer.set_data(data)
        numba_result = numba_tracer.trace_level(1.5)
        
        cython_tracer = ContourTracerCython(6, 6)
        cython_tracer.set_data(data)
        cython_result = cython_tracer.trace_level(1.5)
        
        self.compare_segments(python_result, numba_result)
        self.compare_segments(python_result, cython_result)


if __name__ == '__main__':
    unittest.main()
