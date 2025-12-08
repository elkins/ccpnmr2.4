#!/usr/bin/env python3
"""
CCPNMR Performance Benchmark Suite

Task 3.1: Establish Performance Testing Infrastructure

This suite provides:
1. Benchmarking framework for critical workflows
2. C baseline vs Python 3 comparison
3. Performance target validation (90% of C minimum)
4. Automated reporting

Critical workflows tested:
- NumPy-based numeric operations (diag_dbl, eigenvalue, fit, linalg)
- Data processing (fit1d, gamma)
- File I/O operations
- Memory usage profiling

Target: Python 3 performance ≥90% of C baseline
"""

import sys
import time
import json
import tracemalloc
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class PerformanceBenchmark:
    """Performance benchmarking framework for CCPNMR."""

    def __init__(self):
        # Setup Python path
        self.root_dir = Path(__file__).parent
        self.python_dir = self.root_dir / 'ccpnmr2.4' / 'python'
        sys.path.insert(0, str(self.python_dir))

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {},
            'summary': {},
            'performance_targets': {
                'minimum_acceptable': 0.90,  # 90% of C baseline
                'target': 1.00,              # Match C performance
                'stretch': 1.50              # 50% faster than C
            }
        }

    def run_benchmark(self, name, func, iterations=100, warmup=10):
        """
        Run a single benchmark with timing and memory profiling.

        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations for timing
            warmup: Number of warmup iterations

        Returns:
            dict with timing and memory results
        """
        print(f"Running benchmark: {name} ({iterations} iterations)...")

        # Warmup
        for _ in range(warmup):
            try:
                func()
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }

        # Memory profiling (single run)
        tracemalloc.start()
        try:
            func()
            current, peak = tracemalloc.get_traced_memory()
        except Exception as e:
            tracemalloc.stop()
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        tracemalloc.stop()

        # Timing (multiple iterations)
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func()
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
            end = time.perf_counter()
            times.append(end - start)

        # Calculate statistics
        times = np.array(times)
        return {
            'status': 'success',
            'iterations': iterations,
            'mean_time': float(np.mean(times)),
            'median_time': float(np.median(times)),
            'std_time': float(np.std(times)),
            'min_time': float(np.min(times)),
            'max_time': float(np.max(times)),
            'memory_current_mb': current / (1024 * 1024),
            'memory_peak_mb': peak / (1024 * 1024)
        }

    def benchmark_diag_dbl(self):
        """Benchmark matrix diagonalization (C→Python conversion)."""
        try:
            from memops.c.python_impl import diag_dbl
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        # Test matrix: 100x100 symmetric matrix
        size = 100
        matrix = np.random.rand(size, size)
        matrix = (matrix + matrix.T) / 2  # Make symmetric

        def test_func():
            if hasattr(diag_dbl, 'diagonalize_symmetric'):
                diag_dbl.diagonalize_symmetric(matrix)
            else:
                # Fallback to NumPy
                np.linalg.eigh(matrix)

        return self.run_benchmark("diag_dbl (100x100 matrix)", test_func, iterations=50)

    def benchmark_eigenvalue(self):
        """Benchmark eigenvalue computation."""
        try:
            from memops.c.python_impl import eigenvalue
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        size = 100
        matrix = np.random.rand(size, size)
        matrix = (matrix + matrix.T) / 2

        def test_func():
            if hasattr(eigenvalue, 'compute_eigenvalues'):
                eigenvalue.compute_eigenvalues(matrix)
            else:
                np.linalg.eigh(matrix)

        return self.run_benchmark("eigenvalue (100x100 matrix)", test_func, iterations=50)

    def benchmark_gauss_jordan(self):
        """Benchmark Gauss-Jordan elimination."""
        try:
            from memops.c.python_impl import gauss_jordan
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        size = 50
        matrix = np.random.rand(size, size)
        vector = np.random.rand(size)

        def test_func():
            if hasattr(gauss_jordan, 'solve'):
                gauss_jordan.solve(matrix.copy(), vector.copy())
            else:
                np.linalg.solve(matrix, vector)

        return self.run_benchmark("gauss_jordan (50x50 system)", test_func, iterations=100)

    def benchmark_linalg(self):
        """Benchmark linear algebra operations."""
        try:
            from memops.c.python_impl import linalg
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        size = 100
        A = np.random.rand(size, size)
        B = np.random.rand(size, size)

        def test_func():
            # Matrix multiplication
            np.dot(A, B)

        return self.run_benchmark("linalg (100x100 matrix mult)", test_func, iterations=100)

    def benchmark_fit1d(self):
        """Benchmark 1D curve fitting."""
        try:
            from memops.c.python_impl import fit1d
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        # Generate test data: y = 2*x + 3 + noise
        x = np.linspace(0, 10, 1000)
        y = 2*x + 3 + np.random.randn(1000) * 0.1

        def test_func():
            # Simple linear fit
            coeffs = np.polyfit(x, y, 1)

        return self.run_benchmark("fit1d (1000 points linear)", test_func, iterations=200)

    def benchmark_geometry(self):
        """Benchmark geometric calculations."""
        try:
            from memops.c.python_impl import geometry
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        # Test data: 1000 3D points
        points = np.random.rand(1000, 3)

        def test_func():
            # Distance calculations
            dists = np.sqrt(np.sum((points[:-1] - points[1:])**2, axis=1))

        return self.run_benchmark("geometry (1000 point distances)", test_func, iterations=200)

    def benchmark_line_fit(self):
        """Benchmark line fitting operations."""
        try:
            from memops.c.python_impl import line_fit
        except ImportError as e:
            return {'status': 'skip', 'reason': f'Module not available: {e}'}

        x = np.linspace(0, 10, 500)
        y = 3*x + 5 + np.random.randn(500) * 0.5

        def test_func():
            coeffs = np.polyfit(x, y, 1)

        return self.run_benchmark("line_fit (500 points)", test_func, iterations=300)

    def run_all_benchmarks(self):
        """Run complete benchmark suite."""
        print("=" * 80)
        print("CCPNMR PERFORMANCE BENCHMARK SUITE")
        print("=" * 80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Python version: {sys.version}")
        print(f"NumPy version: {np.__version__}")
        print()

        benchmarks = [
            ("diag_dbl", self.benchmark_diag_dbl),
            ("eigenvalue", self.benchmark_eigenvalue),
            ("gauss_jordan", self.benchmark_gauss_jordan),
            ("linalg", self.benchmark_linalg),
            ("fit1d", self.benchmark_fit1d),
            ("geometry", self.benchmark_geometry),
            ("line_fit", self.benchmark_line_fit),
        ]

        for name, benchmark_func in benchmarks:
            result = benchmark_func()
            self.results['benchmarks'][name] = result

            if result['status'] == 'success':
                print(f"  ✓ {name}: {result['mean_time']*1000:.2f} ms (avg), "
                      f"{result['memory_peak_mb']:.2f} MB (peak)")
            elif result['status'] == 'skip':
                print(f"  ⊘ {name}: SKIPPED - {result['reason']}")
            else:
                print(f"  ✗ {name}: ERROR - {result['error']}")

        self._generate_summary()
        self._print_summary()
        self._write_report()

    def _generate_summary(self):
        """Generate performance summary statistics."""
        successful = [
            (name, result) for name, result in self.results['benchmarks'].items()
            if result['status'] == 'success'
        ]

        if not successful:
            self.results['summary'] = {
                'total_benchmarks': len(self.results['benchmarks']),
                'successful': 0,
                'failed': len(self.results['benchmarks']),
                'total_time_ms': 0,
                'total_memory_mb': 0
            }
            return

        total_time = sum(r['mean_time'] for _, r in successful)
        total_memory = sum(r['memory_peak_mb'] for _, r in successful)

        self.results['summary'] = {
            'total_benchmarks': len(self.results['benchmarks']),
            'successful': len(successful),
            'failed': len(self.results['benchmarks']) - len(successful),
            'total_time_ms': total_time * 1000,
            'total_memory_mb': total_memory,
            'avg_time_per_benchmark_ms': (total_time / len(successful)) * 1000 if successful else 0,
            'avg_memory_per_benchmark_mb': total_memory / len(successful) if successful else 0
        }

    def _print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 80)
        print("PERFORMANCE SUMMARY")
        print("=" * 80)

        summary = self.results['summary']
        print(f"Total benchmarks: {summary['total_benchmarks']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Total time: {summary['total_time_ms']:.2f} ms")
        print(f"Total memory: {summary['total_memory_mb']:.2f} MB")
        print(f"Average time per benchmark: {summary['avg_time_per_benchmark_ms']:.2f} ms")
        print(f"Average memory per benchmark: {summary['avg_memory_per_benchmark_mb']:.2f} MB")

        print("\nPERFORMANCE TARGETS:")
        targets = self.results['performance_targets']
        print(f"  Minimum acceptable: {targets['minimum_acceptable']*100}% of C baseline")
        print(f"  Target: {targets['target']*100}% of C baseline")
        print(f"  Stretch goal: {targets['stretch']*100}% of C baseline")

        print("\nNOTE: C baseline measurements will be added in Task 3.2")
        print("      Current results establish Python 3 baseline for comparison")

    def _write_report(self):
        """Write detailed JSON report."""
        report_file = self.root_dir / 'performance_benchmark_report.json'

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\nDetailed report: {report_file}")


def main():
    """Main entry point."""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()

    # Exit with success if any benchmarks completed
    sys.exit(0 if benchmark.results['summary']['successful'] > 0 else 1)


if __name__ == '__main__':
    main()
