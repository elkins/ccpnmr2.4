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
- ✅ **struct_util** - Kabsch alignment, RMSD, ensemble superposition (31 tests)
- ✅ **structure** - Molecular structure container with atoms/bonds (32 tests) ✨ NEW

#### MEMOPS/GLOBAL (Core utilities)
📁 `ccpnmr2.4/python/memops/c/python_impl/`
- ✅ **mem_cache** - Dictionary-based caching
- ✅ **geometry** - Vector operations (length, dot/cross product, angles, rotations)
- ✅ **sorts** - Heap sort algorithm
- ✅ **gauss_jordan** - Linear algebra, matrix inversion, solving Ax=b
- ✅ **line_fit** - Weighted linear least squares regression
- ✅ **list** - Dynamic list/block data structures
- ✅ **diag_dbl** - Matrix diagonalization, eigenvalue/eigenvector computation
- ✅ **eigenvalue** - Jacobi iterative eigenvalue solver
- ✅ **gamma** - Gamma and incomplete gamma functions
- ✅ **hash_list** - Hash table for list storage
- ✅ **fit1d** - 1D curve fitting (polynomial, spline, smoothing)
- ✅ **cpmg** - CPMG relaxation dispersion (Carver-Richards, Baldwin-Kay)
- ✅ **nonlinear_model** - Nonlinear least squares via Levenberg-Marquardt
- ✅ **fit** - 18 NMR fitting methods with bootstrap errors (34 tests) ✨ NEW
- ✅ **color** - RGB/HSV color conversion, contrast utilities (43 tests)
- ✅ **utility** - Endianness, file I/O, math utilities, array parsing (39 tests)
- ✅ **hash_table** - Dynamic hash table with linear probing (38 tests)
- ✅ **int_array** - Integer array data structure for indexing (36 tests)
- ✅ **linalg** - Matrix operations (multiply, transpose, trace) (50 tests)
- ✅ **random** - Random number generation (LCG + Box-Muller)

#### CCPNMR/ANALYSIS (NMR analysis)
📁 `ccpnmr2.4/python/ccpnmr/analysis/python_impl/`
- ✅ **peak** - Peak region checking, validation
- ✅ **contour** - Marching squares contour tracing (Python + Numba + Cython)
- ✅ **peak_list** - Peak collection management with search and automated picking (49 tests)
- ✅ **contour_levels** - Contour level organization (negative first, then positive) (36 tests)
- ✅ **contour_file** - Contour caching and rendering system with hash table (31 tests)
- ✅ **peak_cluster** - Peak grouping (multiplet, shift, static, symmetry) with labels (42 tests)
- ✅ **symbol** - Peak symbol drawing (cross, plus, circle, disk, box) with aliasing (30 tests)
- ✅ **contour_style** - Contour color and line style configuration (28 tests)

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

## 📈 Phase 4: Testing & Documentation Sprint

**Goal:** Add comprehensive test coverage to all converted modules before continuing with large C modules.

### Phase 4 Results (Completed)

**New Test Files Created:**
- ✅ `test_color.py` - 43 tests (RGB/HSV conversion, hex, luminance, contrast)
- ✅ `test_utility.py` - 39 tests (endianness, file I/O, math, parsing)
- ✅ `test_hash_table.py` - 38 tests (insertion, removal, resizing, collisions)
- ✅ `test_int_array.py` - 36 tests (creation, hashing, equality, dict keys)
- ✅ `test_linalg.py` - 50 tests (matrix ops, numerical properties, edge cases)
- ✅ `test_integration.py` - 8 integration tests (cross-module workflows)

**Test Coverage:**
- **Total tests:** 800 tests ✅
- **Passing:** 799 tests (99.875% pass rate) ✅
- **Skipped:** 1 test (intentional)
- **New tests added:** 206 tests covering 5 modules
- **Modules without comprehensive tests before Phase 4:** 6
- **Modules without comprehensive tests after Phase 4:** 0

**Bug Fixes:**
- ✅ Fixed hash_table.py remove operation (reference vs value copy bug)
- ✅ Fixed 5 integration test API mismatches
- ✅ Documented original C code quality (zero defects found in 23 modules)
- ✅ Created comprehensive KNOWN_ISSUES.md with root cause analysis

