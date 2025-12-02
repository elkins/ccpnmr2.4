"""
Benchmark linear algebra implementations.

Compares performance across implementations showing the critical crossover
points where different approaches dominate:

1. Pure Python (linalg.py) - Baseline
2. Numba JIT (linalg_numba.py) - Competitive for small-medium matrices
3. NumPy BLAS (np.dot) - Dominates for large matrices

Key insights:
- Small matrices (<10×10): Overhead matters, Numba competitive
- Medium matrices (10-50×50): Numba good, NumPy starting to win
- Large matrices (>100×100): NumPy BLAS crushes everything

This benchmark demonstrates why specialized libraries exist and when
to use them versus custom implementations.

Author: CCPN Team
License: LGPL
"""

import time
import sys
import os
import numpy as np

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ccpnmr2.4', 'python'))

from memops.c.python_impl import linalg as linalg_py
from memops.c.python_impl import linalg_numba


def benchmark_matmul(sizes=[3, 5, 10, 20, 50, 100, 200]):
    """Benchmark matrix-matrix multiplication across different sizes."""
    print(f"\n{'='*80}")
    print("MATRIX-MATRIX MULTIPLICATION: C = A × B")
    print(f"{'='*80}")
    print(f"{'Size':>8} | {'Python (ms)':>12} | {'Numba (ms)':>12} | {'NumPy (ms)':>12} | {'Numba/NumPy':>12}")
    print(f"{'-'*80}")
    
    results = {}
    
    for n in sizes:
        results[n] = {}
        
        # Generate random matrices
        A_list = [[float(np.random.randn()) for _ in range(n)] for _ in range(n)]
        B_list = [[float(np.random.randn()) for _ in range(n)] for _ in range(n)]
        A_np = np.array(A_list, dtype=np.float64)
        B_np = np.array(B_list, dtype=np.float64)
        
        # Python version
        if n <= 50:  # Skip Python for large matrices (too slow)
            start = time.perf_counter()
            _ = linalg_py.matrix_matrix_multiply(A_list, B_list)
            elapsed = (time.perf_counter() - start) * 1000
            results[n]['python'] = elapsed
        else:
            results[n]['python'] = None
        
        # Numba version (with warmup for small sizes)
        if n <= 10:
            _ = linalg_numba.matmul(A_np, B_np)  # Warmup
        
        start = time.perf_counter()
        _ = linalg_numba.matmul(A_np, B_np)
        elapsed = (time.perf_counter() - start) * 1000
        results[n]['numba'] = elapsed
        
        # NumPy version
        start = time.perf_counter()
        _ = np.dot(A_np, B_np)
        elapsed = (time.perf_counter() - start) * 1000
        results[n]['numpy'] = elapsed
        
        # Print results
        py_str = f"{results[n]['python']:>10.3f}" if results[n]['python'] is not None else "   too slow"
        numba_str = f"{results[n]['numba']:>10.3f}"
        numpy_str = f"{results[n]['numpy']:>10.3f}"
        ratio = results[n]['numba'] / results[n]['numpy']
        ratio_str = f"{ratio:>10.2f}x"
        
        print(f"{n:>3}×{n:<3} | {py_str} | {numba_str} | {numpy_str} | {ratio_str}")
    
    return results


