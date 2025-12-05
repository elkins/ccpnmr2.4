#!/usr/bin/env python3
"""
Test Existing CcpNmr Varian Reader with BMRB 5106 HNCO Dataset
===============================================================

IMPORTANT: This script tests EXISTING CcpNmr code, not standalone benchmarks.

**CURRENT STATUS: DOES NOT WORK - NEEDS PYTHON 2→3 MODERNIZATION**

The existing CcpNmr Varian reader (ccp/format/varian/varianFile.py) uses Python 2
syntax and has not yet been modernized:
  - `except ValueError, e:` (Python 2) → `except ValueError as e:` (Python 3)
  - Raw string regex escapes need fixing
  - Other Python 2 idioms

This script is a **template** showing how to test CcpNmr's Varian reader once
the Python 2→3 modernization is complete.

PURPOSE (after modernization):
-------------------------------
1. Validate that CcpNmr's existing Varian format reader works with 3D HNCO data
2. Profile performance of existing CcpNmr modules
3. Compare with standalone benchmark (profile_3d_processing.py)

This demonstrates CcpNmr's current capabilities with real 3D NMR data.

TO FIX:
-------
1. Modernize ccpnmr2.4/python/ccp/format/varian/varianFile.py (Python 2→3)
2. Run this script to validate the modernization worked
3. Compare performance with standalone benchmark

Author: CcpNmr Python Modernization Project
Date: December 2025
"""

import sys
import os
import time

# Add CcpNmr to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

from ccp.format.varian.varianFile import parseProcparFile, readDataFileHeader
from ccp.format.spectra.params.VarianParams import VarianParams


def test_procpar_parsing():
    """Test procpar file parsing with existing CcpNmr code."""
    print("=" * 70)
    print("TEST 1: Procpar Parsing (Existing CcpNmr Code)")
    print("=" * 70)

    data_dir = os.path.dirname(__file__)
    procpar_path = os.path.join(data_dir, 'hnco_bmr5106_procpar')

    if not os.path.exists(procpar_path):
        print(f"ERROR: Procpar file not found: {procpar_path}")
        return None

    # Profile parsing
    start = time.perf_counter()
    try:
        params = parseProcparFile(procpar_path)
    except Exception as e:
        print(f"ERROR: Failed to parse procpar: {e}")
        return None
    parse_time = time.perf_counter() - start

    print(f"\n  ⏱  Procpar parsing time: {parse_time*1000:.2f} ms")
    print(f"  ✓  Parameters parsed: {len(params) - 1}")  # -1 for 'procparFile' key

    # Print key parameters
    if 'ccpnParams' in params:
        ccpn = params['ccpnParams']
        print(f"\n  Spectrum Information:")
        print(f"    Dimensions: {ccpn.get('ndim', 'N/A')}")
        print(f"    Data points: {ccpn.get('npts', 'N/A')}")
        print(f"    Spectral widths (Hz): {ccpn.get('sw', 'N/A')}")
        print(f"    Spectrometer frequencies (MHz): {ccpn.get('sf', 'N/A')}")
        print(f"    Reference points: {ccpn.get('refpt', 'N/A')}")
        print(f"    Reference ppm: {ccpn.get('refppm', 'N/A')}")

    return params


def test_fid_header_reading():
    """Test FID header reading with existing CcpNmr code."""
    print("\n" + "=" * 70)
    print("TEST 2: FID Header Reading (Existing CcpNmr Code)")
    print("=" * 70)

    data_dir = os.path.dirname(__file__)
    fid_path = os.path.join(data_dir, 'hnco_bmr5106_origfid')

    if not os.path.exists(fid_path):
        print(f"ERROR: FID file not found: {fid_path}")
        return None

    # Profile header reading
    start = time.perf_counter()
    try:
        header = readDataFileHeader(fid_path)
    except Exception as e:
        print(f"ERROR: Failed to read FID header: {e}")
        return None
    header_time = time.perf_counter() - start

    print(f"\n  ⏱  FID header read time: {header_time*1000:.2f} ms")

    # Print header info
    print(f"\n  FID Header Information:")
    print(f"    Number of points (np): {header.get('np', 'N/A')}")
    print(f"    Number of traces: {header.get('ntraces', 'N/A')}")
    print(f"    Number of block headers: {header.get('nbheaders', 'N/A')}")
    print(f"    First block: {header.get('firstBlock', 'N/A')}")
    print(f"    Byte swapped: {header.get('swapped', 'N/A')}")

    # Calculate data size
    if 'np' in header and 'ntraces' in header:
        total_points = header['np'] * header['ntraces']
        data_size_mb = total_points * 4 / 1024 / 1024  # 4 bytes per float
        print(f"    Estimated data size: {data_size_mb:.1f} MB")

    return header


