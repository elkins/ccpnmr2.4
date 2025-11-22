# C/Python Integration Example

This directory contains a minimal, self-contained example demonstrating the C/Python integration patterns used in CcpNmr, along with pure Python equivalents.

## Purpose

- **Understand** how C extensions work in CcpNmr
- **Compare** C vs Python performance and complexity  
- **Test** modernization strategies before applying to main codebase
- **Learn** patterns for replacing C with optimized Python

## Files

- `spectral_processing.c` - Original C implementation (NMR apodization)
- `cextension.c` - Python C extension wrapper
- `python_implementation.py` - Pure Python equivalents
- `test_comparison.py` - Correctness and performance tests
- `setup.py` - Build the C extension

## NMR Algorithm: Exponential Apodization

Exponential apodization (line broadening) is a common NMR processing step that applies a window function to FID data to improve signal-to-noise ratio.

## Usage

```bash
# Build the C extension
python setup.py build_ext --inplace

# Run comparison tests
python test_comparison.py
```

## Expected output:
 - Correctness verification (all implementations match)
 - Performance comparison (C vs Python vs NumPy)
 - Usage examples
