# Using 3D HNCO Spectrum with Existing CcpNmr Code

## Overview

This directory contains two types of testing tools:

### 1. Standalone Benchmarks (Current)
- **[profile_3d_processing.py](profile_3d_processing.py)** - Pure Python/NumPy performance baselines
- **[test_3d_algorithms.py](test_3d_algorithms.py)** - Algorithm correctness validation (30 tests)

These are **NOT** testing existing CcpNmr code. They serve as:
- Performance targets for future C→Python conversions
- Reference implementations for algorithmic correctness
- Baseline metrics for optimization work

### 2. CcpNmr Integration (To Be Created)
Testing the **existing CcpNmr codebase** with real 3D spectrum data.

---

## Existing CcpNmr Varian Support

CcpNmr **already has** Varian format support:

### Key Modules

**1. Varian File Reader:**
```python
from ccp.format.varian.varianFile import parseProcparFile, readDataFileHeader
```
- Located: [`ccpnmr2.4/python/ccp/format/varian/varianFile.py`](../../python/ccp/format/varian/varianFile.py)
- Parses `procpar` parameter files
- Reads binary FID data headers
- Handles byte swapping and block structures

**2. Varian Parameter Wrapper:**
```python
from ccp.format.spectra.params.VarianParams import VarianParams
```
- Located: [`ccpnmr2.4/python/ccp/format/spectra/params/VarianParams.py`](../../python/ccp/format/spectra/params/VarianParams.py)
- High-level interface to Varian data
- Integrates with CcpNmr data model
- Handles 1D, 2D, 3D spectra

**3. Spectrum Data I/O:**
```python
from ccp.format.spectra.OpenSpectrum import openSpectrum
```
- Located: [`ccpnmr2.4/python/ccp/format/spectra/`](../../python/ccp/format/spectra/)
- Generic interface for opening spectra
- Supports Varian, Bruker, nmrPipe, Azara, etc.

### Supported Formats
- ✓ Varian/Agilent
- ✓ Bruker
- ✓ nmrPipe
- ✓ Azara
- ✓ Felix
- ✓ nmrDraw
- ✓ And many more...

---

## Quick Test: Use CcpNmr with HNCO Data

⚠️ **IMPORTANT: The examples below will NOT work yet!**

CcpNmr's Varian reader (`ccp/format/varian/varianFile.py`) uses **Python 2 syntax** and needs modernization:
- `except ValueError, e:` → `except ValueError as e:`
- Regex patterns need raw strings: `r'(\d+)'`

These examples are **templates** showing how to test CcpNmr once the Python 2→3 modernization is complete.

---

### Example 1: Read Procpar with Existing CcpNmr Code (TEMPLATE - needs Python 3 conversion)

```python
#!/usr/bin/env python3
"""Test existing CcpNmr Varian reader with BMRB 5106 HNCO data."""

import sys
import os

# Add CcpNmr to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from ccp.format.varian.varianFile import parseProcparFile

# Read procpar
data_dir = os.path.dirname(__file__)
procpar_path = os.path.join(data_dir, 'hnco_bmr5106_procpar')

params = parseProcparFile(procpar_path)

# Print key parameters
print("Varian Procpar Parameters:")
print(f"  ndim: {params['ccpnParams']['ndim']}")
print(f"  npts: {params['ccpnParams']['npts']}")
print(f"  sf (MHz): {params['ccpnParams']['sf']}")
print(f"  sw (Hz): {params['ccpnParams']['sw']}")
print(f"  refpt: {params['ccpnParams']['refpt']}")
print(f"  refppm: {params['ccpnParams']['refppm']}")
```

### Example 2: Open Spectrum with VarianParams

```python
#!/usr/bin/env python3
"""Open HNCO spectrum using CcpNmr VarianParams."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from ccp.format.spectra.params.VarianParams import VarianParams

data_dir = os.path.dirname(__file__)
procpar_path = os.path.join(data_dir, 'hnco_bmr5106_procpar')
fid_path = os.path.join(data_dir, 'hnco_bmr5106_origfid')

# Create params object
params = VarianParams(procpar_path, data_file=fid_path)

print(f"Spectrum dimensions: {params.ndim}D")
print(f"Data points: {params.npts}")
print(f"Spectral widths (Hz): {params.sw}")
print(f"Spectrometer frequencies (MHz): {params.sf}")
print(f"Reference points: {params.refpt}")
print(f"Reference chemical shifts (ppm): {params.refppm}")
print(f"Block size: {params.block}")
print(f"Header size: {params.head} bytes")
print(f"Byte swap needed: {params.swap}")
```

### Example 3: Profile CcpNmr's Existing Code

