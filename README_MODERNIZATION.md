# CcpNmr Modernization Project

**Experimental fork of CcpNmr 2.4 with goals:**
- 🔧 **Replace C extensions with modern Python** (NumPy, Numba, etc.)
- 📦 **Simplify installation** (no C compiler required)
- 🚀 **Maintain performance** through optimized Python libraries
- 🐍 **Full Python 3 compatibility**
- 🔬 **Preserve NMR functionality** for scientific use

## Branches:
- `analysis-phase` - Initial code analysis and planning
- `c-to-python-experiments` - C extension replacement trials  
- `performance-testing` - Benchmarking and optimization

## Approach:
1. **Analyze** existing C components and performance characteristics
2. **Replace** C code with Python + modern scientific libraries
3. **Verify** NMR functionality remains correct
4. **Optimize** performance-critical sections

[Original CcpNmr 2.4](https://github.com/VuisterLab/ccpnmr2.4)

---

## 📂 Python Implementation Structure

Python implementations are organized to mirror the original C codebase structure:

| C Code Location | Python Implementation | Purpose |
|----------------|----------------------|---------|
| `c/ccp/structure/` | `python/ccp/c/python_impl/` | Molecular structure operations |
| `c/memops/global/` | `python/memops/c/python_impl/` | Core utilities |
| `c/ccpnmr/analysis/` | `python/ccpnmr/analysis/python_impl/` | NMR analysis |

**Pattern:** Each module has `<module>.py` (pure Python), `<module>_numba.py` (JIT-compiled), and `test_<module>.py` (tests).

### Current Modules

#### CCP/STRUCTURE (Molecular structure operations)
📁 `ccpnmr2.4/python/ccp/c/python_impl/`
- ✅ **atom** - Geometric transformations, distance calculations
- ✅ **bond** - Line segment geometry, intersections

#### MEMOPS/GLOBAL (Core utilities)
📁 `ccpnmr2.4/python/memops/c/python_impl/`
- ✅ **mem_cache** - Dictionary-based caching
- ✅ **geometry** - Vector operations (length, dot/cross product, angles, rotations)
- ✅ **sorts** - Heap sort algorithm
- ✅ **gauss_jordan** - Linear algebra, matrix inversion, solving Ax=b
- ✅ **line_fit** - Weighted linear least squares regression

#### CCPNMR/ANALYSIS (NMR analysis)
📁 `ccpnmr2.4/python/ccpnmr/analysis/python_impl/`
- ✅ **peak** - Peak region checking, validation
- ✅ **contour** - Marching squares contour tracing (Python + Numba + Cython)

---

## 🧪 Testing & Benchmarking

### Run All Tests
```bash
cd tests
python3 run_three_way_comparison.py
```

### Run Specific Module
```bash
python3 run_three_way_comparison.py --module atom
```

### Run with Benchmarks
```bash
python3 run_three_way_comparison.py --module bond --benchmark
```

### Module-Specific Benchmarks
```bash
# Geometry and sorts
cd ccpnmr2.4/python/memops/c/python_impl
python benchmark_geometry_sorts.py

# Gauss-Jordan linear algebra
cd ccpnmr2.4/python/memops/c/python_impl
python benchmark_gauss_jordan.py

# Line fitting
cd ccpnmr2.4/python/memops/c/python_impl
python benchmark_line_fit.py

# Contour tracing
cd ccpnmr2.4/python/ccpnmr/analysis/python_impl
python benchmark_contour.py
```

---

## 🎯 Why Three Locations?

We maintain the original architectural separation:
- **Structure** (ccp): Atomic and molecular geometry
- **Utilities** (memops): Generic algorithms and caching
- **Analysis** (ccpnmr): NMR-specific processing

This makes it easy to navigate: "Where's `atom.c`? → Look in `ccp/c/python_impl/atom.py`"

---

## 📊 Performance Results

### Three-Way Comparison Test Results
✅ **All 9 modules passing functional tests:**
- `mem_cache` - Dictionary operations work correctly
- `atom` - Geometric transformations validated
- `bond` - Line segment operations verified
- `peak` - Peak position handling correct
- `geometry` - Vector math operations verified
- `sorts` - Heap sort algorithm validated
- `gauss_jordan` - Linear equation solving validated
- `line_fit` - Statistical fitting verified
- `contour` - Contour tracing validated

### Gauss-Jordan Linear Algebra (Python vs Numba vs NumPy)
| Matrix Size | Numba Speedup vs Python | NumPy vs Python | Notes |
|-------------|-------------------------|-----------------|-------|
| 3×3 | 3.8x faster | 2.3x faster | Numba wins small matrices |
| 5×5 | 8.1x faster | 7.3x faster | Both significantly faster |
| 10×10 | 19.8x faster | **34.1x faster** | NumPy starts dominating |
| 20×20 | 41x faster | **163x faster** | LAPACK optimization clear |
| 50×50 | 64x faster | **540x faster** | NumPy dominant for large |

**Key Finding:** Numba excels for small-medium matrices (typical NMR use), NumPy's LAPACK dominates for large systems.

### Line Fitting (Python vs Numba vs NumPy vs SciPy)
| Dataset Size | Numba vs Python | Best Overall | Notes |
|--------------|-----------------|--------------|-------|
| 10 points | 2.3x faster | **Numba** | Beats NumPy 7.5x |
| 100 points | 4.5x faster | **Numba** | Beats NumPy 2.7x |
| 1000 points | 5.0x faster | **NumPy** | LAPACK takes lead |
| 10000 points | 8.9x faster | **NumPy** | NumPy 1.7x faster than Numba |

**Key Finding:** Numba optimal for typical NMR dataset sizes (10-100 points), NumPy polyfit dominates for large datasets.

### Geometry Operations (Python vs Numba)
| Operation | Winner | Speedup | Notes |
|-----------|--------|---------|-------|
| Vector Length | Numba | 1.28x | Close performance |
| Inner Product | Python | 1.71x | Simple list operations |
| Cross Product | Python | 4.50x | List comprehension wins |
| Normalize Vector | Python | 1.03x | Essentially tied |
| Vectors Angle | Numba | 2.34x | Trig operations benefit from JIT |

**Key Finding:** Python's native list operations are highly optimized; Numba wins on complex math.

### Sorting Operations (Python vs Numba)
| Array Size | Numba Speedup | Python Heap Sort | Numba Heap Sort |
|------------|---------------|------------------|-----------------|
| 10 elements | 4.49x | 0.044s | 0.010s |
| 100 elements | 22.27x | 0.089s | 0.004s |
| 1000 elements | 37.50x | 0.141s | 0.004s |

**Note:** Python's built-in Timsort is 5.56x faster than our heap sort implementation. Use built-in `sorted()` for production.

### Contour Tracing (Python vs Numba)
| Grid Size | Pattern | Numba Speedup | Notes |
|-----------|---------|---------------|-------|
| 50×50 | Gradient | 90x | Simple data |
| 100×100 | Gradient | 151x | Scales well |
| 200×200 | Gradient | 220x | Best scaling |
| 100×100 | Peaks | 597x | Complex patterns |
| 100×100 | Noise | **3208x** | Worst-case for Python |

**Key Finding:** Numba provides dramatic speedups (90-3200x) for nested loop algorithms like contour tracing.

### Performance Strategy
- **Use Python:** Dictionary operations, simple list comprehensions, object manipulation
- **Use Numba:** Nested loops, numerical arrays, complex mathematical operations, small-medium datasets
- **Use NumPy/SciPy:** Large matrices (>20×20), large datasets (>1000 points), production linear algebra
- **Use Built-ins:** Python's `sorted()`, `min()`, `max()` are highly optimized

---

## 📈 Progress Summary

**Modules Completed: 9 / ~50+ C modules**

### By Category:
- **Structure Operations (ccp):** 2/8 modules (25%)
- **Core Utilities (memops):** 5/30+ modules (17%)
- **NMR Analysis (ccpnmr):** 2/15+ modules (13%)

### Implementation Pattern:
Each module includes:
- Pure Python implementation
- Numba JIT-compiled version
- Comprehensive test suite (100% passing)
- Performance benchmarks vs NumPy/SciPy
- Documentation

### Performance Wins:
- **Numba dominates** small-medium numerical operations (2-64x speedup)
- **Python competitive** for simple operations (list/dict manipulation)
- **NumPy/SciPy best** for large-scale linear algebra
- **Contour tracing** sees most dramatic improvement (90-3200x with Numba)
