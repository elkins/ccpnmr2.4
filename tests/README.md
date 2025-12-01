# Testing Framework for C-to-Python Migration

This directory demonstrates the pattern for creating implementation-agnostic tests that work with both C extensions and pure Python replacements. Currently includes complete examples for **mem_cache**, **peak**, **atom**, and **bond** modules.

## What's Included

## What's Included

### Example 1: Memory Cache (`mem_cache.py`)

#### Pure Python Implementation
- Complete thread-safe LRU cache implementation
- Matches C API exactly: `new_mem_cache()`, `add_mem_cache()`, etc.
- Drop-in replacement for the C extension
- ~300 lines with full documentation

**Key features:**
- Thread-safe using `threading.RLock`
- LRU eviction policy using `OrderedDict`
- Lock count mechanism prevents premature eviction
- Size-based memory management
- Custom cleanup/delete functions

#### Unit Tests (`test_mem_cache.py`)
- **16 tests** covering all major functionality
- Test categories:
  - Basic operations: add, remove, lock/unlock
  - Eviction behavior: size limits, locked objects
  - Delete functions: cleanup callbacks
  - Thread safety: concurrent operations
  - API compatibility: verify interface matches

**Test results:**
```
Ran 16 tests in 0.013s
OK
```

### Example 2: Peak (`peak.py`)

#### Pure Python Implementation
- NMR spectral peak representation
- Matches C API: `new_peak()`, `set_position_peak()`, etc.
- Drop-in replacement for data management functions
- ~350 lines with full documentation

**Key features:**
- Multi-dimensional peak positions (1D, 2D, 3D, nD)
- Peak metadata: intensity, volume, line widths
- Selection state and text labels
- Aliasing support for spectral folding
- Region checking and scaled region calculations

**Note:** Some advanced functions (`fit_volume_peak`, `draw_peak`) are stubs requiring additional infrastructure (block_file, drawing_funcs). Basic data management is fully implemented.

#### Unit Tests (`test_peak.py`)
- **39 tests** covering all implemented functionality
- Test categories:
  - Peak creation: 1D, 2D, 3D peaks
  - Selection state: get/set operations
  - Text labels: Unicode support, empty strings
  - Position management: multi-dimensional coordinates
  - Aliasing: spectral folding calculations
  - Intensity/volume: positive, negative, zero values
  - Line widths: per-dimension settings
  - Text offsets: label positioning
  - Region checking: with/without aliasing
  - Scaled regions: dimension-specific scaling
  - API compatibility: all C functions present

**Test results:**
```
Ran 39 tests in 0.001s
OK
```

### Example 3: Atom (`atom.py`)

#### Pure Python Implementation
- 3D atom representation for molecular visualization
- Matches C API: `new_atom()`, `translate_atom()`, `rotate_atom()`, etc.
- Drop-in replacement for molecular structure operations
- ~400 lines with full documentation

**Key features:**
- 3D coordinates and transformations (translate, rotate, zoom)
- Visual properties: size, color, symbol, annotation
- Bond connectivity management
- Drawing state (visible/hidden)
- Annotation color overrides
- Distance checking (2D tolerance)
- Depth-based color blending for 3D rendering

**Note:** The `draw_atom()` function is a stub requiring drawing_funcs infrastructure. All other operations (geometry, properties, bonds) are fully implemented.

#### Unit Tests (`test_atom.py`)
- **45 tests** covering all implemented functionality
- Test categories:
  - Basic operations: creation, properties, initial state
  - Property setters: size, symbol, annotation, color
  - Visibility: show/hide, toggle
  - Annotation colors: set/clear custom colors
  - Bond management: add, remove, allocation growth
  - Transformations: translate, rotate, zoom, set_coords
  - Distance checks: within_xy_tol with various cases
  - Helper functions: depth_param, inverted_grey_color
  - Constants: ATOM_NDIMS, ATOM_NCOLORS, depth values
  - API compatibility: all C functions present

**Test results:**
```
Ran 45 tests in 0.001s
OK
```

### Example 4: Bond (`bond.py`)

