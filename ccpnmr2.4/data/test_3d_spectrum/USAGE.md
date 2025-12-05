# 3D NMR Spectrum Testing - Quick Start Guide

This directory contains a real 3D HNCO NMR spectrum and comprehensive testing/profiling tools.

## Dataset

**BMRB Entry 5106** - Mth1743 protein HNCO experiment
- **Size:** 16 MB time-domain data
- **Dimensions:** 3D (¹H, ¹⁵N, ¹³C)
- **Files:**
  - `hnco_bmr5106_origfid` - Raw FID data
  - `hnco_bmr5106_procpar` - Acquisition parameters
  - `hnco_bmr5106.peaks` - Reference peak list

## Quick Start

### 1. Run Performance Profiling

Profile all major NMR processing operations:

```bash
cd /Users/georgeelkins/nmr/ccpnmr2.4/ccpnmr2.4/data/test_3d_spectrum
python3 profile_3d_processing.py
```

**What it profiles:**
- File I/O (reading 16 MB FID)
- Data reshaping (1D → 3D)
- FFT operations (1D, 3D, stepwise)
- Apodization (sine-bell, exponential, Gaussian)
- Zero-filling
- Phase correction
- Peak picking
- Memory operations (transpose, copy, slicing)

**Expected output:**
```
======================================================================
3D NMR SPECTRUM PROCESSING - PERFORMANCE PROFILE
======================================================================

FILE I/O PERFORMANCE
======================================================================
  ⏱  Read procpar file                            0.002 s  (  +0.1 MB)
  ⏱  Read binary FID (16 MB)                      0.045 s  ( +16.0 MB)
  ⏱  Reshape to 3D complex                        0.012 s  ( +32.0 MB)

FFT PERFORMANCE
======================================================================
  ⏱  FFT 1D along axis 0                          0.023 s  ( +32.0 MB)
  ⏱  FFT 1D along axis 1                          0.021 s  (  +0.0 MB)
  ⏱  FFT 1D along axis 2                          0.019 s  (  +0.0 MB)
  ⏱  FFT 3D (single call)                         0.156 s  ( +32.0 MB)
  ⏱  FFT 3D (stepwise, axis by axis)              0.148 s  (  +0.0 MB)

... (more output)
```

### 2. Run Algorithm Tests

Validate algorithms against known results:

```bash
python3 -m pytest test_3d_algorithms.py -v
```