def test_varian_params_wrapper():
    """Test VarianParams high-level wrapper."""
    print("\n" + "=" * 70)
    print("TEST 3: VarianParams Wrapper (Existing CcpNmr Code)")
    print("=" * 70)

    data_dir = os.path.dirname(__file__)
    procpar_path = os.path.join(data_dir, 'hnco_bmr5106_procpar')
    fid_path = os.path.join(data_dir, 'hnco_bmr5106_origfid')

    # Profile VarianParams initialization
    start = time.perf_counter()
    try:
        params = VarianParams(procpar_path, data_file=fid_path)
    except Exception as e:
        print(f"ERROR: Failed to create VarianParams: {e}")
        import traceback
        traceback.print_exc()
        return None
    init_time = time.perf_counter() - start

    print(f"\n  ⏱  VarianParams initialization: {init_time*1000:.2f} ms")
    print(f"  ✓  Successfully created VarianParams object")

    # Print params attributes
    print(f"\n  Spectrum Parameters:")
    print(f"    Format: {params.format}")
    print(f"    Dimensions: {params.ndim}D")
    print(f"    Data points: {params.npts}")
    print(f"    Spectral widths (Hz): {params.sw}")
    print(f"    Spectrometer frequencies (MHz): {params.sf}")
    print(f"    Reference points: {params.refpt}")
    print(f"    Reference ppm: {params.refppm}")
    print(f"    Block structure: {params.block}")
    print(f"    Header size: {params.head} bytes")
    print(f"    Block header size: {params.blockHead} bytes")
    print(f"    Byte swap needed: {params.swap}")
    print(f"    Data file: {os.path.basename(params.dataFile)}")

    return params


def compare_with_standalone():
    """Compare performance with standalone benchmark."""
    print("\n" + "=" * 70)
    print("COMPARISON: CcpNmr vs Standalone Benchmark")
    print("=" * 70)

    print("\n  Run `python3 profile_3d_processing.py` to compare with")
    print("  standalone pure Python/NumPy implementation.")

    print("\n  Expected differences:")
    print("    • CcpNmr: Integrated, production-ready, full format support")
    print("    • Standalone: Simple, minimal, benchmark baseline")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TESTING EXISTING CCPNMR VARIAN READER")
    print("=" * 70)

    print("\n⚠️  WARNING: This script currently FAILS due to Python 2 syntax")
    print("=" * 70)
    print("\nThe CcpNmr Varian reader needs Python 2→3 modernization:")
    print("  File: ccpnmr2.4/python/ccp/format/varian/varianFile.py")
    print("  Issues:")
    print("    - except ValueError, e:  → needs: except ValueError as e:")
    print("    - Invalid regex escape sequences (\\d without r-string)")
    print("\nThis script is a TEMPLATE for future testing after modernization.")
    print("For working 3D spectrum tests, use the standalone benchmarks:")
    print("  • python3 profile_3d_processing.py")
    print("  • pytest test_3d_algorithms.py -v")
    print("=" * 70)

    print("\nAttempting to import CcpNmr modules (will likely fail)...")
    print("\nDataset: BMRB 5106 HNCO (Mth1743 protein)")
    print("Format: Varian/Agilent")
    print("Size: 16 MB raw FID + procpar")

    # Run tests (will fail with Python 2 syntax errors)
    procpar_params = test_procpar_parsing()
    fid_header = test_fid_header_reading()
    varian_params = test_varian_params_wrapper()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if procpar_params and fid_header and varian_params:
        print("\n  ✓ All tests passed!")
        print("  ✓ CcpNmr's Varian reader successfully handles 3D HNCO data")
        print("\n  Next steps:")
        print("    1. Compare performance with standalone benchmark")
        print("    2. Test full processing pipeline (FFT, peak picking)")
        print("    3. Validate results against reference data")
    else:
        print("\n  ✗ Some tests failed")
        print("  Check error messages above for details")

    compare_with_standalone()

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
