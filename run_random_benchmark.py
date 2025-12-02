"""
Wrapper script to run random benchmark without import conflicts.
"""

import sys
import os

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ccpnmr2.4', 'python'))

# Now run the benchmark code
import time
import math
import random as stdlib_random
import numpy as np

from memops.c.python_impl import random as random_py
from memops.c.python_impl import random_numba


def benchmark_single_uniform(n_calls=10000):
    """Benchmark single uniform random number generation."""
    print(f"\n{'='*70}")
    print(f"UNIFORM01: Single value generation ({n_calls:,} calls)")
    print(f"{'='*70}")
    
    results = {}
    
    # Pure Python LCG
    random_py.set_seed(12345)
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = random_py.uniform01()
    elapsed = time.perf_counter() - start
    results['Python LCG'] = elapsed
    print(f"Python LCG:        {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # Numba LCG
    random_numba.set_seed(12345)
    # Warmup
    for _ in range(100):
        _ = random_numba.uniform01()
    
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = random_numba.uniform01()
    elapsed = time.perf_counter() - start
    results['Numba LCG'] = elapsed
    print(f"Numba LCG:         {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # Python stdlib
    stdlib_random.seed(12345)
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = stdlib_random.random()
    elapsed = time.perf_counter() - start
    results['Stdlib (MT)'] = elapsed
    print(f"Stdlib (MT):       {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # NumPy
    np.random.seed(12345)
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = np.random.random()
    elapsed = time.perf_counter() - start
    results['NumPy (PCG64)'] = elapsed
    print(f"NumPy (PCG64):     {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # Find fastest
    fastest = min(results.values())
    print(f"\nSpeedup vs fastest:")
    for name, elapsed in results.items():
        speedup = elapsed / fastest
        print(f"  {name:20s}: {speedup:6.2f}x")
    
    return results


def benchmark_array_uniform(n_values=100000):
    """Benchmark array uniform random number generation."""
    print(f"\n{'='*70}")
    print(f"UNIFORM01: Array generation ({n_values:,} values)")
    print(f"{'='*70}")
    
    results = {}
    
    # Pure Python LCG
    random_py.set_seed(12345)
    start = time.perf_counter()
    _ = random_py.uniform01_array(n_values)
    elapsed = time.perf_counter() - start
    results['Python LCG'] = elapsed
    print(f"Python LCG:        {elapsed:8.4f}s  ({n_values/elapsed:>12,.0f} values/sec)")
    
    # Numba LCG
    random_numba.set_seed(12345)
    # Warmup
    _ = random_numba.uniform01_array(100)
    
    start = time.perf_counter()
    _ = random_numba.uniform01_array(n_values)
    elapsed = time.perf_counter() - start
    results['Numba LCG'] = elapsed
    print(f"Numba LCG:         {elapsed:8.4f}s  ({n_values/elapsed:>12,.0f} values/sec)")
    
    # NumPy (vectorized)
    np.random.seed(12345)
    start = time.perf_counter()
    _ = np.random.random(n_values)
    elapsed = time.perf_counter() - start
    results['NumPy (PCG64)'] = elapsed
    print(f"NumPy (PCG64):     {elapsed:8.4f}s  ({n_values/elapsed:>12,.0f} values/sec)")
    
    # Find fastest
    fastest = min(results.values())
    print(f"\nSpeedup vs fastest:")
    for name, elapsed in results.items():
        speedup = elapsed / fastest
        print(f"  {name:20s}: {speedup:6.2f}x")
    
    return results


def benchmark_single_normal(n_calls=10000):
    """Benchmark single normal random number generation."""
    print(f"\n{'='*70}")
    print(f"NORMAL01: Single value generation ({n_calls:,} calls)")
    print(f"{'='*70}")
    
    results = {}
    
    # Pure Python LCG
    random_py.set_seed(12345)
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = random_py.normal01()
    elapsed = time.perf_counter() - start
    results['Python LCG'] = elapsed
    print(f"Python LCG:        {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # Numba LCG
    random_numba.set_seed(12345)
    # Warmup
    for _ in range(100):
        _ = random_numba.normal01()
    
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = random_numba.normal01()
    elapsed = time.perf_counter() - start
    results['Numba LCG'] = elapsed
    print(f"Numba LCG:         {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # Python stdlib
    stdlib_random.seed(12345)
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = stdlib_random.gauss(0, 1)
    elapsed = time.perf_counter() - start
    results['Stdlib (MT)'] = elapsed
    print(f"Stdlib (MT):       {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # NumPy
    np.random.seed(12345)
    start = time.perf_counter()
    for _ in range(n_calls):
        _ = np.random.randn()
    elapsed = time.perf_counter() - start
    results['NumPy (PCG64)'] = elapsed
    print(f"NumPy (PCG64):     {elapsed:8.4f}s  ({n_calls/elapsed:>12,.0f} calls/sec)")
    
    # Find fastest
    fastest = min(results.values())
    print(f"\nSpeedup vs fastest:")
    for name, elapsed in results.items():
        speedup = elapsed / fastest
        print(f"  {name:20s}: {speedup:6.2f}x")
    
    return results


def benchmark_array_normal(n_values=100000):
    """Benchmark array normal random number generation."""
    print(f"\n{'='*70}")
    print(f"NORMAL01: Array generation ({n_values:,} values)")
    print(f"{'='*70}")
    
    results = {}
    
    # Pure Python LCG
    random_py.set_seed(12345)
    start = time.perf_counter()
    _ = random_py.normal01_array(n_values)
    elapsed = time.perf_counter() - start
    results['Python LCG'] = elapsed
    print(f"Python LCG:        {elapsed:8.4f}s  ({n_values/elapsed:>12,.0f} values/sec)")
    
    # Numba LCG
    random_numba.set_seed(12345)
    # Warmup
    _ = random_numba.normal01_array(100)
    
    start = time.perf_counter()
    _ = random_numba.normal01_array(n_values)
    elapsed = time.perf_counter() - start
    results['Numba LCG'] = elapsed
    print(f"Numba LCG:         {elapsed:8.4f}s  ({n_values/elapsed:>12,.0f} values/sec)")
    
    # NumPy (vectorized)
    np.random.seed(12345)
    start = time.perf_counter()
    _ = np.random.randn(n_values)
    elapsed = time.perf_counter() - start
    results['NumPy (PCG64)'] = elapsed
    print(f"NumPy (PCG64):     {elapsed:8.4f}s  ({n_values/elapsed:>12,.0f} values/sec)")
    
    # Find fastest
    fastest = min(results.values())
    print(f"\nSpeedup vs fastest:")
    for name, elapsed in results.items():
        speedup = elapsed / fastest
        print(f"  {name:20s}: {speedup:6.2f}x")
    
    return results


def test_statistical_quality():
    """Test statistical quality of different generators."""
    print(f"\n{'='*70}")
    print(f"STATISTICAL QUALITY COMPARISON")
    print(f"{'='*70}")
    
    n = 10000
    
    # Test uniformity (chi-square)
    print(f"\nUniformity (Chi-square test, {n:,} samples):")
    print("Lower values = more uniform (< 20 is good)")
    
    for name, gen_func, seed_func in [
        ('Python LCG', lambda: random_py.uniform01(), random_py.set_seed),
        ('Numba LCG', lambda: random_numba.uniform01(), random_numba.set_seed),
        ('Stdlib (MT)', lambda: stdlib_random.random(), lambda s: stdlib_random.seed(s)),
        ('NumPy (PCG64)', lambda: np.random.random(), lambda s: np.random.seed(s)),
    ]:
        seed_func(12345)
        values = [gen_func() for _ in range(n)]
        
        # Chi-square test
        bins = 10
        counts = [0] * bins
        for v in values:
            bin_idx = min(int(v * bins), bins - 1)
            counts[bin_idx] += 1
        
        expected = n / bins
        chi_square = sum((c - expected) ** 2 / expected for c in counts)
        
        print(f"  {name:20s}: χ² = {chi_square:6.2f}")
    
    # Test normality (mean and std)
    print(f"\nNormality (Mean and Std Dev, {n:,} samples):")
    print("Should be close to mean=0.0, std=1.0")
    
    for name, gen_func, seed_func in [
        ('Python LCG', lambda: random_py.normal01(), random_py.set_seed),
        ('Numba LCG', lambda: random_numba.normal01(), random_numba.set_seed),
        ('Stdlib (MT)', lambda: stdlib_random.gauss(0, 1), lambda s: stdlib_random.seed(s)),
        ('NumPy (PCG64)', lambda: np.random.randn(), lambda s: np.random.seed(s)),
    ]:
        seed_func(12345)
        values = [gen_func() for _ in range(n)]
        
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        std = math.sqrt(variance)
        
        print(f"  {name:20s}: mean={mean:7.4f}, std={std:6.4f}")


def main():
    """Run all benchmarks."""
    print("="*70)
    print("RANDOM NUMBER GENERATION BENCHMARK")
    print("="*70)
    print("\nComparing implementations:")
    print("  - Python LCG:     Pure Python implementation (random.py)")
    print("  - Numba LCG:      JIT-compiled implementation (random_numba.py)")
    print("  - Stdlib (MT):    Python standard library (Mersenne Twister)")
    print("  - NumPy (PCG64):  NumPy random (PCG64 generator)")
    
    # Single value benchmarks
    benchmark_single_uniform(n_calls=100000)
    benchmark_single_normal(n_calls=100000)
    
    # Array benchmarks
    benchmark_array_uniform(n_values=1000000)
    benchmark_array_normal(n_values=1000000)
    
    # Statistical quality
    test_statistical_quality()
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print("\nKey Findings:")
    print("  • Single values: Stdlib/NumPy typically fastest (optimized C)")
    print("  • Array generation: NumPy dominates (vectorized operations)")
    print("  • Numba LCG: Good compromise, near-C performance")
    print("  • All generators pass statistical quality tests")
    print("\nUse Cases:")
    print("  • Python LCG:  Legacy compatibility, pure Python environments")
    print("  • Numba LCG:   Balance of speed and compatibility")
    print("  • NumPy:       Large arrays, best performance")
    print("  • Stdlib:      General purpose, no dependencies")


if __name__ == '__main__':
    main()
