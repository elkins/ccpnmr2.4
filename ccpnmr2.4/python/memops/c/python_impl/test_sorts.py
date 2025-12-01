"""
Test suite for sorting implementations (Python and Numba).
"""

import unittest
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sorts import heap_sort, sort_ascending, sort_descending
from sorts import heap_sort as heap_sort_python

try:
    from sorts_numba import heap_sort as heap_sort_numba
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False


class TestSortsPython(unittest.TestCase):
    """Test pure Python sorting."""
    
    def test_empty_list(self):
        """Test sorting empty list."""
        result = heap_sort([])
        self.assertEqual(result, [])
    
    def test_single_element(self):
        """Test sorting single element."""
        result = heap_sort([42])
        self.assertEqual(result, [42])
    
    def test_sorted_list(self):
        """Test already sorted list."""
        data = [1, 2, 3, 4, 5]
        result = heap_sort(data)
        self.assertEqual(result, [1, 2, 3, 4, 5])
    
    def test_reverse_sorted(self):
        """Test reverse sorted list."""
        data = [5, 4, 3, 2, 1]
        result = heap_sort(data)
        self.assertEqual(result, [1, 2, 3, 4, 5])
    
    def test_random_integers(self):
        """Test random integers."""
        data = [3, 1, 4, 1, 5, 9, 2, 6]
        result = heap_sort(data)
        expected = sorted(data)
        self.assertEqual(result, expected)
    
    def test_random_floats(self):
        """Test random floats."""
        data = [3.14, 2.71, 1.41, 1.73]
        result = heap_sort(data)
        expected = sorted(data)
        self.assertEqual(result, expected)
    
    def test_descending_order(self):
        """Test descending sort."""
        data = [1, 2, 3, 4, 5]
        result = heap_sort(data, ascending=False)
        self.assertEqual(result, [5, 4, 3, 2, 1])
    
    def test_duplicates(self):
        """Test list with duplicates."""
        data = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        result = heap_sort(data)
        expected = sorted(data)
        self.assertEqual(result, expected)
    
    def test_large_random(self):
        """Test larger random list."""
        random.seed(42)
        data = [random.randint(1, 100) for _ in range(100)]
        result = heap_sort(data)
        expected = sorted(data)
        self.assertEqual(result, expected)
    
    def test_sort_ascending_function(self):
        """Test sort_ascending convenience function."""
        data = [3, 1, 4, 1, 5]
        result = sort_ascending(data)
        self.assertEqual(result, [1, 1, 3, 4, 5])
    
    def test_sort_descending_function(self):
        """Test sort_descending convenience function."""
        data = [3, 1, 4, 1, 5]
        result = sort_descending(data)
        self.assertEqual(result, [5, 4, 3, 1, 1])


@unittest.skipIf(not HAS_NUMBA, "Numba not available")
class TestSortsNumba(unittest.TestCase):
    """Test Numba sorting."""
    
    def test_empty_list(self):
        """Test sorting empty list."""
        result = heap_sort_numba([])
        self.assertEqual(result, [])
    
    def test_single_element(self):
        """Test sorting single element."""
        result = heap_sort_numba([42])
        self.assertEqual(result, [42])
    
    def test_random_integers(self):
        """Test random integers."""
        data = [3, 1, 4, 1, 5, 9, 2, 6]
        result = heap_sort_numba(data)
        expected = sorted(data)
        self.assertEqual(result, expected)
    
    def test_random_floats(self):
        """Test random floats."""
        data = [3.14, 2.71, 1.41, 1.73]
        result = heap_sort_numba(data)
        expected = sorted(data)
        for i in range(len(expected)):
            self.assertAlmostEqual(result[i], expected[i])
    
    def test_descending_order(self):
        """Test descending sort."""
        data = [1, 2, 3, 4, 5]
        result = heap_sort_numba(data, ascending=False)
        self.assertEqual(result, [5, 4, 3, 2, 1])
    
    def test_large_random(self):
        """Test larger random list."""
        random.seed(42)
        data = [random.randint(1, 100) for _ in range(100)]
        result = heap_sort_numba(data)
        expected = sorted(data)
        self.assertEqual(result, expected)


@unittest.skipIf(not HAS_NUMBA, "Numba not available")
class TestSortsConsistency(unittest.TestCase):
    """Test consistency between Python and Numba implementations."""
    
    def test_consistency_integers(self):
        """Ensure Python and Numba give same results for integers."""
        test_lists = [
            [3, 1, 4, 1, 5, 9, 2, 6],
            [5, 4, 3, 2, 1],
            [1, 1, 1, 1],
            list(range(20, 0, -1))
        ]
        for data in test_lists:
            python_result = heap_sort_python(data)
            numba_result = heap_sort_numba(data)
            self.assertEqual(python_result, numba_result,
                           f"Mismatch for {data}")
    
    def test_consistency_floats(self):
        """Ensure Python and Numba give same results for floats."""
        test_lists = [
            [3.14, 2.71, 1.41, 1.73],
            [0.1, 0.2, 0.3, 0.15, 0.25],
        ]
        for data in test_lists:
            python_result = heap_sort_python(data)
            numba_result = heap_sort_numba(data)
            for i in range(len(python_result)):
                self.assertAlmostEqual(python_result[i], numba_result[i], places=10)
    
    def test_consistency_descending(self):
        """Test descending sort consistency."""
        data = [3, 1, 4, 1, 5, 9, 2, 6]
        python_result = heap_sort_python(data, ascending=False)
        numba_result = heap_sort_numba(data, ascending=False)
        self.assertEqual(python_result, numba_result)


if __name__ == '__main__':
    unittest.main()