#### Pure Python Implementation
- Molecular bond connecting two atoms
- Matches C API: `new_bond()`, `set_color_bond()`, `get_other_atom_bond()`, etc.
- Drop-in replacement for bond visualization and connectivity
- ~260 lines with full documentation

**Key features:**
- Connects two atoms (atom1, atom2)
- Custom color or gradient from atom colors
- Line width and line style (normal/dashed)
- Text annotation labels
- Get opposite atom in bond
- Depth parameter calculation for 3D rendering
- Distance checking (point to line segment with perspective)

**Note:** The `draw_bond()` function is stubbed pending drawing_funcs infrastructure. All other operations (properties, connectivity, geometry) are fully implemented.

#### Unit Tests (`test_bond.py`)
- **33 tests** covering all implemented functionality
- Test categories:
  - Basic operations: creation with/without color, initial properties
  - Property setters: color, line width, line style, annotation
  - Atom queries: get_other_atom from both atoms
  - Depth parameter: calculation at various depths
  - Distance checks: within_xy_tol, behind camera, z_out
  - Integration: bonds connect atoms, use positions, multiple bonds
  - Constants: BOND_NCOLORS, DEFAULT_BOND_WIDTH, line styles, depth values
  - API compatibility: all C functions present

**Test results:**
```
Ran 33 tests in 0.001s
OK
```

### Comparison Test Runner (`run_comparison_tests.py`)
- Runs same tests against both implementations
- Reports equivalence (or differences)
- Useful for validation during porting

## Running Tests

### Quick test - mem_cache:
```bash
python3 tests/test_mem_cache.py
```

### Quick test - peak:
```bash
python3 tests/test_peak.py
```

### Quick test - atom:
```bash
python3 tests/test_atom.py
```

### Quick test - bond:
```bash
python3 tests/test_bond.py
```

### Run all tests:
```bash
python3 -m unittest discover tests
```

### Compare implementations:
```bash
python3 tests/run_comparison_tests.py
```

### Three-way comparison (Python vs Numba vs C):
```bash
python3 tests/run_three_way_comparison.py --benchmark
```

### Run specific test class:
```bash
python3 -m unittest tests.test_mem_cache.TestMemCacheEviction
python3 -m unittest tests.test_peak.TestPeakRegion
python3 -m unittest tests.test_atom.TestAtomTransformations
python3 -m unittest tests.test_bond.TestBondProperties
```

## Example Test Output

### mem_cache tests:
```
test_add_single_object (__main__.TestMemCacheBasics)
Test adding a single object. ... ok
test_eviction_when_full (__main__.TestMemCacheEviction)
Test that unlocked items are evicted when cache is full. ... ok
test_concurrent_additions (__main__.TestMemCacheThreadSafety)
Test adding objects from multiple threads. ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.013s

OK
```

### peak tests:
```
test_peak_creation_2d (__main__.TestPeakBasics)
Test creating a 2D peak. ... ok
test_peak_in_region (__main__.TestPeakRegion)
Test peak is detected when in region. ... ok
test_peak_with_aliasing (__main__.TestPeakRegion)
Test peak detection with aliasing. ... ok

----------------------------------------------------------------------
Ran 39 tests in 0.001s

OK
```

### atom tests:
```
test_atom_creation (__main__.TestAtomBasics)
Test creating a basic atom. ... ok
test_translate_atom (__main__.TestAtomTransformations)
Test translating atom position. ... ok
test_rotate_atom_90_degrees_z (__main__.TestAtomTransformations)
Test 90-degree rotation around z-axis. ... ok
test_add_multiple_bonds (__main__.TestAtomBonds)
Test adding multiple bonds. ... ok

----------------------------------------------------------------------
Ran 45 tests in 0.001s

OK
```

### bond tests:
```
test_bond_creation_with_color (__main__.TestBondBasics)
Test creating a bond with explicit color. ... ok
test_get_other_atom_from_atom1 (__main__.TestBondAtomQueries)
Test getting other atom when given atom1. ... ok
test_set_line_width (__main__.TestBondProperties)
Test setting line width. ... ok
test_depth_param_at_depth (__main__.TestBondDepthParam)
Test depth parameter at reference depth. ... ok

----------------------------------------------------------------------
Ran 33 tests in 0.001s

OK
```

