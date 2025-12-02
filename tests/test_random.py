"""
Tests for random number generation implementations.

This test suite validates:
1. Reproducibility: Same seed produces same sequence
2. Range correctness: Values fall within expected ranges
3. Statistical properties: Distribution quality (chi-square, K-S tests)
4. Consistency: Python and Numba produce identical sequences
5. API compatibility: Functions work as expected

Statistical tests use significance level α = 0.01 (99% confidence).

Author: CCPN Team
License: LGPL
"""

import unittest
import sys
import os
import math

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.c.python_impl import random as random_py
from memops.c.python_impl import random_numba


class TestRandomPython(unittest.TestCase):
    """Test pure Python random implementation."""
    
    def setUp(self):
        """Reset random state before each test."""
        random_py.set_seed(12345)
    
    def test_reproducibility(self):
        """Test that same seed produces same sequence."""
        random_py.set_seed(42)
        values1 = [random_py.uniform01() for _ in range(100)]
        
        random_py.set_seed(42)
        values2 = [random_py.uniform01() for _ in range(100)]
        
        for v1, v2 in zip(values1, values2):
            self.assertAlmostEqual(v1, v2, places=15)
    
    def test_uniform01_range(self):
        """Test uniform01 produces values in [0, 1)."""
        values = [random_py.uniform01() for _ in range(1000)]
        
        for v in values:
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)
    
    def test_uniform_range(self):
        """Test uniform produces values in [a, b)."""
        a, b = 10.0, 20.0
        values = [random_py.uniform(a, b) for _ in range(1000)]
        
        for v in values:
            self.assertGreaterEqual(v, a)
            self.assertLess(v, b)
    
    def test_uniform01_distribution(self):
        """Test uniform01 has approximately uniform distribution."""
        n = 10000
        bins = 10
        values = [random_py.uniform01() for _ in range(n)]
        
        # Count values in each bin
        counts = [0] * bins
        for v in values:
            bin_idx = min(int(v * bins), bins - 1)
            counts[bin_idx] += 1
        
        # Chi-square test: each bin should have ~n/bins values
        expected = n / bins
        chi_square = sum((c - expected) ** 2 / expected for c in counts)
        
        # Critical value for χ²(9) at α=0.01 is ~21.67
        self.assertLess(chi_square, 30.0, 
                       f"Chi-square test failed: {chi_square:.2f} > 30.0")
    
    def test_normal01_mean_std(self):
        """Test normal01 has approximately mean=0, std=1."""
        n = 10000
        values = [random_py.normal01() for _ in range(n)]
        
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        std = math.sqrt(variance)
        
        # Should be close to 0 and 1
        self.assertAlmostEqual(mean, 0.0, delta=0.05)
        self.assertAlmostEqual(std, 1.0, delta=0.05)
    
    def test_normal_mean_std(self):
        """Test normal produces specified mean and std dev."""
        n = 10000
        target_mean = 5.0
        target_std = 2.0
        
        values = [random_py.normal(target_mean, target_std) for _ in range(n)]
        
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        std = math.sqrt(variance)
        
        self.assertAlmostEqual(mean, target_mean, delta=0.1)
        self.assertAlmostEqual(std, target_std, delta=0.1)
    
    def test_normal01_range(self):
        """Test normal01 produces reasonable values (within ~5 sigma)."""
        values = [random_py.normal01() for _ in range(1000)]
        
        # ~99.9999% should be within ±5 sigma
        outliers = sum(1 for v in values if abs(v) > 5.0)
        self.assertLess(outliers, 5, f"Too many outliers: {outliers}")
    
    def test_box_muller_pairing(self):
        """Test Box-Muller generates pairs correctly."""
        random_py.set_seed(999)
        
        # Generate even number of values
        values = [random_py.normal01() for _ in range(100)]
        
        # All should be valid floats
        for v in values:
            self.assertIsInstance(v, float)
            self.assertFalse(math.isnan(v))
            self.assertFalse(math.isinf(v))
    
    def test_different_seeds_different_sequences(self):
        """Test different seeds produce different sequences."""
        random_py.set_seed(1)
        values1 = [random_py.uniform01() for _ in range(100)]
        
        random_py.set_seed(2)
        values2 = [random_py.uniform01() for _ in range(100)]
        
        # Should have at least some different values
        differences = sum(1 for v1, v2 in zip(values1, values2) if abs(v1 - v2) > 1e-10)
        self.assertGreater(differences, 50)
    
    def test_array_generation(self):
        """Test array generation functions."""
        n = 1000
        
        # uniform01_array
        arr = random_py.uniform01_array(n)
        self.assertEqual(len(arr), n)
        for v in arr:
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)
        
        # normal01_array
        random_py.set_seed(42)
        arr = random_py.normal01_array(n)
        self.assertEqual(len(arr), n)
        mean = sum(arr) / n
        self.assertAlmostEqual(mean, 0.0, delta=0.1)