```python
#!/usr/bin/env python3
"""Profile performance of existing CcpNmr Varian reader."""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from ccp.format.varian.varianFile import parseProcparFile, readDataFileHeader

data_dir = os.path.dirname(__file__)
procpar_path = os.path.join(data_dir, 'hnco_bmr5106_procpar')
fid_path = os.path.join(data_dir, 'hnco_bmr5106_origfid')

# Profile procpar parsing
start = time.perf_counter()
procpar_params = parseProcparFile(procpar_path)
procpar_time = time.perf_counter() - start

# Profile FID header reading
start = time.perf_counter()
fid_header = readDataFileHeader(fid_path)
header_time = time.perf_counter() - start

print("CcpNmr Varian Reader Performance:")
print(f"  Procpar parsing: {procpar_time*1000:.2f} ms")
print(f"  FID header read: {header_time*1000:.2f} ms")
print(f"  Total: {(procpar_time + header_time)*1000:.2f} ms")

print("\nProcpar parameters found:")
print(f"  Number of parameters: {len(procpar_params) - 1}")  # -1 for procparFile
print(f"  Dimensions: {procpar_params['ccpnParams']['ndim']}")

print("\nFID header info:")
print(f"  Number of points: {fid_header['np']}")
print(f"  Number of traces: {fid_header['ntraces']}")
print(f"  Number of block headers: {fid_header['nbheaders']}")
print(f"  First block: {fid_header['firstBlock']}")
print(f"  Byte swapped: {fid_header['swapped']}")
```

---

## Comparison: Standalone vs CcpNmr

| Feature | Standalone Scripts | Existing CcpNmr Code |
|---------|-------------------|---------------------|
| **Purpose** | Performance baselines, reference implementations | Production spectrum processing |
| **Complexity** | Simple, minimal dependencies | Full-featured, integrated with CcpNmr data model |
| **Speed** | Pure Python/NumPy (baseline) | Optimized with C extensions where needed |
| **Format Support** | Varian only (custom reader) | Varian, Bruker, nmrPipe, many more |
| **Processing** | Basic FFT, apodization, peak picking | Full processing pipeline + GUI |
| **Tests** | 30 algorithm validation tests | 708 existing tests across codebase |
| **Use Case** | C→Python conversion targets | Actual NMR analysis workflows |

---

## Next Steps

### Option A: Test Existing CcpNmr Code (Recommended First)

1. **Create `test_ccpnmr_varian.py`**:
   - Use existing `ccp.format.varian` modules
   - Profile reading HNCO dataset
   - Compare performance with standalone reader
   - Validate data correctness

2. **Integrate with CcpNmr Processing Pipeline**:
   - Use existing FFT/processing modules if available
   - Profile end-to-end spectrum processing
   - Identify performance bottlenecks

3. **Compare Results**:
   - Standalone benchmarks vs CcpNmr implementation
   - Identify opportunities for optimization
   - Document performance differences

### Option B: Continue C→Python Conversion Work

See [CONVERSION_PROGRESS.md](../../CONVERSION_PROGRESS.md) for ongoing work:
- ✓ line_fit.c → line_fit.py (completed, 25 tests passing)
- ⏳ fit.c → fit.py (in progress)
- ⏳ geometry.c, cpmg.c, etc. (planned)

Standalone benchmarks serve as performance/correctness targets for this work.

---

## File Structure

```
ccpnmr2.4/data/test_3d_spectrum/
├── README.md                       # Dataset documentation
├── USAGE.md                        # Standalone benchmarks usage
├── CCPNMR_INTEGRATION.md          # This file (CcpNmr integration guide)
├── profile_3d_processing.py       # Standalone profiler (NOT CcpNmr code)
├── test_3d_algorithms.py          # Standalone tests (NOT CcpNmr code)
├── hnco_bmr5106_origfid           # Raw 3D FID (16 MB, Varian format)
├── hnco_bmr5106_procpar           # Acquisition parameters
└── hnco_bmr5106.peaks             # Reference peak list

ccpnmr2.4/python/ccp/format/varian/
├── varianFile.py                  # Existing CcpNmr Varian reader
├── acqParsIO.py                   # Parameter I/O
└── generalIO.py                   # Format conversion

ccpnmr2.4/python/ccp/format/spectra/
├── params/VarianParams.py         # High-level Varian interface
└── OpenSpectrum.py                # Generic spectrum opener
```

---

## Questions?

- **Standalone benchmarks**: See [USAGE.md](USAGE.md)
- **CcpNmr integration**: Create examples above, then profile and compare
- **C→Python conversion**: See [CONVERSION_PROGRESS.md](../../CONVERSION_PROGRESS.md)

---

**Last Updated:** December 2025
**Purpose:** Clarify relationship between standalone benchmarks and existing CcpNmr code