## Pattern for Other Modules

This same approach works for any C extension module:

1. **Analyze the C code** to understand the API
   - Read `.h` header file for public interface
   - Check `.c` implementation for behavior details
   
2. **Create pure Python implementation**
   - Match function signatures exactly
   - Preserve behavior (thread-safety, error handling, etc.)
   - Add docstrings and type hints
   
3. **Optionally create numba-accelerated version**
   - Use `@jit` decorators for numerical operations
   - Best for array operations and tight loops
   - See `ccpnmr2.4/python/README_NUMBA.md` for details
   
4. **Write implementation-agnostic tests**
   - Import through the wrapper (`py_*.py` files)
   - Test public API behavior, not implementation
   - Cover edge cases, threading, memory management
   
4. **Validate equivalence**
   - Run tests against both implementations
   - Compare performance (optional)
   - Document any known differences

## Benefits of This Approach

✅ **Safety**: Tests validate correctness before/after replacement  
✅ **Incremental**: Can port one module at a time  
✅ **Reversible**: Easy to switch back if issues found  
✅ **Documentation**: Tests serve as executable specification  
✅ **Confidence**: Same tests ensure equivalent behavior  

## Next Steps for Other Modules

High-priority modules from `scripts/priority_backlog.csv`:

1. ~~**mem_cache.py**~~ - ✅ Complete with 16 tests
2. ~~**peak.py**~~ - ✅ Complete with 39 tests  
3. ~~**atom.py**~~ - ✅ Complete with 45 tests
4. ~~**bond.py**~~ - ✅ Complete with 33 tests
5. **contour_file.py** - Contour data handling (next priority)
6. **block_file.py** - Block file I/O

For each module:
1. Copy this pattern (implementation + tests)
2. Run tests to validate
3. Commit when tests pass
4. Update `scripts/failure_report_with_reasons.csv`

## Testing Strategy

### Unit Tests (this file)
- Test individual module behavior
- Fast, run frequently
- Implementation-agnostic

### Integration Tests (future)
- Test module interactions
- Use real data files
- Catch interface issues

### Performance Tests (optional)
- Compare C vs Python speed
- Identify bottlenecks
- Guide optimization priorities

## Files Created

```
# Pure Python implementations (in proper package locations):
ccpnmr2.4/python/memops/c/python_impl/mem_cache.py        # ✅ Complete
ccpnmr2.4/python/memops/c/python_impl/mem_cache_numba.py  # ✅ Numba variant
ccpnmr2.4/python/ccp/c/python_impl/atom.py                # ✅ Complete
ccpnmr2.4/python/ccp/c/python_impl/atom_numba.py          # ✅ Numba variant
ccpnmr2.4/python/ccp/c/python_impl/bond.py                # ✅ Complete
ccpnmr2.4/python/ccp/c/python_impl/bond_numba.py          # ✅ Numba variant
ccpnmr2.4/python/ccpnmr/analysis/python_impl/peak.py     # ✅ Complete
ccpnmr2.4/python/ccpnmr/analysis/python_impl/peak_numba.py # ✅ Numba variant

# Unit tests:
tests/test_mem_cache.py            # 16 tests for mem_cache
tests/test_peak.py                 # 39 tests for peak
tests/test_atom.py                 # 45 tests for atom
tests/test_bond.py                 # 33 tests for bond
tests/run_comparison_tests.py      # Two-way comparison runner
tests/run_three_way_comparison.py  # Three-way comparison with benchmarks
tests/README.md                    # This file

# Documentation:
ccpnmr2.4/python/README_NUMBA.md   # Numba implementation guide

# Wrappers (auto-generated, point to python_impl):
ccpnmr2.4/c/memops/global/py_mem_cache.py       # Wrapper for mem_cache
ccpnmr2.4/c/ccp/structure/py_atom.py            # Wrapper for atom
ccpnmr2.4/c/ccp/structure/py_bond.py            # Wrapper for bond
ccpnmr2.4/c/ccpnmr/analysis/py_peak.py          # Wrapper for peak
```

