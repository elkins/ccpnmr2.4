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
✅ **All modules passing functional tests:**
- `mem_cache` - Dictionary operations work correctly
- `atom` - Geometric transformations validated
- `bond` - Line segment operations verified
- `peak` - Peak position handling correct

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
- **Use Numba:** Nested loops, numerical arrays, complex mathematical operations
- **Use Built-ins:** Python's `sorted()`, `min()`, `max()` are highly optimized