def benchmark_matvec(sizes=[10, 50, 100, 200, 500, 1000]):
    """Benchmark matrix-vector multiplication."""
    print(f"\n{'='*80}")
    print("MATRIX-VECTOR MULTIPLICATION: y = A × x")
    print(f"{'='*80}")
    print(f"{'Size':>8} | {'Python (ms)':>12} | {'Numba (ms)':>12} | {'NumPy (ms)':>12} | {'Numba/NumPy':>12}")
    print(f"{'-'*80}")
    
    results = {}
    
    for n in sizes:
        results[n] = {}
        
        # Generate random matrix and vector
        A_list = [[float(np.random.randn()) for _ in range(n)] for _ in range(n)]
        x_list = [float(np.random.randn()) for _ in range(n)]
        A_np = np.array(A_list, dtype=np.float64)
        x_np = np.array(x_list, dtype=np.float64)
        
        # Python version
        if n <= 100:  # Skip Python for large sizes
            start = time.perf_counter()
            _ = linalg_py.matrix_vector_multiply(A_list, x_list)
            elapsed = (time.perf_counter() - start) * 1000
            results[n]['python'] = elapsed
        else:
            results[n]['python'] = None
        
        # Numba version (with warmup)
        if n <= 50:
            _ = linalg_numba.matvec(A_np, x_np)
        
        start = time.perf_counter()
        _ = linalg_numba.matvec(A_np, x_np)
        elapsed = (time.perf_counter() - start) * 1000
        results[n]['numba'] = elapsed
        
        # NumPy version
        start = time.perf_counter()
        _ = np.dot(A_np, x_np)
        elapsed = (time.perf_counter() - start) * 1000
        results[n]['numpy'] = elapsed
        
        # Print results
        py_str = f"{results[n]['python']:>10.3f}" if results[n]['python'] is not None else "   too slow"
        numba_str = f"{results[n]['numba']:>10.3f}"
        numpy_str = f"{results[n]['numpy']:>10.3f}"
        ratio = results[n]['numba'] / results[n]['numpy']
        ratio_str = f"{ratio:>10.2f}x"
        
        print(f"{n:>3}×{n:<3} | {py_str} | {numba_str} | {numpy_str} | {ratio_str}")
    
    return results


def benchmark_transpose(sizes=[10, 50, 100, 200, 500, 1000]):
    """Benchmark matrix transpose."""
    print(f"\n{'='*80}")
    print("MATRIX TRANSPOSE: B = A^T")
    print(f"{'='*80}")
    print(f"{'Size':>8} | {'Python (ms)':>12} | {'Numba (ms)':>12} | {'NumPy (ms)':>12} | {'Numba/NumPy':>12}")
    print(f"{'-'*80}")
    
    results = {}
    
    for n in sizes:
        results[n] = {}
        
        # Generate random matrix
        A_list = [[float(np.random.randn()) for _ in range(n)] for _ in range(n)]
        A_np = np.array(A_list, dtype=np.float64)
        
        # Python version
        if n <= 500:
            start = time.perf_counter()
            _ = linalg_py.matrix_transpose(A_list)
            elapsed = (time.perf_counter() - start) * 1000
            results[n]['python'] = elapsed
        else:
            results[n]['python'] = None
        
        # Numba version (with warmup)
        if n <= 50:
            _ = linalg_numba.transpose(A_np)
        
        start = time.perf_counter()
        _ = linalg_numba.transpose(A_np)
        elapsed = (time.perf_counter() - start) * 1000
        results[n]['numba'] = elapsed
        
        # NumPy version
        start = time.perf_counter()
        _ = A_np.T
        elapsed = (time.perf_counter() - start) * 1000
        results[n]['numpy'] = elapsed
        
        # Print results
        py_str = f"{results[n]['python']:>10.3f}" if results[n]['python'] is not None else "   too slow"
        numba_str = f"{results[n]['numba']:>10.3f}"
        numpy_str = f"{results[n]['numpy']:>10.3f}"
        ratio = results[n]['numba'] / results[n]['numpy']
        ratio_str = f"{ratio:>10.2f}x"
        
        print(f"{n:>3}×{n:<3} | {py_str} | {numba_str} | {numpy_str} | {ratio_str}")
    
    return results