## Directory Structure

Pure Python implementations are organized to mirror the C extension structure:

```
ccpnmr2.4/
├── c/                          # C source code and wrappers
│   ├── memops/global/
│   │   └── py_mem_cache.py     # Wrapper: loads Python or C implementation
│   ├── ccp/structure/
│   │   ├── py_atom.py          # Wrapper: loads Python or C implementation
│   │   └── py_bond.py          # Wrapper: loads Python or C implementation
│   └── ccpnmr/analysis/
│       └── py_peak.py          # Wrapper: loads Python or C implementation
│
└── python/                     # Python implementations and compiled extensions
    ├── memops/c/
    │   ├── MemCache.so         # C extension (compiled)
    │   └── python_impl/
    │       └── mem_cache.py    # Pure Python implementation ✅
    ├── ccp/c/
    │   ├── StructAtom.so       # C extension (compiled)
    │   └── python_impl/
    │       ├── atom.py         # Pure Python implementation ✅
    │       └── bond.py         # Pure Python implementation ✅
    └── ccpnmr/analysis/
        └── python_impl/
            └── peak.py         # Pure Python implementation ✅
```

**Benefits of this structure:**
- ✅ Python implementations live in appropriate package namespaces
- ✅ Wrappers use relative paths (no hardcoded absolute paths)
- ✅ Clear separation: C extensions (`.so`) vs pure Python (`python_impl/`)
- ✅ Easy to find related code (wrapper, C extension, Python version all nearby)
- ✅ Matches Python package import structure

## Implementation Notes

### mem_cache - Thread Safety
Both C and Python implementations use mutexes/locks to ensure thread-safe operations. The Python version uses `threading.RLock` (reentrant lock) to match C behavior.

### mem_cache - Eviction Policy
When cache exceeds `max_size`, unlocked entries are evicted from oldest to newest until size drops to 70% of maximum. Locked entries are never evicted.

### mem_cache - Lock Counts
Objects track lock counts (can be locked multiple times). Only when count reaches 0 can object be evicted or removed.

### mem_cache - Delete Functions
Optional cleanup callbacks execute when objects are removed, evicted, or cache is cleared.

### peak - Multi-dimensional Support
Peaks support arbitrary dimensionality (1D, 2D, 3D, nD). Position, text_offset, num_aliasing, and line_width arrays automatically size to match ndim.

### peak - Aliasing
Spectral aliasing is handled by `num_aliasing` array and `is_in_region_peak` function. When aliasing is allowed, peak positions are adjusted by `position + num_aliasing * npoints` per dimension.

### peak - Deferred Implementation
Some functions (`fit_volume_peak`, `fit_center_peak`, `fit_linewidth_peak`, `draw_peak`) require additional infrastructure (block_file for data access, drawing_funcs for visualization). These are marked with `NotImplementedError` stubs and can be implemented when their dependencies are ported.

### atom - Geometric Transformations
Atom positions are manipulated using standard 3D transformations. `rotate_atom()` applies matrix multiplication: `new_pos = origin + matrix * (old_pos - origin)`. `zoom_atom()` scales coordinates from the origin. `translate_atom()` adds a delta vector.

### atom - Bond Management
Bonds are stored as references in a dynamically-growing list. The C code uses realloc; Python automatically grows the list. When removing bonds, the implementation searches from back to front (assumes recent bonds more likely removed) and fills gaps with the last element since order doesn't matter.

### atom - Drawing and Depth
`draw_atom()` is stubbed pending drawing_funcs infrastructure. The C code implements sophisticated 3D rendering with perspective transformation, depth cueing (color blending based on z-position), and multi-circle sphere effects. Helper functions (`get_depth_param_atom`, `inverted_grey_color`) are fully implemented for when drawing support is added.

### bond - Color Modes
Bonds support two color modes: (1) explicit color via `set_color_bond()`, or (2) gradient between atom colors. When `have_color` is False, `draw_bond()` blends colors from atom1 to atom2 along the bond length.