**What it tests:**
- FFT accuracy (Parseval's theorem, Hermitian symmetry)
- Window function properties
- Zero-filling correctness
- Phase correction mathematics
- Peak picking validation
- Numerical stability
- Integration workflow

**Expected output:**
```
============================= test session starts ==============================
test_3d_algorithms.py::TestVarianFIDReader::test_read_procpar PASSED      [  3%]
test_3d_algorithms.py::TestVarianFIDReader::test_read_fid_size PASSED     [  6%]
test_3d_algorithms.py::TestFFTOperations::test_fft_1d_parseval PASSED     [  9%]
test_3d_algorithms.py::TestFFTOperations::test_fft_3d_vs_stepwise PASSED  [ 12%]
...
========================== 30 passed in 12.34s ===============================
```

### 3. Run Specific Test Categories

```bash
# Test only FFT operations
pytest test_3d_algorithms.py::TestFFTOperations -v

# Test only peak picking
pytest test_3d_algorithms.py::TestPeakPicking -v

# Test numerical stability
pytest test_3d_algorithms.py::TestNumericalStability -v

# Run integration test only
pytest test_3d_algorithms.py::test_full_workflow_integration -v
```

## Test Categories

### TestVarianFIDReader
- Procpar file parsing
- Binary FID reading
- Data format validation
- 3D reshaping

### TestFFTOperations
- Parseval's theorem (energy conservation)
- 3D FFT vs stepwise FFT equivalence
- Inverse FFT round-trip
- Hermitian symmetry
- Shift property

### TestApodization
- Sine-bell window properties
- Exponential window properties
- Shape preservation
- Normalization

### TestZeroFilling
- Size increase validation
- Data preservation
- Zero padding correctness
- Resolution improvement

### TestPhaseCorrection
- Zero-order phase correction
- First-order phase correction
- Magnitude preservation

### TestPeakPicking
- Peak detection accuracy
- Threshold behavior
- Intensity ordering
- Local maxima finding

### TestNumericalStability
- Zero input handling
- Single point FFT
- Large value stability
- Small value precision

### TestPeakListValidation
- Reference peak list loading
- Chemical shift ranges
- Peak count validation

## Performance Benchmarks

Typical performance on modern hardware (M1/M2 Mac or equivalent):

| Operation | Time | Memory |
|-----------|------|--------|
| Read 16 MB FID | ~0.05 s | +16 MB |
| Reshape to 3D | ~0.01 s | +32 MB |
| 3D FFT (64×64×512) | ~0.15 s | +32 MB |
| Apodization (per axis) | ~0.02 s | +0 MB |
| Zero-fill 2x | ~0.05 s | +256 MB |
| Peak picking (subset) | ~0.5 s | +0 MB |

**Total peak memory:** ~350 MB for full processing

## Interpreting Results

### Performance Profiling

**Good performance indicators:**
- File I/O < 0.1 seconds
- FFT operations scale roughly linearly with size
- Memory growth matches expected array sizes
- No memory leaks (memory returns after processing)

**Red flags:**
- File I/O > 1 second (disk issue or wrong format)
- FFT > 1 second for 64×64×512 (CPU bottleneck)
- Memory doesn't release after operations (memory leak)
- Peak memory > 1 GB (algorithm inefficiency)

### Algorithm Tests

**All tests should pass.** If tests fail:

1. **FFT accuracy tests fail:**
   - Check NumPy version (requires ≥1.20)
   - Verify no precision loss in conversions
   - Check for NaN/Inf in input data

2. **Peak picking tests fail:**
   - Threshold may need adjustment
   - Local maxima definition may differ
   - Noise estimation method may vary

3. **Integration test fails:**
   - Check file paths are correct
   - Verify FID file is uncorrupted
   - Ensure sufficient memory available

## Common Issues

### "FID file not found"
```bash
# Make sure you're in the correct directory
cd /Users/georgeelkins/nmr/ccpnmr2.4/ccpnmr2.4/data/test_3d_spectrum
pwd  # Should end in test_3d_spectrum

# Check files exist
ls -lh hnco_bmr5106_*
```

### "ImportError: No module named 'pytest'"
```bash
# Install pytest
pip install pytest

# Or with conda
conda install pytest
```

### "Memory error during processing"
```bash
# Process smaller region
# Edit test_3d_algorithms.py, change:
small_region = mag_spectrum[:16, :16, :64]  # Even smaller

# Or increase available memory
# Close other applications
```

### Tests are slow
```bash
# Run specific fast tests
pytest test_3d_algorithms.py -k "not integration" -v

# Skip slow FFT tests
pytest test_3d_algorithms.py -k "not fft_3d" -v

# Use pytest-xdist for parallel execution
pip install pytest-xdist
pytest test_3d_algorithms.py -n 4  # 4 parallel workers
```

## Extending the Tests

### Add Custom Profiling

Edit `profile_3d_processing.py` and add to `PerformanceProfiler`:

```python
def profile_my_algorithm(self, data: np.ndarray):
    """Profile your custom algorithm."""
    print("\n" + "="*70)
    print("MY ALGORITHM PERFORMANCE")
    print("="*70)

    with profile_time("My algorithm operation"):
        result = my_algorithm(data)

    return result

# Add to run_full_profile():
self.profile_my_algorithm(data_3d)
```

### Add Custom Tests

Edit `test_3d_algorithms.py` and add:

```python
class TestMyAlgorithm:
    """Test my custom algorithm."""

    def test_basic_functionality(self):
        """Test basic behavior."""
        data = np.random.randn(8, 8, 16).astype(np.complex64)
        result = my_algorithm(data)

        assert result.shape == data.shape
        assert np.all(np.isfinite(result))

    def test_known_case(self):
        """Test with known input/output."""
        data = np.ones((8, 8, 16), dtype=np.complex64)
        result = my_algorithm(data)

        expected = calculate_expected(data)
        assert_allclose(result, expected, rtol=1e-5)
```

## Automated Testing

### Run on Every Commit

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd ccpnmr2.4/data/test_3d_spectrum
python3 -m pytest test_3d_algorithms.py -q
if [ $? -ne 0 ]; then
    echo "3D algorithm tests failed!"
    exit 1
fi
```

### Continuous Integration

For GitHub Actions (`.github/workflows/test-3d.yml`):

```yaml
name: 3D NMR Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install numpy pytest scipy
      - name: Run 3D tests
        run: |
          cd ccpnmr2.4/data/test_3d_spectrum
          pytest test_3d_algorithms.py -v
```

## References

- **BMRB:** https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr5106/
- **NumPy FFT:** https://numpy.org/doc/stable/reference/routines.fft.html
- **pytest:** https://docs.pytest.org/
- **NMR Processing:** Spin Dynamics (Malcolm Levitt, 2008)

## Support

For issues or questions:
1. Check this USAGE.md file
2. Review README.md for dataset info
3. Check test output for specific error messages
4. File an issue with full error output

---

**Last Updated:** December 2025
**Python Version:** 3.9+
**Dependencies:** numpy, pytest, scipy (optional)
