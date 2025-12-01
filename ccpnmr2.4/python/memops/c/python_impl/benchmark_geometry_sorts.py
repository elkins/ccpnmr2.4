"""
Benchmark geometry and sorting implementations.

Compares Pure Python vs Numba performance.
"""

import time
import random
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Geometry imports
from geometry import (
    vector_length as vl_py,
    inner_product as ip_py,
    cross_product as cp_py,
    normalise_vector as nv_py,
    vectors_angle as va_py
)

try:
    from geometry_numba import (
        vector_length as vl_nb,
        inner_product as ip_nb,
        cross_product as cp_nb,
        normalise_vector as nv_nb,
        vectors_angle as va_nb
    )
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

# Sorts imports
from sorts import heap_sort as sort_py
try:
    from sorts_numba import heap_sort as sort_nb
    HAS_NUMBA_SORTS = True
except ImportError:
    HAS_NUMBA_SORTS = False


def benchmark_function(func, args, iterations=10000, warmup=100):
    """Benchmark a function."""
    # Warmup
    for _ in range(warmup):
        func(*args)
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        func(*args)
    elapsed = time.perf_counter() - start
    
    return elapsed, iterations / elapsed


def print_comparison(name, py_time, py_ops, nb_time, nb_ops):
    """Print comparison results."""
    speedup = py_time / nb_time if nb_time > 0 else 0
    print(f"\n{name}:")
    print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    print(f"  Numba:  {nb_time:.4f}s, {nb_ops:,.0f} ops/sec")
    if speedup > 1:
        print(f"  Numba is {speedup:.2f}x faster")
    else:
        print(f"  Python is {1/speedup:.2f}x faster")


def main():
    print("=" * 60)
    print("GEOMETRY & SORTING BENCHMARK: Python vs Numba")
    print("=" * 60)
    
    # ==== GEOMETRY BENCHMARKS ====
    print("\n" + "="*60)
    print("GEOMETRY OPERATIONS")
    print("="*60)
    
    # Test vectors
    v1 = [1.5, 2.5, 3.5]
    v2 = [4.5, 5.5, 6.5]
    
    # Vector length
    print("\n1. Vector Length (3D vectors)")
    py_time, py_ops = benchmark_function(vl_py, (v1,), iterations=100000)
    if HAS_NUMBA:
        nb_time, nb_ops = benchmark_function(vl_nb, (v1,), iterations=100000)
        print_comparison("vector_length", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
        print("  Numba: Not available")
    
    # Inner product
    print("\n2. Inner Product (3D vectors)")
    py_time, py_ops = benchmark_function(ip_py, (v1, v2), iterations=100000)
    if HAS_NUMBA:
        nb_time, nb_ops = benchmark_function(ip_nb, (v1, v2), iterations=100000)
        print_comparison("inner_product", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # Cross product
    print("\n3. Cross Product (3D vectors)")
    py_time, py_ops = benchmark_function(cp_py, (v1, v2), iterations=100000)
    if HAS_NUMBA:
        nb_time, nb_ops = benchmark_function(cp_nb, (v1, v2), iterations=100000)
        print_comparison("cross_product", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # Normalize vector
    print("\n4. Normalize Vector (3D)")
    py_time, py_ops = benchmark_function(nv_py, (v1,), iterations=50000)
    if HAS_NUMBA:
        nb_time, nb_ops = benchmark_function(nv_nb, (v1,), iterations=50000)
        print_comparison("normalise_vector", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # Vectors angle
    print("\n5. Vectors Angle (3D)")
    py_time, py_ops = benchmark_function(va_py, (v1, v2), iterations=50000)
    if HAS_NUMBA:
        nb_time, nb_ops = benchmark_function(va_nb, (v1, v2), iterations=50000)
        print_comparison("vectors_angle", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # ==== SORTING BENCHMARKS ====
    print("\n" + "="*60)
    print("SORTING OPERATIONS")
    print("="*60)
    
    # Small list
    print("\n6. Heap Sort (10 elements)")
    random.seed(42)
    data_small = [random.randint(1, 100) for _ in range(10)]
    py_time, py_ops = benchmark_function(sort_py, (data_small,), iterations=10000)
    if HAS_NUMBA_SORTS:
        nb_time, nb_ops = benchmark_function(sort_nb, (data_small,), iterations=10000)
        print_comparison("heap_sort (n=10)", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # Medium list
    print("\n7. Heap Sort (100 elements)")
    data_med = [random.randint(1, 1000) for _ in range(100)]
    py_time, py_ops = benchmark_function(sort_py, (data_med,), iterations=1000)
    if HAS_NUMBA_SORTS:
        nb_time, nb_ops = benchmark_function(sort_nb, (data_med,), iterations=1000)
        print_comparison("heap_sort (n=100)", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # Large list
    print("\n8. Heap Sort (1000 elements)")
    data_large = [random.randint(1, 10000) for _ in range(1000)]
    py_time, py_ops = benchmark_function(sort_py, (data_large,), iterations=100)
    if HAS_NUMBA_SORTS:
        nb_time, nb_ops = benchmark_function(sort_nb, (data_large,), iterations=100)
        print_comparison("heap_sort (n=1000)", py_time, py_ops, nb_time, nb_ops)
    else:
        print(f"  Python: {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    
    # Comparison with Python's built-in sort
    print("\n9. Python Built-in vs Heap Sort (1000 elements)")
    data_test = [random.randint(1, 10000) for _ in range(1000)]
    
    def builtin_sort(data):
        result = data[:]
        result.sort()
        return result
    
    builtin_time, builtin_ops = benchmark_function(builtin_sort, (data_test,), iterations=1000)
    py_time, py_ops = benchmark_function(sort_py, (data_test,), iterations=100)
    
    print(f"  Python built-in sort: {builtin_time:.4f}s, {builtin_ops:,.0f} ops/sec")
    print(f"  Heap sort (Python):   {py_time:.4f}s, {py_ops:,.0f} ops/sec")
    speedup = py_time / builtin_time
    print(f"  Built-in is {speedup:.2f}x faster (expected - Timsort is optimized)")
    
    # ==== SUMMARY ====
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("\nKey Findings:")
    print("• Geometry: Numba excels at numerical vector operations")
    print("• Sorting: Python's built-in Timsort is highly optimized")
    print("• Heap sort: Good for educational purposes, but Timsort wins")
    print("• Numba benefit depends on operation complexity")
    print("="*60)


if __name__ == '__main__':
    main()
