"""
Benchmark script for comparing Gauss-Jordan implementations.

Compares pure Python, Numba JIT, and NumPy's linalg.solve performance
across different matrix sizes.
"""

import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import gauss_jordan
import gauss_jordan_numba

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not available, skipping NumPy comparison")


def create_test_matrix(n):
    """Create a test n×n matrix that is well-conditioned."""
    # Create a diagonally dominant matrix for numerical stability
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(float(n + 10))  # Diagonal dominance
            else:
                row.append(float((i + j) % 5 + 1))
        matrix.append(row)
    return matrix


def create_test_vector(n):
    """Create a test n-element vector."""
    return [float(i + 1) for i in range(n)]


def benchmark_function(func, *args, iterations=100, warmup=5):
    """Benchmark a function with warmup iterations."""
    # Warmup
    for _ in range(warmup):
        func(*args)
    
    # Actual timing
    start = time.time()
    for _ in range(iterations):
        func(*args)
    end = time.time()
    
    elapsed = end - start
    ops_per_sec = iterations / elapsed if elapsed > 0 else 0
    
    return elapsed, ops_per_sec


def print_comparison(name, time_py, time_nb, time_np=None):
    """Print comparison results."""
    print(f"\n{name}:")
    print(f"  Python: {time_py:.4f}s, {1/time_py*100:,.0f} ops/sec")
    print(f"  Numba:  {time_nb:.4f}s, {1/time_nb*100:,.0f} ops/sec")
    
    if time_np is not None:
        print(f"  NumPy:  {time_np:.4f}s, {1/time_np*100:,.0f} ops/sec")
    
    if time_nb < time_py:
        speedup = time_py / time_nb
        print(f"  Numba is {speedup:.2f}x faster than Python")
    else:
        speedup = time_nb / time_py
        print(f"  Python is {speedup:.2f}x faster than Numba")
    
    if time_np is not None:
        if time_np < time_py:
            speedup = time_py / time_np
            print(f"  NumPy is {speedup:.2f}x faster than Python")
        if time_np < time_nb:
            speedup = time_nb / time_np
            print(f"  NumPy is {speedup:.2f}x faster than Numba")


def benchmark_solve(n, iterations):
    """Benchmark solving a linear system of size n×n."""
    print(f"\n{'='*60}")
    print(f"SOLVING LINEAR SYSTEM: {n}×{n} matrix")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}")
    
    # Create test data
    a = create_test_matrix(n)
    b = create_test_vector(n)
    
    # Python version
    def solve_py():
        a_copy = [row[:] for row in a]
        b_copy = b[:]
        return gauss_jordan.solve_linear_system(a_copy, b_copy)
    
    time_py, _ = benchmark_function(solve_py, iterations=iterations)
    
    # Numba version
    def solve_nb():
        a_copy = [row[:] for row in a]
        b_copy = b[:]
        return gauss_jordan_numba.solve_linear_system(a_copy, b_copy)
    
    time_nb, _ = benchmark_function(solve_nb, iterations=iterations)
    
    # NumPy version (for comparison)
    time_np = None
    if NUMPY_AVAILABLE:
        a_np = np.array(a, dtype=np.float64)
        b_np = np.array(b, dtype=np.float64)
        
        def solve_np():
            return np.linalg.solve(a_np, b_np)
        
        time_np, _ = benchmark_function(solve_np, iterations=iterations)
    
    print_comparison(f"solve_{n}x{n}", time_py, time_nb, time_np)


def benchmark_inverse(n, iterations):
    """Benchmark computing matrix inverse of size n×n."""
    print(f"\n{'='*60}")
    print(f"MATRIX INVERSE: {n}×{n} matrix")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}")
    
    # Create test data
    a = create_test_matrix(n)
    
    # Python version
    def inverse_py():
        a_copy = [row[:] for row in a]
        return gauss_jordan.matrix_inverse(a_copy)
    
    time_py, _ = benchmark_function(inverse_py, iterations=iterations)
    
    # Numba version
    def inverse_nb():
        a_copy = [row[:] for row in a]
        return gauss_jordan_numba.matrix_inverse(a_copy)
    
    time_nb, _ = benchmark_function(inverse_nb, iterations=iterations)
    
    # NumPy version
    time_np = None
    if NUMPY_AVAILABLE:
        a_np = np.array(a, dtype=np.float64)
        
        def inverse_np():
            return np.linalg.inv(a_np)
        
        time_np, _ = benchmark_function(inverse_np, iterations=iterations)
    
    print_comparison(f"inverse_{n}x{n}", time_py, time_nb, time_np)


def main():
    """Run all benchmarks."""
    print("="*60)
    print("GAUSS-JORDAN BENCHMARK: Python vs Numba vs NumPy")
    print("="*60)
    
    # Small matrices (more iterations)
    benchmark_solve(3, iterations=1000)
    benchmark_inverse(3, iterations=1000)
    
    # Medium matrices
    benchmark_solve(5, iterations=500)
    benchmark_inverse(5, iterations=500)
    
    # Larger matrices (fewer iterations)
    benchmark_solve(10, iterations=100)
    benchmark_inverse(10, iterations=100)
    
    # Even larger
    benchmark_solve(20, iterations=20)
    benchmark_inverse(20, iterations=20)
    
    # Large matrices (very few iterations)
    benchmark_solve(50, iterations=5)
    benchmark_inverse(50, iterations=5)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("\nKey Findings:")
    print("• NumPy's LAPACK-based routines are highly optimized")
    print("• Numba provides good performance with pure Python code")
    print("• For production use, prefer NumPy's linalg.solve and linalg.inv")
    print("• Gauss-Jordan is educational but not optimal for large systems")
    print("="*60)


if __name__ == '__main__':
    main()