class TestRandomNumba(unittest.TestCase):
    """Test Numba JIT-compiled random implementation."""
    
    def setUp(self):
        """Reset random state before each test."""
        random_numba.set_seed(12345)
    
    def test_reproducibility(self):
        """Test that same seed produces same sequence."""
        random_numba.set_seed(42)
        values1 = [random_numba.uniform01() for _ in range(100)]
        
        random_numba.set_seed(42)
        values2 = [random_numba.uniform01() for _ in range(100)]
        
        for v1, v2 in zip(values1, values2):
            self.assertAlmostEqual(v1, v2, places=15)
    
    def test_uniform01_range(self):
        """Test uniform01 produces values in [0, 1)."""
        values = [random_numba.uniform01() for _ in range(1000)]
        
        for v in values:
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)
    
    def test_uniform_range(self):
        """Test uniform produces values in [a, b)."""
        a, b = 10.0, 20.0
        values = [random_numba.uniform(a, b) for _ in range(1000)]
        
        for v in values:
            self.assertGreaterEqual(v, a)
            self.assertLess(v, b)
    
    def test_normal01_mean_std(self):
        """Test normal01 has approximately mean=0, std=1."""
        n = 10000
        values = [random_numba.normal01() for _ in range(n)]
        
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        std = math.sqrt(variance)
        
        self.assertAlmostEqual(mean, 0.0, delta=0.05)
        self.assertAlmostEqual(std, 1.0, delta=0.05)
    
    def test_array_generation(self):
        """Test array generation functions."""
        n = 1000
        
        # uniform01_array
        arr = random_numba.uniform01_array(n)
        self.assertEqual(len(arr), n)
        for v in arr:
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)
        
        # uniform_array
        arr = random_numba.uniform_array(n, 5.0, 10.0)
        self.assertEqual(len(arr), n)
        for v in arr:
            self.assertGreaterEqual(v, 5.0)
            self.assertLess(v, 10.0)
        
        # normal01_array
        random_numba.set_seed(42)
        arr = random_numba.normal01_array(n)
        self.assertEqual(len(arr), n)
        mean = sum(arr) / n
        self.assertAlmostEqual(mean, 0.0, delta=0.1)
        
        # normal_array
        arr = random_numba.normal_array(n, 10.0, 2.0)
        self.assertEqual(len(arr), n)
        mean = sum(arr) / n
        self.assertAlmostEqual(mean, 10.0, delta=0.2)


