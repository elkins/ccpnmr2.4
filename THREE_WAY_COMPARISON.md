# Three-Way Implementation Comparison Guide

## Overview

This repository includes **multiple implementation variants** for performance-critical modules:

1. **Pure Python** - Maximum compatibility, surprisingly competitive
2. **Numba-Accelerated** - JIT-compiled Python for numerical operations  
3. **C Extension** (original) - Fastest for some operations, requires compilation

**Strategy:** Pure Python + Numba provides excellent performance without compilation hassles.

## Quick Start

### Install Dependencies
```bash
pip install numpy numba
# Optional: scipy (for comparisons)
pip install scipy
```

### Run All Tests
```bash
# Test all 9 modules
cd tests
python3 run_three_way_comparison.py
```

### Run Specific Module
```bash
python3 run_three_way_comparison.py --module gauss_jordan
```

### Run Performance Benchmarks
```bash
# Individual module benchmarks
cd ccpnmr2.4/python/memops/c/python_impl
python3 benchmark_gauss_jordan.py
python3 benchmark_line_fit.py
python3 benchmark_geometry_sorts.py

cd ccpnmr2.4/python/ccpnmr/analysis/python_impl
python3 benchmark_contour.py
```

## Completed Modules (9)

| Module | Location | Pure Python | Numba | Tests |
|--------|----------|-------------|-------|-------|
| **mem_cache** | memops | ✅ | ✅ | ✅ |
| **geometry** | memops | ✅ | ✅ | ✅ |
| **sorts** | memops | ✅ | ✅ | ✅ |
| **gauss_jordan** | memops | ✅ | ✅ | ✅ |
| **line_fit** | memops | ✅ | ✅ | ✅ |
| **atom** | ccp | ✅ | ✅ | ✅ |
| **bond** | ccp | ✅ | ✅ | ✅ |
| **peak** | ccpnmr | ✅ | ✅ | ✅ |
| **contour** | ccpnmr | ✅ | ✅ + Cython | ✅ |

---

## Performance Summary

### When Numba Wins (Significant speedups)

**🏆 Contour Tracing:** 90-3200x faster
- Grid processing with nested loops
- Most dramatic improvement in the codebase
- Essential for real-time NMR visualization
- 100×100 noise pattern: **3208x speedup**

**🏆 Gauss-Jordan (small-medium matrices):** 4-64x faster
- 3×3 matrices: 3.8x speedup
- 10×10 matrices: 19.8x speedup  
- 50×50 matrices: 64x speedup
- Optimal for typical NMR linear systems

**🏆 Line Fitting (small datasets):** 2-5x faster
- 10 points: 2.3x, **beats NumPy 7.5x**
- 100 points: 4.5x, **beats NumPy 2.7x**
- Ideal for NMR peak fitting

**🏆 Sorting:** 4-37x faster
- Scales extremely well with data size
- 10 elements: 4.5x speedup
- 1000 elements: 37.5x speedup

**Geometry (selective):** 1.3-2.3x faster
- vectors_angle: 2.34x speedup
- vector_length: 1.28x speedup

### When Pure Python Wins

**Simple operations:**
- List comprehensions (cross_product: **Python 4.5x faster**)
- Dictionary operations (mem_cache basics)
- Inner products on small vectors (Python 1.7x faster)

**Small overhead operations:**
- Function call overhead dominates
- JIT compilation cost not amortized
- atom/bond transformations on individual objects

### When NumPy/SciPy Wins

**Large matrices (>20×20):**
- Gauss-Jordan 50×50: **NumPy 540x faster** than Python
- LAPACK-optimized routines dominate
- Production linear algebra

**Large datasets (>1000 points):**
- Line fitting 10000 points: **NumPy 13x faster** than Python
- Optimized Timsort vs heap sort: **5.6x faster**

---

## Key Findings

### Overall Strategy

1. **Numba for NMR-typical sizes:** Most NMR operations use small-medium datasets where Numba excels
2. **Pure Python stays competitive:** Surprising performance for simple operations
3. **NumPy for production math:** When available, use for large-scale linear algebra
4. **No C compilation needed:** Python + Numba provides 80-90% of performance gains

