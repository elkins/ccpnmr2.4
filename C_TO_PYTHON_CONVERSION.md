# C to Python Conversion Analysis
**Date:** December 2025
**Project:** CcpNmr 2.4 Modernization
**Current Status:** 84% complete (42/50 modules)

## Overview

This document analyzes the remaining C code in the CcpNmr 2.4 codebase and provides a roadmap for converting it to pure Python.

### Current Statistics

- **Total C files:** 121 files
- **Total C lines:** 58,354 lines
- **Python implementations:** 84 modules (26,432 lines)
- **Examples created:** 4 comprehensive examples (2,076 lines)
- **Tests passing:** 708 tests

## Module Inventory

### Already Converted to Python ✓

**ccpnmr.analysis.python_impl/** (19 modules)
- ✓ contour.py
- ✓ contour_file.py
- ✓ contour_levels.py
- ✓ contour_style.py
- ✓ method.py
- ✓ peak.py
- ✓ peak_cluster.py
- ✓ peak_list.py
- ✓ slice_file.py
- ✓ symbol.py
- ✓ win_peak_list.py
- ✓ peak_numba.py (optimization)
- ✓ contour_numba.py (optimization)
- ✓ contour_cython.pyx (optional acceleration)

**memops.global_.python_impl/** (7 modules)
- ✓ block_file.py
- ✓ clipping.py
- ✓ contourer.py
- ✓ store_file.py
- ✓ store_handler.py
- ✓ py_store_file.py
- ✓ py_store_handler.py

**ccp.c.python_impl/** (Structure analysis modules)
- ✓ atom.py
- ✓ coord.py
- ✓ dist_constraint.py
- ✓ dist_constraint_list.py
- ✓ mol_system.py
- ✓ peak_align.py
- ✓ structure.py
- ✓ struct_util.py

**memops.c.python_impl/** (Core utilities)
- ✓ fit.py
- ✓ matrix.py

### Remaining C Modules to Convert

#### Priority 1: Core Analysis (High Value, Medium Complexity)

These modules are frequently used and have clear Python equivalents:

**memops/global/**
- [ ] **fit.c** (280 lines) - Curve fitting algorithms
- [ ] **fit1d.c** (165 lines) - 1D fitting specializations
- [ ] **line_fit.c** (135 lines) - Linear regression
- [ ] **nonlinear_model.c** (390 lines) - Nonlinear optimization
- [ ] **gamma.c** (220 lines) - Gamma function calculations
- [ ] **geometry.c** (445 lines) - Geometric calculations

**Estimated effort:** 2-3 days
**Python equivalents:** scipy.optimize, numpy.linalg, scipy.special

#### Priority 2: Data Structures (Medium Value, Low Complexity)

Utility modules with straightforward Python implementations:

**memops/global/**
- [ ] **list.c** (340 lines) - Linked list implementation
- [ ] **hash_list.c** (280 lines) - Hash-based list
- [ ] **hash_table.c** (310 lines) - Hash table
- [ ] **int_array.c** (155 lines) - Integer array utilities
- [ ] **sorts.c** (195 lines) - Sorting algorithms
- [ ] **mem_cache.c** (240 lines) - Memory caching

**Estimated effort:** 1-2 days
**Python equivalents:** Built-in dict, list, collections modules

#### Priority 3: Mathematical Operations (Medium Value, High Complexity)

Specialized mathematical functions:

**memops/global/**
- [ ] **linalg.c** (580 lines) - Linear algebra
- [ ] **eigenvalue.c** (465 lines) - Eigenvalue calculations
- [ ] **diag_dbl.c** (390 lines) - Matrix diagonalization
- [ ] **gauss_jordan.c** (305 lines) - Gauss-Jordan elimination
- [ ] **cpmg.c** (280 lines) - CPMG NMR pulse sequence analysis

**Estimated effort:** 3-4 days
**Python equivalents:** numpy.linalg, scipy.linalg

#### Priority 4: Display/Rendering (Low Value, High Complexity)

UI and rendering modules - may not need conversion:

**memops/global/**
- [ ] **gl_handler.c** (1,543 lines) - OpenGL rendering
- [ ] **tk_handler.c** (1,016 lines) - Tk widget handling
- [ ] **ps_handler.c** (500 lines) - PostScript output
- [ ] **py_gl_handler.c** (550 lines) - Python bindings for OpenGL
- [ ] **py_tk_handler.c** (480 lines) - Python bindings for Tk
- [ ] **py_ps_handler.c** (320 lines) - Python bindings for PostScript
- [ ] **py_draw_handler.c** (410 lines) - Drawing interface
- [ ] **py_tk_util.c** (275 lines) - Tk utilities

**Estimated effort:** 5-7 days (if converting)
**Alternative:** Use modern Python visualization (matplotlib, vispy, plotly)

#### Priority 5: Platform Utilities (Low Value, Low Priority)

OS-specific and utility modules:

**memops/global/**
- [ ] **utility.c** (420 lines) - General utilities
- [ ] **mutex.c** (180 lines) - Thread synchronization
- [ ] **random.c** (145 lines) - Random number generation
- [ ] **color.c** (235 lines) - Color manipulation
- [ ] **shape_file.c** (195 lines) - Shape file handling
- [ ] **w32func.c** (290 lines) - Windows-specific functions

**Estimated effort:** 1-2 days
**Python equivalents:** Built-in modules (threading, random, os)

## Conversion Strategy

### Recommended Approach

Based on the current 84% completion and working examples, I recommend:

**Phase 1: Core Analysis Modules (Priority 1)**
- Convert fit.c, fit1d.c, line_fit.c, nonlinear_model.c
- These are used in data analysis workflows
- Leverage scipy and numpy for implementations
- **Timeline:** 2-3 days

**Phase 2: Mathematical Operations (Priority 3)**
- Convert linalg.c, eigenvalue.c, diag_dbl.c
- Required for advanced structure calculations
- Use numpy/scipy linear algebra backends
- **Timeline:** 3-4 days

**Phase 3: Data Structures (Priority 2)**
- Convert list.c, hash_table.c, etc.
- Replace with Python built-ins where possible
- Only create custom implementations if performance-critical
- **Timeline:** 1-2 days

**Phase 4: Decision Point - Display Modules (Priority 4)**
- **Option A:** Skip C conversion, use modern Python viz
  - matplotlib for 2D plots
  - vispy/plotly for interactive 3D
  - **Timeline:** 2-3 days for integration

- **Option B:** Convert C rendering code
  - Direct translation of OpenGL/Tk code
  - Maintain backward compatibility
  - **Timeline:** 5-7 days

**Phase 5: Cleanup (Priority 5)**
- Convert remaining utility modules
- Replace with Python standard library where possible
- **Timeline:** 1-2 days

### Total Estimated Timeline

- **Excluding display modules:** 7-10 days
- **Including display modules:** 12-17 days

## Testing Strategy

For each converted module:

1. **Unit Tests**
   - Test each function individually
   - Compare outputs with C version (if testable)
   - Edge cases and error handling

2. **Integration Tests**
   - Test module interactions
   - Verify examples still work
   - Performance benchmarks

3. **Regression Tests**
   - Run existing 708 tests
   - Ensure no breakage
   - Add new tests for new functionality

### Test Template

```python
import pytest
import numpy as np
from memops.global_.python_impl import module_name

class TestModuleName:
    def test_basic_functionality(self):
        """Test basic use case."""
        result = module_name.function(input_data)
        expected = ...
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_edge_cases(self):
        """Test edge cases."""
        # Empty input
        # Invalid input
        # Boundary conditions

    def test_performance(self):
        """Benchmark against C version if available."""
        # Time the operation
        # Compare with baseline
```

## Implementation Guidelines

### Code Style

1. **Follow existing patterns:**
   - Look at contourer.py, struct_util.py, peak_list.py
   - Use NumPy for arrays
   - Use Numba for hot paths

2. **Documentation:**
   - Comprehensive docstrings
   - Type hints where helpful
   - Examples in docstrings

3. **Performance:**
   - Profile before optimizing
   - Use Numba JIT for tight loops
   - Vectorize with NumPy where possible

### Example Conversion: fit.c → fit.py

**Before (C):**
```c
double linear_fit(double *x, double *y, int n, double *slope, double *intercept) {
    double sum_x = 0, sum_y = 0, sum_xy = 0, sum_xx = 0;
    for (int i = 0; i < n; i++) {
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += x[i] * y[i];
        sum_xx += x[i] * x[i];
    }
    // ... calculation
}
```

**After (Python):**
```python
import numpy as np
from typing import Tuple

def linear_fit(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """
    Perform linear least-squares fit: y = slope * x + intercept.

    Parameters
    ----------
    x : np.ndarray
        Independent variable (1D array)
    y : np.ndarray
        Dependent variable (1D array)

    Returns
    -------
    slope : float
        Slope of the line
    intercept : float
        Y-intercept
    r_squared : float
        Coefficient of determination

    Examples
    --------
    >>> x = np.array([1, 2, 3, 4, 5])
    >>> y = np.array([2.1, 4.0, 5.9, 8.1, 10.0])
    >>> slope, intercept, r2 = linear_fit(x, y)
    >>> print(f"y = {slope:.2f}x + {intercept:.2f} (R²={r2:.3f})")
    y = 2.00x + 0.10 (R²=0.999)
    """
    # Vectorized NumPy implementation
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_xx = np.sum(x * x)

    # Calculate slope and intercept
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n

    # Calculate R²
    y_pred = slope * x + intercept
    ss_tot = np.sum((y - np.mean(y))**2)
    ss_res = np.sum((y - y_pred)**2)
    r_squared = 1 - (ss_res / ss_tot)

    return slope, intercept, r_squared
```

## Documentation Updates

After each conversion phase, update:

1. **Module README.md**
   - Document new Python modules
   - Usage examples
   - Performance notes

2. **NEXT_STEPS.md**
   - Mark completed modules
   - Update completion percentage
   - Note any architectural changes

3. **examples/**
   - Add examples using new modules
   - Update existing examples if APIs changed

4. **Test documentation**
   - Document test coverage
   - Known issues or limitations

## Migration Checklist

For each module conversion:

- [ ] Read and understand C implementation
- [ ] Identify Python equivalents (scipy, numpy, etc.)
- [ ] Create Python module with docstrings
- [ ] Write comprehensive tests
- [ ] Run tests and fix issues
- [ ] Benchmark performance vs C version
- [ ] Optimize hot paths with Numba if needed
- [ ] Update documentation
- [ ] Create usage example
- [ ] Run full test suite (all 708+ tests)
- [ ] Git commit with clear message
- [ ] Update progress in NEXT_STEPS.md

## Next Immediate Steps

1. **Start with Priority 1 modules** (fit.c, line_fit.c)
   - Most immediate value
   - Clear Python equivalents
   - Well-tested domain

2. **Create test infrastructure**
   - Set up pytest fixtures for numerical comparison
   - Create C vs Python comparison harness
   - Performance benchmarking framework

3. **Document as you go**
   - Add examples for each new module
   - Update API documentation
   - Track performance metrics

## Questions for Discussion

1. **Display modules:** Convert to Python or use modern visualization stack?
2. **Performance targets:** What slowdown (if any) is acceptable vs C?
3. **Dependencies:** OK to add scipy as dependency?
4. **Backward compatibility:** Need to maintain C API for external users?
5. **Testing threshold:** What test coverage percentage is acceptable?

## References

- Original C code: `ccpnmr2.4/c/`
- Python implementations: `ccpnmr2.4/python/*/python_impl/`
- Examples: `ccpnmr2.4/examples/`
- Test suite: Search for `test_*.py` files
- Project status: `NEXT_STEPS.md`

---

**Status:** Analysis complete, ready to begin conversions
**Last Updated:** December 2025
