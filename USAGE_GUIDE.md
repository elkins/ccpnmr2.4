# CcpNmr Python Implementation - Usage Guide

This guide provides practical examples for using the modernized Python implementations of CcpNmr modules.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Molecular Structure Operations](#molecular-structure-operations)
3. [Peak Detection and Analysis](#peak-detection-and-analysis)
4. [Contour Generation](#contour-generation)
5. [Spectral Data Processing](#spectral-data-processing)
6. [File I/O and Caching](#file-io-and-caching)
7. [Performance Optimization](#performance-optimization)

---

## Getting Started

### Basic Setup

```python
import sys
from pathlib import Path

# Add CcpNmr to path
ccpnmr_path = Path("/path/to/ccpnmr2.4/python")
sys.path.insert(0, str(ccpnmr_path))
```

### Running Tests

```bash
# Run all tests
cd tests
pytest -v

# Run specific module tests
pytest test_peak_list.py -v

# Run with coverage
pytest --cov=ccpnmr --cov-report=html
```

---

## Molecular Structure Operations

### Structural Alignment (Kabsch Algorithm)

```python
from ccp.c.python_impl.struct_util import align_ensemble
import numpy as np

# Coordinate arrays: (n_atoms, 3) for each structure
coords1 = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
coords2 = np.array([[0.1, 0, 0], [1.1, 0.1, 0], [0, 1.1, 0.1]], dtype=np.float32)
coords3 = np.array([[0, 0.1, 0], [1, 0, 0.1], [0.1, 1, 0]], dtype=np.float32)

ensemble = [coords1, coords2, coords3]

# Align ensemble with iterative RMSD weighting
aligned, weights, rmsd = align_ensemble(ensemble, threshold=0.8)

print(f"Final RMSD: {rmsd:.3f} Å")
print(f"Structure weights: {weights}")
```

### RMSD Calculation

```python
from ccp.c.python_impl.struct_util import calculate_rmsd

coords_a = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
coords_b = np.array([[0.1, 0, 0], [1.1, 0, 0], [0, 1.1, 0]], dtype=np.float32)

rmsd = calculate_rmsd(coords_a, coords_b)
print(f"RMSD: {rmsd:.3f} Å")
```

### Structure Management

```python
from ccp.c.python_impl.structure import Structure
from ccp.c.python_impl.atom import Atom
from ccp.c.python_impl.bond import Bond

# Create structure
structure = Structure()

# Add atoms
atom1 = Atom(coord=[0.0, 0.0, 0.0], radius=1.5, color=[1.0, 0.0, 0.0])
atom2 = Atom(coord=[1.0, 0.0, 0.0], radius=1.5, color=[0.0, 1.0, 0.0])

idx1 = structure.add_atom(atom1)
idx2 = structure.add_atom(atom2)

# Add bond
bond = Bond(atom1=atom1, atom2=atom2, width=0.1, color=[0.5, 0.5, 0.5])
structure.add_bond(bond)

# Find nearest atom (with perspective projection)
camera = [0.0, 0.0, 10.0]
x, y = 0.5, 0.0  # Screen coordinates
found, index, distance = structure.find_nearest_atom(x, y, 0.5, camera)
```

---

## Peak Detection and Analysis

### Automated Peak Picking

```python
from ccpnmr.analysis.python_impl.peak_list import PeakList
from ccpnmr.analysis.python_impl.peak import Peak
import numpy as np

# Create peak list
peak_list = PeakList(
    ndim=2,
    dim_names=["1H", "15N"],
    npoints=np.array([1024, 256])
)

# Automated peak picking from spectral data
# data is a 2D numpy array
data = np.random.randn(256, 1024).astype(np.float32)
data[100, 500] = 50.0  # Add a peak

# Mock block file for peak picking
class MockBlockFile:
    def __init__(self, data):
        self.data = data
        self.ndim = 2
        self.npoints = np.array(data.shape)
        self.points = self.npoints
    
    def get_point(self, point):
        return self.data[point[1], point[0]]

block_file = MockBlockFile(data)

# Pick peaks with criteria
peak_list.pick_peaks(
    block_file=block_file,
    threshold=10.0,           # Minimum intensity
    is_max=True,              # Find maxima
    drop_factor=0.5,          # 50% intensity drop required
    diagonal_exclusions=[],   # No diagonal exclusion
    box_exclusions=[],        # No box exclusions
    min_linewidth=None,       # No linewidth filter
    min_drop_distance=2       # Minimum separation
)

print(f"Found {peak_list.npeaks} peaks")

# Access peaks
for i in range(peak_list.npeaks):
    peak = peak_list.peaks[i]
    print(f"Peak {i}: position={peak.position}, intensity={peak.intensity:.2f}")
```

### Peak Clustering (Multiplet Detection)

```python
from ccpnmr.analysis.python_impl.peak_cluster import (
    cluster_peaks_multiplet, cluster_peaks_shift
)

# Cluster by multiplet structure
positions = np.array([
    [100.0, 50.0],
    [100.2, 50.0],  # Close in both dims (multiplet)
    [100.4, 50.0],
    [200.0, 100.0]
])

clusters = cluster_peaks_multiplet(
    positions=positions,
    tolerances=np.array([0.3, 0.1])  # PPM tolerances
)

print(f"Found {len(clusters)} multiplets")

# Cluster by chemical shift (one dimension)
clusters = cluster_peaks_shift(
    positions=positions,
    dim=0,
    tolerance=0.5
)
```

### Peak Fitting

```python
from ccpnmr.analysis.python_impl.method import (
    fit_peak_parabolic, fit_peak_gaussian
)

# Parabolic fitting (fast, for center determination)
data_slice = np.array([1.0, 5.0, 10.0, 5.0, 1.0])
center, height = fit_peak_parabolic(data_slice, center_index=2)
print(f"Peak center: {center:.2f}, height: {height:.2f}")

# Gaussian fitting (accurate, for linewidth)
result = fit_peak_gaussian(
    data_slice,
    center_index=2,
    max_iterations=100,
    tolerance=1e-5
)
print(f"Gaussian: center={result['center']:.2f}, sigma={result['sigma']:.2f}")
```

---

## Contour Generation

### Marching Squares Contour Tracing

```python
from memops.global_.python_impl.contourer import (
    ContoururInfo, calculate_contours, process_chains
)
import numpy as np

# Create 2D spectral data
size = 100
x = np.linspace(-5, 5, size)
y = np.linspace(-5, 5, size)
xx, yy = np.meshgrid(x, y)

# Gaussian peak
data = np.exp(-(xx**2 + yy**2) / 2.0).astype(np.float32)

# Setup contour generation
row_index = [0]

def get_row(user_data):
    """Callback to get data rows."""
    row = data[row_index[0]]
    row_index[0] += 1
    return row

# Configure contourer
levels = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
info = ContoururInfo(
    user_data=None,
    nlevels=len(levels),
    levels=levels,
    npoints=np.array([size, size]),
    offset=np.array([0.0, 0.0]),
    scale=np.array([1.0, 1.0]),
    get_row_func=get_row
)

# Generate contours
contours = calculate_contours(info)

print(f"Generated contours for {contours.n} levels")
for level_idx in range(contours.n):
    vertices = contours.vertices[level_idx]
    print(f"  Level {levels[level_idx]:.2f}: {vertices.nvertices} vertices")
    
    # Process chains (connected contour paths)
    chains = []
    def collect_chain(user_data, nvertices, first_vertex):
        chain_coords = []
        v = first_vertex
        for _ in range(nvertices):
            chain_coords.append((v.x[0], v.x[1]))
            if v.v2:
                v = v.v2
            else:
                break
        chains.append(chain_coords)
    
    process_chains(vertices, None, collect_chain)
    print(f"    {len(chains)} contour paths")
```

### Contour Storage and Retrieval

```python
from memops.global_.python_impl.store_handler import StoreHandler
from memops.global_.python_impl.store_file import StoreFile

# Save contours to binary file
handler = StoreHandler("contours.dat")
handler.start_contours(
    level=0.5,
    size=10,
    x_min=0.0, y_min=0.0,
    x_max=100.0, y_max=100.0,
    cull_min=0.0, cull_max=10.0
)

# Add contour segments
for segment in contour_segments:
    handler.add_contour(segment)  # segment is 10 floats

handler.finish_contours()
handler.close()

# Read contours back
store = StoreFile("contours.dat")
ncontours = store.get_ncontours()

for i in range(ncontours):
    level = store.get_level(i)
    x_min, y_min, x_max, y_max = store.get_tile(i)
    segment = store.get_contour(i)
    print(f"Contour {i}: level={level:.2f}, tile=({x_min},{y_min})-({x_max},{y_max})")

store.close()
```

---

## Spectral Data Processing

### Block File I/O

```python
from memops.global_.python_impl.block_file import BlockFile
import numpy as np

# Create block file for 2D spectrum
block_file = BlockFile(
    file="spectrum.dat",
    ndim=2,
    points=np.array([1024, 512]),
    block_size=np.array([64, 64]),
    bytes_per_point=4,
    big_endian=True,
    writeable=True
)

# Open file
block_file.open()

# Write data point
point = np.array([100, 200])
value = 42.5
block_file.set_point(point, value)

# Read data point
retrieved = block_file.get_point(point)
print(f"Value at {point}: {retrieved}")

# Read data region (box)
first = np.array([90, 190])
last = np.array([110, 210])
box_data = block_file.get_box(first, last)
print(f"Box shape: {box_data.shape}")

# Save changes
block_file.save()
block_file.close()
```

### 1D Slice Extraction

```python
from ccpnmr.analysis.python_impl.slice_file import SliceFile

# Create slice file
slice_file = SliceFile(
    orient=1,  # Horizontal
    dim=0,     # Slice along dimension 0
    block_file=block_file
)

# Mock drawing functions
class DrawingFuncs:
    def __init__(self):
        self.lines = []
    
    def draw_line(self, data, x0, y0, x1, y1):
        self.lines.append((x0, y0, x1, y1))

drawing = DrawingFuncs()

# Extract horizontal slice at position y=256
position = np.array([0.0, 256.0])
slice_file.draw_slice(
    first=0,
    last=1024,
    position=position,
    drawing_funcs=drawing,
    data=None
)

print(f"Drew {len(drawing.lines)} line segments")
```

### Linear Regression and Fitting

```python
from memops.global_.python_impl.line_fit import line_fit
from memops.global_.python_impl.fit import exponential_fit

# Simple line fitting
x_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
y_data = np.array([2.1, 4.0, 5.9, 8.1, 10.0])
weights = np.ones_like(x_data)

result = line_fit(x_data, y_data, weights)
print(f"y = {result['a']:.2f} + {result['b']:.2f}x")
print(f"Error: a±{result['error_a']:.2f}, b±{result['error_b']:.2f}")

# Exponential decay fitting
t = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
intensity = np.array([100.0, 60.6, 36.8, 22.3, 13.5])

params = exponential_fit(t, intensity)
print(f"I(t) = {params['a']:.2f} * exp(-t / {params['tau']:.2f}) + {params['c']:.2f}")
```

---

## File I/O and Caching

### Memory Cache

```python
from memops.global_.python_impl.mem_cache import Mem_cache

# Create cache (stores Python objects)
cache = Mem_cache()

# Store data
key1 = "spectrum_data"
data = np.random.randn(1000, 1000)
cache.add(key1, data)

# Retrieve data
retrieved = cache.get(key1)
assert retrieved is data

# Check existence
if cache.contains(key1):
    print(f"Cache hit for {key1}")

# Remove from cache
cache.remove(key1)

# Clear all
cache.clear()
```

### Hash Tables

```python
from memops.global_.python_impl.hash_table import Hash_table

# Create hash table
table = Hash_table(size=1000)

# Insert key-value pairs
table.insert("peak_001", "data_for_peak_1")
table.insert("peak_002", "data_for_peak_2")

# Lookup
value = table.lookup("peak_001")
print(f"Found: {value}")

# Check existence
exists = table.exists("peak_003")

# Remove
table.remove("peak_001")

# Iterate
for key in table.keys():
    value = table.lookup(key)
    print(f"{key}: {value}")
```

---

## Performance Optimization

### Using Numba JIT Compilation

Many modules have `_numba.py` versions with JIT-compiled functions:

```python
# Regular version
from ccpnmr.analysis.python_impl.contour import trace_contours

# Numba-accelerated version (90-3200x faster)
from ccpnmr.analysis.python_impl.contour_numba import trace_contours_numba

# Use Numba version for large datasets
data = np.random.randn(1000, 1000).astype(np.float32)
level = 0.5

# This will be dramatically faster
contours = trace_contours_numba(data, level)
```

### Benchmarking

```python
import time

def benchmark(func, *args, iterations=100):
    """Simple benchmark helper."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = np.mean(times)
    std_time = np.std(times)
    return mean_time, std_time, result

# Compare implementations
data = np.random.randn(500, 500).astype(np.float32)

mean_py, std_py, _ = benchmark(trace_contours, data, 0.5)
mean_nb, std_nb, _ = benchmark(trace_contours_numba, data, 0.5)

print(f"Python: {mean_py*1000:.2f}±{std_py*1000:.2f} ms")
print(f"Numba:  {mean_nb*1000:.2f}±{std_nb*1000:.2f} ms")
print(f"Speedup: {mean_py/mean_nb:.1f}x")
```

### Memory Optimization

```python
# Use appropriate dtypes
data_float32 = np.array(data, dtype=np.float32)  # Smaller than float64

# Pre-allocate arrays when possible
result = np.empty((1000, 1000), dtype=np.float32)

# Use generators for large datasets
def process_peaks_generator(peak_list):
    for i in range(peak_list.npeaks):
        yield peak_list.peaks[i]

# Instead of loading all at once
for peak in process_peaks_generator(peak_list):
    # Process one at a time
    pass
```

### Caching Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    """Cache results of expensive operations."""
    # Compute something expensive
    return result

# First call computes
result1 = expensive_calculation(42)

# Second call retrieves from cache
result2 = expensive_calculation(42)  # Instant
```

---

## Tips and Best Practices

### 1. Choose the Right Implementation

- **Small datasets (<100×100):** Use Numba versions for speed
- **Large datasets (>1000×1000):** Use NumPy/SciPy for memory efficiency
- **Interactive use:** Python versions for debugging
- **Production:** Numba or C-extension compatible versions

### 2. Error Handling

```python
try:
    result = peak_list.pick_peaks(block_file, threshold=10.0)
except ValueError as e:
    print(f"Invalid parameters: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
```

### 3. Testing Your Code

```python
import pytest

def test_my_analysis():
    """Test your analysis workflow."""
    peak_list = PeakList(ndim=2, ...)
    
    # Add test peaks
    peak_list.add_peak(Peak(...))
    
    # Verify
    assert peak_list.npeaks == 1
    assert peak_list.peaks[0].intensity > 0
```

### 4. Profiling

```python
import cProfile
import pstats

# Profile your code
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = expensive_function()

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

---

## Additional Resources

- **API Documentation:** See docstrings in each module
- **Test Examples:** Check `tests/test_*.py` for usage patterns
- **Benchmarks:** Run `python benchmark_*.py` in module directories
- **Original C Code:** Available in `ccpnmr2.4/c/` for reference

## Getting Help

1. Check module docstrings: `help(module.function)`
2. Review test files for examples
3. Compare with original C implementation
4. Run with verbose error messages

---

## Summary

This guide covers the most common use cases for the CcpNmr Python implementations. All modules are designed to be:

- **Drop-in replacements** for C extensions
- **Well-tested** with comprehensive test suites
- **Performance-optimized** with NumPy/Numba
- **Easy to use** with Pythonic APIs

For specific module details, refer to the module docstrings and test files.