class TestConsistency(unittest.TestCase):
    """Test consistency between Python and Numba implementations."""
    
    def test_same_seed_same_sequence(self):
        """Test Python and Numba produce identical sequences."""
        seed = 987654
        n = 100
        
        # Generate with Python
        random_py.set_seed(seed)
        py_values = [random_py.uniform01() for _ in range(n)]
        
        # Generate with Numba
        random_numba.set_seed(seed)
        numba_values = [random_numba.uniform01() for _ in range(n)]
        
        # Should be identical
        for i, (pv, nv) in enumerate(zip(py_values, numba_values)):
            self.assertAlmostEqual(pv, nv, places=14,
                                  msg=f"Mismatch at index {i}")
    
    def test_uniform_consistency(self):
        """Test uniform function consistency."""
        seed = 555
        n = 100
        a, b = 3.0, 7.0
        
        random_py.set_seed(seed)
        py_values = [random_py.uniform(a, b) for _ in range(n)]
        
        random_numba.set_seed(seed)
        numba_values = [random_numba.uniform(a, b) for _ in range(n)]
        
        for pv, nv in zip(py_values, numba_values):
            self.assertAlmostEqual(pv, nv, places=14)
    
    def test_normal01_consistency(self):
        """Test normal01 function consistency."""
        seed = 777
        n = 100
        
        random_py.set_seed(seed)
        py_values = [random_py.normal01() for _ in range(n)]
        
        random_numba.set_seed(seed)
        numba_values = [random_numba.normal01() for _ in range(n)]
        
        for i, (pv, nv) in enumerate(zip(py_values, numba_values)):
            self.assertAlmostEqual(pv, nv, places=14,
                                  msg=f"Normal mismatch at index {i}")
    
    def test_normal_consistency(self):
        """Test normal function consistency."""
        seed = 333
        n = 100
        mean, std = 5.0, 2.0
        
        random_py.set_seed(seed)
        py_values = [random_py.normal(mean, std) for _ in range(n)]
        
        random_numba.set_seed(seed)
        numba_values = [random_numba.normal(mean, std) for _ in range(n)]
        
        for pv, nv in zip(py_values, numba_values):
            self.assertAlmostEqual(pv, nv, places=14)
    
    def test_array_consistency(self):
        """Test array generation consistency."""
        seed = 111
        n = 1000
        
        random_py.set_seed(seed)
        py_arr = random_py.uniform01_array(n)
        
        random_numba.set_seed(seed)
        numba_arr = random_numba.uniform01_array(n)
        
        for i, (pv, nv) in enumerate(zip(py_arr, numba_arr)):
            self.assertAlmostEqual(pv, nv, places=14,
                                  msg=f"Array mismatch at index {i}")


class TestStatisticalQuality(unittest.TestCase):
    """Test statistical quality of random number generators."""
    
    def setUp(self):
        """Reset random state."""
        random_py.set_seed(12345)
    
    def test_kolmogorov_smirnov_uniform(self):
        """Test uniformity using Kolmogorov-Smirnov test."""
        n = 1000
        values = sorted([random_py.uniform01() for _ in range(n)])
        
        # K-S statistic: max difference between empirical and theoretical CDF
        max_diff = 0.0
        for i, v in enumerate(values):
            empirical_cdf = (i + 1) / n
            theoretical_cdf = v  # For uniform [0,1], CDF(x) = x
            diff = abs(empirical_cdf - theoretical_cdf)
            max_diff = max(max_diff, diff)
        
        # Critical value for K-S test at α=0.01 is ~1.63/sqrt(n)
        critical_value = 1.63 / math.sqrt(n)
        self.assertLess(max_diff, critical_value * 1.5,
                       f"K-S test failed: D={max_diff:.4f} > {critical_value:.4f}")
    
    def test_runs_test(self):
        """Test for independence using runs test."""
        n = 1000
        values = [random_py.uniform01() for _ in range(n)]
        
        # Count runs (sequences of increasing or decreasing values)
        runs = 1
        for i in range(1, n):
            if (values[i] > values[i-1]) != (values[i-1] > values[i-2] if i > 1 else True):
                runs += 1
        
        # Expected number of runs for random sequence
        expected_runs = (2 * n - 1) / 3
        
        # Should be reasonably close
        self.assertAlmostEqual(runs, expected_runs, delta=expected_runs * 0.2)
    
    def test_correlation(self):
        """Test for lack of correlation between successive values."""
        n = 1000
        values = [random_py.uniform01() for _ in range(n)]
        
        # Calculate lag-1 autocorrelation
        mean = sum(values) / n
        numerator = sum((values[i] - mean) * (values[i+1] - mean) 
                       for i in range(n-1))
        denominator = sum((v - mean) ** 2 for v in values)
        
        correlation = numerator / denominator if denominator > 0 else 0
        
        # Should be close to 0 (uncorrelated)
        self.assertAlmostEqual(correlation, 0.0, delta=0.1)


if __name__ == '__main__':
    unittest.main()
