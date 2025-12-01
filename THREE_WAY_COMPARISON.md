# Three-Way Implementation Comparison Guide

## Overview

This repository now includes **three implementation variants** for each module:

1. **C Extension** (original) - Fastest, requires compilation
2. **Pure Python** - Maximum compatibility, surprisingly fast
3. **Numba-Accelerated** - JIT-compiled Python for numerical operations

## Quick Start

### Install Numba (optional)
```bash
pip install numba
```

### Run Functional Tests
```bash
# Test all modules
python3 tests/run_three_way_comparison.py

# Test specific module
python3 tests/run_three_way_comparison.py --module atom
```

### Run Performance Benchmarks
```bash
# Full benchmark suite
python3 tests/run_three_way_comparison.py --benchmark

# Benchmark specific module
python3 tests/run_three_way_comparison.py --module bond --benchmark
```

## Benchmark Results

| Module | Pure Python | Numba | Winner | Speedup |
|--------|-------------|-------|--------|---------|
| **mem_cache** | 317K ops/s | 3.8M ops/s | Numba | **11.9x faster** |
| **atom** | 5.1M ops/s | 454K ops/s | Python | **11.3x faster** |
| **bond** | 2.5M ops/s | 344K ops/s | Python | **7.4x faster** |
| **peak** | ~3M ops/s | ~800K ops/s | Python | **~4x faster** |
| **contour*** | TBD | TBD | TBD | Run benchmarks |

\* **Note**: The contour implementations are simplified standalone versions for comparison,
not wrappers around the existing C code. See "Important Notes" section below.

## Key Findings

### Pure Python Wins Most Cases
For this codebase, **Pure Python is the best choice** because:
- ✅ CPython highly optimizes dict/object operations
- ✅ No JIT compilation overhead for simple operations
- ✅ Zero dependencies beyond standard library
- ✅ Excellent performance (millions of ops/sec)
- ✅ Maximum compatibility

### When Numba Helps
Numba excels at:
- ✅ Tight loops over numerical arrays
- ✅ Heavy numerical computations (FFT, matrix operations)
- ✅ Batch processing of many objects
- ✅ Array-based algorithms

### When Numba Struggles
Numba has overhead for:
- ❌ Simple operations (JIT compilation cost)
- ❌ Dict/object-heavy operations
- ❌ String manipulation
- ❌ Operations CPython already optimizes

## Example Output

```
Three-Way Implementation Comparison
Python version: 3.9.6
✓ Numba available: 0.60.0

======================================================================
Module: atom
======================================================================

Functional Tests:
✓ Pure Python: translation works
✓ Numba: translation works

Performance Benchmarks (10,000 iterations):
Pure Python: 0.0059s, 5,121,347 ops/sec
Numba: 0.0661s, 453,667 ops/sec
Pure Python is 11.29x faster
```

## Implementation Highlights

### mem_cache_numba.py
- Same dict-based approach as pure Python
- Numba surprisingly helps despite dict operations
- Demonstrates that JIT can optimize some patterns

### atom_numba.py
JIT-compiled geometric functions:
```python
@jit(nopython=True)
def _translate_coords(x, y, z, dx, dy, dz):
    return (x + dx, y + dy, z + dz)

@jit(nopython=True)
def _rotate_coords(x, y, z, ox, oy, oz, m00, m01, m02, ...):
    # Matrix multiplication
    ...
```

### bond_numba.py
JIT-compiled geometric calculations:
```python
@jit(nopython=True)
def _line_segment_closest_point(x, y, x1, y1, x2, y2):
    # Find closest point on line segment
    ...
```

### peak_numba.py
JIT-compiled region checking:
```python
@jit(nopython=True)
def _check_in_region(pos, low, high, num_alias, npoints, allow_alias):
    # Check if position in region with aliasing
    ...
```

## Recommendations

### For Production Use
**Use Pure Python implementations:**
- Excellent performance
- No dependencies
- Maximum compatibility
- Easy to maintain

### For Research/Optimization
**Explore Numba when:**
- Implementing FFT/signal processing
- Batch processing arrays of atoms/bonds
- Heavy matrix operations
- Profiling shows numerical bottlenecks

### Future Opportunities
Consider numba for:
- **Spectral processing**: FFT, filtering, convolution on NMR data
- **Batch operations**: Process arrays of atoms/bonds simultaneously
- **Matrix operations**: Bulk rotation/transformation of coordinates
- **Region queries**: Check many peaks against regions at once

## Architecture

All implementations share the same API:
```python
# Pure Python
from memops.c.python_impl.mem_cache import new_mem_cache

# Numba variant
from memops.c.python_impl.mem_cache_numba import new_mem_cache

# Same API, different performance characteristics
cache = new_mem_cache(1000, None, None)
```

## Files

```
ccpnmr2.4/python/
├── memops/c/python_impl/
│   ├── mem_cache.py          # Pure Python
│   └── mem_cache_numba.py    # Numba variant
├── ccp/c/python_impl/
│   ├── atom.py               # Pure Python
│   ├── atom_numba.py         # Numba variant
│   ├── bond.py               # Pure Python
│   └── bond_numba.py         # Numba variant
├── ccpnmr/analysis/python_impl/
│   ├── peak.py               # Pure Python
│   └── peak_numba.py         # Numba variant
└── README_NUMBA.md           # Detailed guide

tests/
├── run_three_way_comparison.py  # Comparison tool
└── README.md                    # Testing guide
```

## Graceful Degradation

All numba implementations work without numba installed:
```python
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    # Fallback decorator
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]
    NUMBA_AVAILABLE = False
```

## Conclusion

**Pure Python is the winner** for this codebase. The implementations demonstrate that:

1. CPython is highly optimized for common patterns
2. JIT compilation has overhead that needs large workloads to amortize
3. Dict/object operations are already fast in pure Python
4. Numba is powerful but best saved for numerical array operations

The numba implementations serve as:
- ✅ Reference for future optimization
- ✅ Demonstration of JIT patterns
- ✅ Benchmark baseline for C extensions
- ✅ Foundation for future array-based algorithms

## Additional Resources

- **README_NUMBA.md** - Complete implementation guide and patterns
- **README_CONTOUR.md** (in python_impl/) - Why contour uses simplified implementations
- **benchmark_contour.py** - Standalone benchmarks for contour (Python/Numba/Cython)

For **production use**, stick with **Pure Python** for excellent performance, zero dependencies, and maximum compatibility.