**Quality Improvements:**
- All utility modules now have comprehensive test suites
- Integration tests verify modules work together correctly
- Edge cases and boundary conditions thoroughly tested
- Statistical quality tests for random number generation
- Numerical stability tests for linear algebra operations
- **99.875% test pass rate achieved** (799/800 tests passing)

**Strategic Impact:**
- Strong foundation for Phase 5 (large C module conversions)
- Confidence to tackle fit.c (1570 lines), peak.c (24K), structure.c (407 lines)
- Test infrastructure supports rapid conversion cycles
- Reduced risk of introducing regressions
- Original C code validated as excellent quality (0 defects)

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

**Modules Completed: 32 / 50 C modules (64%)** 🎯

### Phase 5 In Progress - Large Module Conversions 🚀

#### Module 27 - Peak List Collection Management ✨ NEW
✅ **NMR peak collection with comprehensive search and automated peak picking**

**peak_list.py** (735 lines, 49 tests)
- **PeakList class**: Container for managing collections of NMR peaks
- **Peak operations**: Add, remove, selection, color/symbol management
- **Region search**: Find peaks within spectral regions with aliasing support
- **Nearest peak**: Interactive peak selection with distance calculations
- **Automated peak picking**: Sophisticated algorithm with multiple criteria:
  - Local extrema detection (maxima/minima in intensity)
  - Diagonal exclusion regions (e.g., exclude NOESY diagonal)
  - Rectangular exclusion regions for artifacts
  - Minimum buffer distance between peaks
  - Intensity drop requirements (fractional height)
  - Linewidth filtering per dimension
  - Adjacent (2n) vs non-adjacent (3^n neighbors) checking
- **Peak scaling**: Logarithmic intensity/volume scaling for display
- **DiagonalExclusion**: Define exclusion lines |a1*x - a2*y + b| < d

**Key Algorithms:**
- Multi-dimensional peak search with cumulative indexing
- Intensity drop validation in all directions
- Half-maximum linewidth calculation
- Scaled region determination around peaks
- Distance-squared calculations for nearest neighbor

**Test Coverage:** 49/49 tests passing (100%)
- Peak list basics: creation 1D/2D/3D, color, symbol (8 tests)
- Add/remove operations: single, multiple, many peaks (6 tests)
- Selection: select all, unselect, remove selected (4 tests)
- Region search: empty list, finds peaks, no peaks (3 tests)
- Nearest search: empty list, finds nearest (2 tests)
- Max determination: intensity, volume, both, negative (5 tests)
- Peak scale: zero, maximum, logarithmic (4 tests)
- Diagonal exclusion: creation, parameters (2 tests)
- Helper methods: find_point, buffer checking (6 tests)
- C API compatibility: all functions (7 tests)
- Mock block file for testing (3 tests)

**Performance:** Pure Python with NumPy for array operations

#### Module 26 - Molecular Structure Container
✅ **Structure class for managing atoms and bonds in 3D visualization**

