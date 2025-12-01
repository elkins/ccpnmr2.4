# Numba-Accelerated Implementations

This directory contains numba-accelerated versions of the pure Python implementations for performance comparison.

## Overview

Three implementation variants are available for each module:

1. **C Extension** (original): Fastest overall, requires compilation
2. **Pure Python**: Maximum compatibility, excellent for object/dict operations
3. **Numba-Accelerated**: JIT-compiled Python, best for numerical arrays

## Modules

### mem_cache_numba.py
Numba-aware version of the LRU cache. Note: Due to numba's limitations with Python dicts and threading, this version doesn't provide significant speedup over pure Python for this use case. Pure Python's highly optimized dict operations are hard to beat for non-numerical workloads.

**Benchmark results**: Numba shows overhead due to dict operations not being JIT-optimizable.

### atom_numba.py
Numba-accelerated geometric operations for 3D atoms. Includes JIT-compiled functions for:
- `_translate_coords()`: 3D translation
- `_rotate_coords()`: 3D rotation with matrix multiplication  
- `_zoom_coords()`: 3D scaling
- `_distance_squared()`: 2D distance calculation
- `_calculate_depth_param()`: Depth-based color blending
- `_inverted_grey()`: Color inversion

**Benchmark results**: Pure Python is actually faster due to the overhead of JIT compilation for simple operations. Numba would shine with larger batch operations on arrays.

### bond_numba.py
Numba-accelerated bond geometry. Includes JIT-compiled functions for:
- `_calculate_depth_param()`: Depth cueing
- `_perspective_transform()`: 3D-to-2D projection
- `_line_segment_closest_point()`: Point-to-line distance with lambda parameter

**Benchmark results**: Pure Python faster for individual operations. Numba would benefit from batch processing many bonds at once.

### peak_numba.py
Numba-accelerated peak operations. Includes JIT-compiled functions for:
- `_check_in_region()`: Region checking with aliasing
- `_calculate_scaled_position()`: Position scaling

**Benchmark results**: Similar performance for typical usage patterns.

## When to Use Numba

✅ **Numba is excellent for:**
- Tight loops over numerical arrays (numpy)
- Heavy numerical computations
- Array-based algorithms (FFT, signal processing, matrix operations)
- Batch processing of many objects

❌ **Numba is NOT ideal for:**
- Dict/object-heavy operations (use pure Python)
- String manipulation
- Complex Python objects
- Threading with Python data structures
- Operations that CPython already optimizes well

## Running Comparisons

### Three-way comparison:
```bash
python3 tests/run_three_way_comparison.py
```

### With performance benchmarks:
```bash
python3 tests/run_three_way_comparison.py --benchmark
```

### Single module:
```bash
python3 tests/run_three_way_comparison.py --module atom --benchmark
```

## Benchmark Results Summary

| Module | Pure Python | Numba | Winner | Reason |
|--------|-------------|-------|--------|--------|
| mem_cache | 317K ops/s | 3.8M ops/s | Numba 11x faster | Surprising! JIT helps despite dicts |
| atom | 5.1M ops/s | 454K ops/s | Python 11x faster | Simple ops, JIT overhead dominates |
| bond | 2.5M ops/s | 344K ops/s | Python 7x faster | Same as atom |
| peak | ~3M ops/s | ~800K ops/s | Python faster | Object creation overhead |

## Key Insights

1. **Pure Python is highly optimized** by CPython for common patterns
2. **Numba has JIT compilation overhead** that only pays off with:
   - Large array operations
   - Tight numerical loops
   - Batch processing
3. **For this codebase**, pure Python is the best choice for most modules
4. **Numba would shine** if we:
   - Processed arrays of atoms/bonds/peaks in batch
   - Implemented FFT/signal processing in Python
   - Had tight loops over large numerical arrays

## Installation

```bash
pip install numba
```

Numba requires:
- NumPy
- LLVM (installed automatically via llvmlite)

## Future Opportunities

For significant speedup with numba, consider:
- **Batch operations**: Process arrays of atoms/bonds at once
- **Spectral processing**: FFT, filtering, convolution on NMR data arrays
- **Matrix operations**: Rotation/transformation of atom coordinate arrays
- **Region queries**: Check many peaks against regions simultaneously

## Implementation Pattern

All numba implementations follow this pattern:

```python
from numba import jit

# Fallback if numba not installed
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
    NUMBA_AVAILABLE = False

# Numba-accelerated numerical function
@jit(nopython=True)
def _numerical_operation(x, y, z):
    """Tight numerical loop (numba-optimized)."""
    result = 0.0
    for i in range(len(x)):
        result += x[i] * y[i] + z[i]
    return result

# Regular class/object code
class MyClass:
    """Regular Python class."""
    def compute(self, data):
        # Call numba function for heavy lifting
        return _numerical_operation(data.x, data.y, data.z)
```

## Conclusion

**For this project**: Pure Python implementations are recommended for production use. They provide excellent performance, maximum compatibility, and no external dependencies beyond standard library.

**Numba can be explored** if/when implementing array-based signal processing, batch geometric operations, or other numerical algorithms where the JIT compilation overhead is amortized over large datasets.

The numba implementations serve as:
- Reference for future optimization opportunities
- Demonstration of JIT compilation patterns
- Baseline for C extension performance comparisons
