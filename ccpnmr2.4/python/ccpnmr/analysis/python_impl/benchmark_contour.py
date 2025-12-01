"""
Benchmark contour implementations: Pure Python, Numba, and Cython.

NOTE: These benchmarks compare simplified standalone implementations created for
performance comparison. They do NOT benchmark the existing C implementation at
ccpnmr2.4/c/ccpnmr/analysis/contour_file.c.

See contour.py for rationale on why simplified implementations were created
instead of wrapping the existing complex C code with its file I/O, caching,
and rendering infrastructure.

Tests performance on:
- Various grid sizes
- Multiple contour levels
- Different data patterns
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("NumPy not available")
    sys.exit(1)

from contour import ContourTracer as ContourTracerPython
from contour_numba import ContourTracer as ContourTracerNumba

try:
    from contour_cython import ContourTracer as ContourTracerCython
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False
    print("Warning: Cython module not available")


def create_test_data(size, pattern='gradient'):
    """Create test data with specified pattern."""
    if pattern == 'gradient':
        # Linear gradient
        data = []
        for y in range(size):
            row = []
            for x in range(size):
                row.append(float(x + y) / size)
            data.append(row)
        return data
    
    elif pattern == 'peaks':
        # Multiple peaks
        data = []
        for y in range(size):
            row = []
            for x in range(size):
                # Create peaks at regular intervals
                dx = (x % 10) - 5
                dy = (y % 10) - 5
                dist = (dx * dx + dy * dy) ** 0.5
                val = max(0, 5 - dist)
                row.append(val)
            data.append(row)
        return data
    
    elif pattern == 'noise':
        # Random noise
        np.random.seed(42)
        return np.random.randn(size, size).tolist()
    
    else:
        raise ValueError(f"Unknown pattern: {pattern}")


def benchmark_tracer(tracer_class, name, data, levels, iterations=10):
    """Benchmark a tracer implementation."""
    size = len(data)
    
    # Create and initialize tracer
    tracer = tracer_class(size, size)
    tracer.set_data(data)
    
    # Warmup
    tracer.trace_level(levels[0])
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        for level in levels:
            tracer.trace_level(level)
    end = time.perf_counter()
    
    elapsed = end - start
    ops_per_sec = (iterations * len(levels)) / elapsed
    
    return elapsed, ops_per_sec


def run_benchmark(size, pattern, levels, iterations=10):
    """Run benchmark for all implementations."""
    print(f"\n{'='*60}")
    print(f"Grid: {size}x{size}, Pattern: {pattern}, Levels: {len(levels)}")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}")
    
    data = create_test_data(size, pattern)
    
    results = {}
    
    # Benchmark Python
    print(f"\n{'Python':<15}", end='', flush=True)
    elapsed, ops = benchmark_tracer(ContourTracerPython, 'Python', data, levels, iterations)
    results['Python'] = (elapsed, ops)
    print(f"Time: {elapsed:.4f}s  Ops/sec: {ops:.2f}")
    
    # Benchmark Numba
    if HAS_NUMPY:
        print(f"{'Numba':<15}", end='', flush=True)
        elapsed, ops = benchmark_tracer(ContourTracerNumba, 'Numba', data, levels, iterations)
        results['Numba'] = (elapsed, ops)
        print(f"Time: {elapsed:.4f}s  Ops/sec: {ops:.2f}")
    
    # Benchmark Cython
    if HAS_CYTHON:
        print(f"{'Cython':<15}", end='', flush=True)
        elapsed, ops = benchmark_tracer(ContourTracerCython, 'Cython', data, levels, iterations)
        results['Cython'] = (elapsed, ops)
        print(f"Time: {elapsed:.4f}s  Ops/sec: {ops:.2f}")
    
    # Print speedups
    print(f"\n{'Speedups vs Python:':^60}")
    python_time = results['Python'][0]
    for name, (elapsed, ops) in results.items():
        if name != 'Python':
            speedup = python_time / elapsed
            print(f"  {name:<15} {speedup:.2f}x")
    
    return results


def main():
    """Run comprehensive benchmarks."""
    print("="*60)
    print("CONTOUR TRACING BENCHMARK: Python vs Numba vs Cython")
    print("="*60)
    
    # Test configurations
    configs = [
        # (size, pattern, levels, iterations)
        (50, 'gradient', [0.2, 0.4, 0.6, 0.8], 50),
        (100, 'gradient', [0.2, 0.4, 0.6, 0.8], 20),
        (200, 'gradient', [0.2, 0.4, 0.6, 0.8], 5),
        (100, 'peaks', [1.0, 2.0, 3.0, 4.0], 20),
        (100, 'noise', [0.0], 20),
    ]
    
    all_results = []
    for size, pattern, levels, iterations in configs:
        results = run_benchmark(size, pattern, levels, iterations)
        all_results.append((size, pattern, results))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    python_wins = 0
    numba_wins = 0
    cython_wins = 0
    
    for size, pattern, results in all_results:
        fastest = min(results.items(), key=lambda x: x[1][0])
        print(f"\n{size}x{size} {pattern:>10}: {fastest[0]} fastest ({fastest[1][0]:.4f}s)")
        
        if fastest[0] == 'Python':
            python_wins += 1
        elif fastest[0] == 'Numba':
            numba_wins += 1
        elif fastest[0] == 'Cython':
            cython_wins += 1
    
    print(f"\n{'='*60}")
    print(f"Python: {python_wins} wins")
    print(f"Numba:  {numba_wins} wins")
    print(f"Cython: {cython_wins} wins")
    print(f"{'='*60}")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if cython_wins > 0:
        print("• Cython: Best for production performance-critical code")
    if numba_wins > 0:
        print("• Numba: Good balance of performance and ease of use")
    if python_wins > 0:
        print("• Python: Surprisingly competitive, easiest to maintain")


if __name__ == '__main__':
    main()
