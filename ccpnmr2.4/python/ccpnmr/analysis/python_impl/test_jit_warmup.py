"""
Test to demonstrate Numba JIT compilation overhead and warmup effectiveness.
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from contour_numba import ContourTracer

def create_test_data(size):
    """Create simple gradient data."""
    data = []
    for y in range(size):
        row = []
        for x in range(size):
            row.append(float(x + y) / size)
        data.append(row)
    return data


def test_first_vs_subsequent_calls():
    """Test timing difference between first call (JIT) and subsequent calls."""
    print("Testing Numba JIT compilation overhead...")
    print("=" * 60)
    
    size = 100
    data = create_test_data(size)
    level = 0.5
    
    # First call - includes JIT compilation
    tracer1 = ContourTracer(size, size)
    tracer1.set_data(data)
    
    start = time.perf_counter()
    result1 = tracer1.trace_level(level)
    first_time = time.perf_counter() - start
    
    print(f"First call (with JIT compilation): {first_time*1000:.2f} ms")
    
    # Second call - JIT already compiled
    start = time.perf_counter()
    result2 = tracer1.trace_level(level)
    second_time = time.perf_counter() - start
    
    print(f"Second call (JIT compiled):        {second_time*1000:.2f} ms")
    
    # Third call
    start = time.perf_counter()
    result3 = tracer1.trace_level(level)
    third_time = time.perf_counter() - start
    
    print(f"Third call (JIT compiled):         {third_time*1000:.2f} ms")
    
    print("\n" + "=" * 60)
    print(f"JIT overhead: {(first_time - second_time)*1000:.2f} ms")
    print(f"First call is {first_time/second_time:.1f}x slower than subsequent calls")
    print("=" * 60)
    
    # Verify warmup strategy
    print("\nTesting warmup strategy...")
    print("-" * 60)
    
    # New tracer with 3 warmup iterations (as in benchmark)
    tracer2 = ContourTracer(size, size)
    tracer2.set_data(data)
    
    # Warmup
    warmup_start = time.perf_counter()
    for _ in range(3):
        tracer2.trace_level(level)
    warmup_time = time.perf_counter() - warmup_start
    
    print(f"Warmup (3 iterations): {warmup_time*1000:.2f} ms")
    
    # Now benchmark (should be fast)
    iterations = 10
    start = time.perf_counter()
    for _ in range(iterations):
        tracer2.trace_level(level)
    benchmark_time = time.perf_counter() - start
    
    print(f"Benchmark (10 iterations): {benchmark_time*1000:.2f} ms")
    print(f"Average per call: {(benchmark_time/iterations)*1000:.2f} ms")
    print("\n✓ Warmup ensures JIT overhead is NOT included in benchmark")


if __name__ == '__main__':
    test_first_vs_subsequent_calls()