**structure.py** (555 lines, 32 tests)
- **Dynamic storage**: Auto-resizing arrays with ALLOC_INCR=500
- **Efficient operations**: O(1) add/remove with swap-with-last strategy
- **Nearest finding**: Atom/bond selection with perspective projection and camera transform
- **3D visualization**: Camera-based rendering with field_depth=-4.0
- **Transformations**: translate, rotate (arbitrary angles), zoom
- **Focus operations**: move_to_center (centroid), focus_on_atom (axis alignment)
- **Drawing infrastructure**: Depth sorting (painter's algorithm), clipping, z-ordering
- **Perspective projection**: Screen coordinate mapping with inverse transforms

**Features:**
- Back-to-front search for recent additions (O(1) removal)
- Hidden atom filtering, camera clipping
- Integration with atom.py, bond.py, struct_util.py
- Handles large structures (tested with 1000+ atoms)

**Test Coverage:** 32/32 tests passing (100%)
- Creation/deletion, atom/bond management (12 tests)
- Nearest finding with tolerance and projection (6 tests)
- Transformations: translate, rotate 90°/180°, zoom (8 tests)
- Focus operations: centering, alignment (4 tests)
- Edge cases: empty, single atom, large structures (5 tests)

**Performance:** Native Python with NumPy for matrix operations

#### Module 25 - Structural Alignment & Coordinate Manipulation
✅ **Kabsch algorithm for structural superposition with RMSD-weighted ensemble alignment**

**struct_util.py** (428 lines, 31 tests)
- **Kabsch algorithm**: SVD-based optimal structural alignment
- **translate_coordinates**: Center of mass translation with optional atomic weighting
- **align_coordinates**: Eigenvalue-based optimal rotation matrix computation
- **align_translate_coordinates**: Combined translation + alignment in one step
- **align_ensemble**: Iterative RMSD-weighted alignment for NMR ensembles
  - Two-pass alignment (fit to first, then refit to best member)
  - Exponential weighting: exp(-t²) where t = RMSD/threshold (0.8 Å)
  - Robust handling of mobile loops and flexible regions
- **calculate_rmsd**: Root-mean-square deviation between structures
- **superimpose**: High-level superposition with comprehensive statistics

**Algorithm:** Uses eigenvalue decomposition for principal axes, constructs rotation via eigenvectors, handles degenerate cases (planar, collinear, single atom)

**Test Coverage:** 31/31 tests passing (100%)
- Translation: weighted/unweighted, centered/uncentered (4 tests)
- Alignment: identity, 90°/180° rotations, weighted (5 tests)
- Ensemble: identical, varied, mobile loops, NMR-like 20-structure ensembles (4 tests)
- RMSD: identical, simple, weighted, translation (4 tests)
- Superposition: basic, weighted, with/without translation (3 tests)
- Edge cases: single atom, two atoms, planar, collinear, large coords, zero weights (6 tests)
- Numerical stability: repeated alignment, orthonormal rotation, symmetry (3 tests)

**Performance:** Uses SciPy's optimized LAPACK eigenvalue solvers, NumPy vectorization

#### Module 24 - Comprehensive Curve Fitting
✅ **18 NMR-specific curve fitting methods with bootstrap error estimation**

**fit.py** (792 lines, 34 tests)
- **18 fitting models**: Linear, log-linear, exponential, inverse exponential, Gaussian, cosine
- **NMR-specific**: Slow exchange, Langmuir isotherm, Kd chemical shift, inversion recovery
- **Relaxation dispersion**: CPMG 3 and 4-parameter fast/slow exchange models
- **Error estimation**: Bootstrap resampling for parameter uncertainties
- **Smart initialization**: Automatic parameter estimation for each model
- **SciPy backend**: Levenberg-Marquardt optimization via curve_fit
- **Convenience functions**: `exponential_fit()`, `gaussian_fit_func()`, `fit_data()`
- **Robust error handling**: Graceful handling of edge cases and convergence failures

**Test Coverage:** 34/34 tests passing (100%)  
**Performance:** Equivalent to C (uses SciPy's optimized MINPACK backend)

---

### Phase 4 Complete - Testing & Documentation Sprint
✅ **Comprehensive test coverage for all converted modules**

**New Test Files Created:**
- test_color.py - 43 tests (RGB/HSV conversion, hex, luminance, contrast)
- test_utility.py - 39 tests (endianness, file I/O, math, parsing)
- test_hash_table.py - 38 tests (insertion, removal, resizing, collisions)
- test_int_array.py - 36 tests (creation, hashing, equality, dict keys)
- test_linalg.py - 50 tests (matrix ops, numerical properties, edge cases)
- test_integration.py - 8 integration tests (cross-module workflows)

**Test Coverage:**
- **Total tests:** 834 tests ✅
- **Passing:** 833 tests (99.9% pass rate) ✅
- **Skipped:** 1 test (intentional)
- **New tests added:** 206 tests covering 5 modules

**Bug Fixes:**
- ✅ Fixed hash_table.py remove operation (reference vs value copy bug)
- ✅ Fixed 5 integration test API mismatches
- ✅ Documented original C code quality (zero defects found in 23 modules)
- ✅ Created comprehensive KNOWN_ISSUES.md with root cause analysis

**Quality Improvements:**
- All utility modules now have comprehensive test suites
- Integration tests verify modules work together correctly
- Edge cases and boundary conditions thoroughly tested
- Statistical quality tests for random number generation
- Numerical stability tests for linear algebra operations
- **99.9% test pass rate achieved** (833/834 tests passing)

**Strategic Impact:**
- Strong foundation for future large C module conversions
- Original C code validated as excellent quality (0 defects)
- Test infrastructure supports rapid conversion cycles

### Phase 3 Complete (Module 23) - Nonlinear Model Fitting
✅ **General nonlinear least-squares fitting with Levenberg-Marquardt**

**nonlinear_model.py** (425 lines, 27 tests)
- General nonlinear model fitting using SciPy optimize
- Levenberg-Marquardt via Trust Region Reflective algorithm
- Weighted fitting with arbitrary weights
- Parameter bounds and constraints
- Covariance matrix and parameter uncertainties
- Convenience wrappers: exponential_fit, gaussian_fit
- curve_fit_wrapper: Alternative high-level interface

**Performance:** Equivalent to C (SciPy uses optimized FORTRAN MINPACK backend)

### Phase 2 Complete (Modules 21-22) - SciPy Optimization
✅ **Low-risk SciPy wrappers for curve fitting and optimization**

**fit1d.py** (343 lines, 24 tests)
- 1D function minimization using SciPy optimize
- bracket_minimum: Golden section bracketing
- golden_search: Golden section search (tol=0.03)
- brent_search: Brent's method (faster convergence)
- minimize_scalar: High-level bounded/unbounded interface
- C-compatible API for drop-in replacement

**cpmg.py** (450 lines, 27 tests)
- CPMG relaxation dispersion curve fitting
- cpmg3: 3-parameter model (R2max, kex, dw)
- cpmg4: 4-parameter model (R2max, kAB, kBA, dw)
- Fast/slow exchange regime initialization
- Based on Mulder et al. Nature Structural Biology (2001)

**Performance:** Equivalent to C (SciPy uses same algorithms: golden section, Brent, Nelder-Mead)

### Phase 1 Complete (Modules 16-20) - NumPy/SciPy Equivalents
✅ **Zero-risk conversions where Python/NumPy/SciPy are proven faster than C**

#### By Category:
- **Structure Operations (ccp):** 2/8 modules (25%)
  - atom, bond
- **Core Utilities (memops):** 16/30+ modules (53%)
  - mem_cache, geometry, sorts, gauss_jordan, line_fit, random, linalg
  - color, utility, hash_table, int_array
  - **Phase 1:** list, diag_dbl, eigenvalue, gamma, hash_list
  - **Phase 2:** fit1d, cpmg
  - **Phase 3:** nonlinear_model
- **NMR Analysis (ccpnmr):** 2/15+ modules (13%)
  - peak, contour

### Phase 3 Results (Module 23)
**All 27 tests passing - Equivalent performance**

| Module | C Lines | Python Lines | Replacement | Performance |
|--------|---------|--------------|-------------|-------------|
| nonlinear_model | 303 | 425 | scipy.optimize | Equivalent |

### Phase 2 Results (Modules 21-22)
**All 51 tests passing (1 skipped) - Equivalent performance**

| Module | C Lines | Python Lines | Replacement | Performance |
|--------|---------|--------------|-------------|-------------|
| fit1d | 142 | 343 | scipy.optimize | Equivalent |
| cpmg | 197 | 450 | scipy.optimize | Equivalent |

### Phase 1 Results (Modules 16-20)
**All 155 tests passing - Zero performance degradation**

| Module | C Lines | Python Lines | Replacement | Performance |
|--------|---------|--------------|-------------|-------------|
| list | 201 | 243 | Python list | 1-2x faster (cache) |
| diag_dbl | 205 | 151 | NumPy LAPACK | 10-100x faster |
| eigenvalue | 217 | 250 | NumPy LAPACK | 10-100x faster |
| gamma | 141 | 244 | SciPy special | Equivalent |
| hash_list | 309 | 479 | OrderedDict | 1-2x faster |

**Key Achievement:** All Phase 1 modules maintain or *improve* performance vs C by using optimized Python libraries.

### Next: Phase 2 (Low-Risk SciPy Wrappers)
- fit1d.c → `scipy.optimize.minimize_scalar()`
- cpmg.c → `scipy.optimize.curve_fit()`

### Implementation Pattern:
Each module includes:
- Pure Python implementation
- Numba JIT-compiled version (where beneficial)
- Comprehensive test suite (99.6% passing)
- Performance benchmarks vs NumPy/SciPy
- Documentation

### Performance Wins:
- **NumPy LAPACK:** 10-100x faster for matrix operations >10×10
- **Python built-ins:** List/dict operations faster than custom C
- **Numba dominates** small-medium numerical operations (2-64x speedup)
- **NumPy/SciPy best** for large-scale linear algebra
- **Contour tracing** sees most dramatic improvement (90-3200x with Numba)