### bond - Line Styles
Two line styles supported: NORMAL_LINE_STYLE (0) and DASHED_LINE_STYLE (1). Line width -1.0 indicates use default (DEFAULT_BOND_WIDTH = 3.0).

### bond - Geometric Functions
`within_xy_tol_bond()` implements full 3D-to-2D projection with perspective transform. Calculates closest point on line segment using lambda parameter, handles camera culling (z > 0 rejected), and returns depth value for z-ordering.

### bond - Drawing
`draw_bond()` is stubbed pending drawing_funcs infrastructure. The C code implements bi-color gradient rendering, depth cueing, annotation placement at bond midpoint, and line style (solid/dashed) via drawing primitives.

## Debugging Tips

### Check cache state (mem_cache):
```python
cache = py_mem_cache.new_mem_cache(1000, None, None)
stats = cache.get_stats()
print(stats)  # {'max_size': 1000, 'current_size': 0, ...}
```

### Enable debug output (mem_cache):
```python
py_mem_cache.check_mem_cache(cache, "debug check")
# Prints all cached objects with sizes and lock counts
```

### Inspect peak data:
```python
peak = py_peak.new_peak(2)
py_peak.set_position_peak(peak, [100.0, 200.0])
py_peak.set_text_peak(peak, "H1-N15", None)
print(peak)
# Peak(ndim=2, pos=[100.0, 200.0], intensity=0.0, ...)
```

### Inspect atom data:
```python
atom = py_atom.new_atom(1.5, 'C', 'CA', [1.0, 2.0, 3.0], [0.5, 0.5, 0.5])
py_atom.translate_atom(atom, [1.0, 1.0, 1.0])
print(atom)
# Atom(symbol='C', size=1.50, pos=[2.00, 3.00, 4.00], nbonds=0, drawn=True)
print(f'Within tolerance: {py_atom.within_xy_tol_atom(atom, 2.5, 3.5, 1.0)}')
```

### Inspect bond data:
```python
atom1 = py_atom.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
atom2 = py_atom.new_atom(1.0, 'N', 'N', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
bond = py_bond.new_bond(atom1, atom2, [1.0, 1.0, 0.0])
py_bond.set_line_width_bond(bond, 5.0)
py_bond.set_annotation_bond(bond, 'C-N bond')
print(bond)
# Bond(atom1=Atom(C), atom2=Atom(N), color=[1.0,1.0,0.0], width=5.0)
print(f'Other atom: {py_bond.get_other_atom_bond(bond, atom1).symbol}')
```

### Verify implementation:
```python
import inspect
print(inspect.getfile(py_mem_cache.MemCache))
print(inspect.getfile(py_peak.Peak))
print(inspect.getfile(py_atom.Atom))
# Shows which implementation is loaded
```

## Common Issues

**Import errors**: Make sure `mem_cache.py` exists at repo root and wrapper points to it.

**Test failures**: Check that implementation matches C API exactly (return values, error handling).

**Thread issues**: Ensure all operations use proper locking (use `with self._mutex:` pattern).

## Contributing

When adding tests for new modules:
- Follow this same structure
- Aim for >80% code coverage
- Test error conditions and edge cases
- Document any C-vs-Python differences

## Summary of Completed Examples

| Module | Lines | Tests | Status | Notes |
|--------|-------|-------|--------|-------|
| **mem_cache** | ~300 | 16 | ✅ Complete | Thread-safe LRU cache with eviction |
| **peak** | ~350 | 39 | ✅ Complete | NMR peak data structure, some stubs for fitting/drawing |
| **atom** | ~400 | 45 | ✅ Complete | 3D atom with geometry, bonds, visualization properties |
| **bond** | ~260 | 33 | ✅ Complete | Molecular bond connecting two atoms |

**Total:** 133 passing tests across 4 modules

All four implementations demonstrate the full pattern:
- Pure Python matching C API exactly
- Comprehensive implementation-agnostic tests
- Full documentation and debugging support
- Ready for production use (where dependencies met)