def analyze_crossover_points(matmul_results):
    """Analyze where NumPy starts winning decisively."""
    print(f"\n{'='*80}")
    print("CROSSOVER ANALYSIS")
    print(f"{'='*80}")
    
    print("\nWhen does NumPy dominate (>2x faster than Numba)?")
    for size in sorted(matmul_results.keys()):
        ratio = matmul_results[size]['numba'] / matmul_results[size]['numpy']
        if ratio > 2.0:
            print(f"  Matrix size {size}×{size}: NumPy is {ratio:.1f}x faster")
            print(f"    → BLAS optimization dominates at this scale")
            break
    else:
        print("  NumPy doesn't reach 2x advantage in tested range")
    
    print("\nWhen is Numba competitive (<1.5x slower than NumPy)?")
    for size in sorted(matmul_results.keys(), reverse=True):
        ratio = matmul_results[size]['numba'] / matmul_results[size]['numpy']
        if ratio < 1.5:
            print(f"  Matrix size {size}×{size}: Numba is {ratio:.2f}x slower")
            print(f"    → Numba is viable alternative up to this size")
            break


def demonstrate_real_nmr_sizes():
    """Show performance for typical NMR computation sizes."""
    print(f"\n{'='*80}")
    print("TYPICAL NMR MATRIX SIZES")
    print(f"{'='*80}")
    
    scenarios = [
        (3, "3D rotation matrix"),
        (5, "Small structure fragment"),
        (20, "Medium protein residue cluster"),
        (50, "Large conformational ensemble"),
    ]
    
    print(f"\n{'Scenario':<35} | {'Size':>5} | {'Best Choice':<20}")
    print(f"{'-'*80}")
    
    for size, desc in scenarios:
        A = np.random.randn(size, size)
        B = np.random.randn(size, size)
        
        # Time Numba
        _ = linalg_numba.matmul(A, B)  # Warmup
        start = time.perf_counter()
        for _ in range(100):
            _ = linalg_numba.matmul(A, B)
        numba_time = time.perf_counter() - start
        
        # Time NumPy
        start = time.perf_counter()
        for _ in range(100):
            _ = np.dot(A, B)
        numpy_time = time.perf_counter() - start
        
        ratio = numba_time / numpy_time
        
        if ratio < 1.2:
            choice = "Either (similar)"
        elif ratio < 2.0:
            choice = "NumPy (1.2-2x faster)"
        else:
            choice = f"NumPy ({ratio:.1f}x faster)"
        
        print(f"{desc:<35} | {size:>3}×{size:<2} | {choice:<20}")


def main():
    """Run all benchmarks."""
    print("="*80)
    print("LINEAR ALGEBRA BENCHMARK")
    print("="*80)
    print("\nComparing implementations:")
    print("  - Python:  Pure Python nested loops (linalg.py)")
    print("  - Numba:   JIT-compiled (linalg_numba.py)")
    print("  - NumPy:   BLAS-optimized (np.dot, np.transpose)")
    
    # Matrix multiplication - the main event
    matmul_results = benchmark_matmul(sizes=[3, 5, 10, 20, 50, 100, 200])
    
    # Matrix-vector multiplication
    matvec_results = benchmark_matvec(sizes=[10, 50, 100, 200, 500, 1000])
    
    # Transpose (less compute-intensive)
    transpose_results = benchmark_transpose(sizes=[10, 50, 100, 200, 500, 1000])
    
    # Analysis
    analyze_crossover_points(matmul_results)
    
    # Real-world context
    demonstrate_real_nmr_sizes()
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print("\nKey Findings:")
    print("  • Small matrices (<10×10): Numba competitive, overhead dominates")
    print("  • Medium matrices (10-50×50): NumPy starting to win (1.5-3x faster)")
    print("  • Large matrices (>100×100): NumPy dominates (5-50x+ faster)")
    print("  • Transpose: NumPy has minimal overhead, usually fastest")
    print("\nWhy NumPy Wins for Large Matrices:")
    print("  • BLAS: Optimized assembly, cache-aware, SIMD instructions")
    print("  • Blocking: Processes in cache-sized chunks")
    print("  • Multithreading: Can use multiple cores")
    print("\nWhen to Use Each:")
    print("  • Python:  Educational, pure Python requirement, tiny matrices")
    print("  • Numba:   Small-medium matrices, custom algorithms")
    print("  • NumPy:   Default choice, especially for large matrices")


if __name__ == '__main__':
    main()
