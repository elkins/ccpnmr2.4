# Contour Tracing Implementations

## Overview

This directory contains **simplified standalone implementations** of contour tracing for performance comparison purposes (Pure Python vs Numba vs Cython).

## Important Note: Not Wrappers for Existing C Code

**These are NEW implementations, not wrappers around the existing C code.**

The existing C implementation is located at:
```
ccpnmr2.4/c/ccpnmr/analysis/contour_file.c (~700 lines)
```

## Why Simplified Implementations?

The existing C `contour_file.c` is a complex, production-ready system with many dependencies:

- **block_file.h** - Block-based file I/O system
- **store_file.h** - Data storage management
- **contour_data.h** - Complex contour data structures
- **hash_table.h** - Hash-based caching system
- **drawing_funcs.h** - Rendering infrastructure
- **mem_cache.h** - Memory management with locking

### Decision Rationale

For a meaningful performance comparison:

1. **Focus on computational hot path** - The marching squares algorithm is where optimization matters most
2. **Fair benchmarking** - Comparing algorithm performance, not file I/O or caching overhead
3. **Standalone testing** - Can test without building entire C dependency tree
4. **Educational value** - Clear, readable implementations for understanding the algorithm

## What's Implemented

All three implementations provide the **core marching squares contour tracing algorithm**:

- **16 marching squares cases** - Complete lookup table
- **Linear interpolation** - Edge crossing calculation
- **Contour segment generation** - Line segments at specified levels
- **Multiple level tracing** - Trace several contour levels efficiently

## What's NOT Implemented

These simplified versions do NOT include:

- ❌ Block-based file I/O
- ❌ Hash table caching
- ❌ Store file management
- ❌ Drawing/rendering functions
- ❌ Memory cache with locking
- ❌ Complex data structure management

## Files

- **contour.py** - Pure Python implementation (baseline)
- **contour_numba.py** - Numba JIT-compiled version
- **contour_cython.pyx** - Cython static-typed version
- **setup_contour.py** - Cython compilation script
- **test_contour.py** - Unit tests for all three implementations
- **benchmark_contour.py** - Performance benchmarks

## Usage

### Compile Cython Module

```bash
cd ccpnmr2.4/python/ccpnmr/analysis/python_impl
python setup_contour.py build_ext --inplace
```

### Run Tests

```bash
python -m pytest test_contour.py -v
```

### Run Benchmarks

```bash
python benchmark_contour.py
```

## API

All three implementations provide the same API:

```python
# Create tracer
tracer = ContourTracer(width=100, height=100)

# Set grid data
tracer.set_data(grid_data)

# Trace single level
segments = tracer.trace_level(level=1.5)

# Trace multiple levels
results = tracer.trace_levels([1.0, 2.0, 3.0])
```

## Performance Expectations

Based on similar modules in this codebase:

- **Cython** - Likely fastest (C-level performance)
- **Numba** - Competitive on JIT-compiled loops
- **Pure Python** - Surprisingly good (CPython optimization)

Actual results may vary based on grid size and data patterns.

## Future Work

If production use of the existing C implementation is needed:

1. Create Python extension module wrapping contour_file.c
2. Implement all dependencies (block_file, store_file, etc.)
3. Add proper error handling and memory management
4. Integrate with existing CCPN framework

This would be a separate effort from the performance comparison work here.