### Architecture Benefits

✅ **No build complexity:** `pip install numpy numba`  
✅ **Cross-platform:** Works on Windows/Mac/Linux without compiler  
✅ **Maintainable:** Pure Python code is easier to debug and modify  
✅ **Performance when needed:** Numba provides dramatic speedups for critical paths  
✅ **Gradual optimization:** Start with Python, add Numba where needed  

### When to Use Each Implementation

| Use Case | Recommendation | Why |
|----------|---------------|-----|
| Small datasets (<100 items) | **Numba** | Best performance, beats NumPy |
| Large datasets (>1000 items) | **NumPy/SciPy** | LAPACK optimization |
| Simple operations | **Pure Python** | Competitive, no overhead |
| Nested loops | **Numba** | Dramatic speedups (100-1000x) |
| Dict/object manipulation | **Pure Python** | CPython highly optimized |
| Production linear algebra | **NumPy** | Industry standard |
| Prototyping | **Pure Python** | Fast development |

---

## Example: Contour Tracing Performance

```
Grid: 100x100, Pattern: noise, Levels: 1
Iterations: 20

Python         Time: 202.92s  Ops/sec: 0.10
Numba          Time: 0.063s   Ops/sec: 316.17

Numba is 3207.88x faster! ⚡
```

## Example: Line Fitting Performance

```
Dataset: 10 points
Iterations: 10000

Python           Time: 0.032s   31 ops/sec
Numba            Time: 0.014s   71 ops/sec
NumPy polyfit    Time: 0.106s   9 ops/sec
SciPy linregress Time: 0.201s   5 ops/sec

Numba wins! (2.3x faster than Python, 7.5x faster than NumPy)
```

---

## Implementation Patterns

### Pure Python Example (line_fit.py)
```python
def line_fit(x, y, sigma=None):
    """Weighted least squares fit."""
    n = len(x)
    # Compute sums
    s = float(n)
    sx = sum(x)
    sy = sum(y)
    # ... more pure Python
    return {'a': a, 'b': b, 'std_a': std_a, ...}
```

### Numba Example (line_fit_numba.py)
```python
@jit(nopython=True)
def line_fit_numba(x, y, sigma=None):
    """JIT-compiled weighted least squares."""
    n = len(x)
    # Same algorithm, but JIT compiled
    # Works on NumPy arrays
    return (success, a, b, std_a, ...)
```

### High-Level API Wrapper
```python
class LineFitOps:
    @staticmethod
    def fit(x, y, sigma=None):
        # Convert to NumPy
        x_arr = np.asarray(x, dtype=np.float64)
        # Call JIT function
        result = line_fit_numba(x_arr, y_arr, sigma_arr)
        return result
```

---

## Testing

All modules have comprehensive test suites:

```bash
# Example: Testing gauss_jordan
cd ccpnmr2.4/python/memops/c/python_impl
python3 test_gauss_jordan.py -v

# Output:
# test_simple_2x2_system ... ok
# test_3x3_system ... ok
# test_matrix_inverse_2x2 ... ok
# test_singular_matrix ... ok
# test_consistency_perfect_line ... ok
# ...
# Ran 17 tests in 0.398s
# OK
```

---

## Recommendations

### For Production Use
✅ **Use NumPy/SciPy** for large-scale operations  
✅ **Use Numba** for small-medium NMR-typical datasets  
✅ **Use Pure Python** for prototyping and simple operations  

### For Development
✅ **Start with Pure Python** - Get it working first  
✅ **Add Numba where profiling shows bottlenecks**  
✅ **Keep both versions** - Fallback if Numba unavailable  

### For Distribution
✅ **No C compilation required** - pip install only  
✅ **Graceful degradation** - Falls back to Pure Python  
✅ **Cross-platform** - Works everywhere Python works  

---

## Next Steps

1. **Run the benchmarks** on your system to see results
2. **Try the examples** in `examples/` directory
3. **Read module documentation** for specific implementations
4. **Check README_MODERNIZATION.md** for overall progress

For questions or contributions, see the main README.
