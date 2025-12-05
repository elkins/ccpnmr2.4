# 3D HNCO NMR Spectrum Test Dataset

**Source:** BMRB Entry 5106
**Experiment Type:** 3D HNCO (triple-resonance)
**Protein:** Mth1743 from Methanobacterium thermoautotrophicum
**Downloaded:** December 2025

## Dataset Information

### BMRB Entry 5106
- **Entry URL:** [https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr5106/timedomain_data/](https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr5106/timedomain_data/)
- **Full dataset:** [https://bmrb.io/data_library/timedomain.shtml](https://bmrb.io/data_library/timedomain.shtml)
- **License:** Publicly available for research use

### 3D HNCO Experiment

The HNCO experiment is a standard triple-resonance experiment used for backbone assignment in protein NMR. It correlates:
- **¹H** (amide proton)
- **¹⁵N** (amide nitrogen)
- **¹³C** (carbonyl carbon of preceding residue)

This provides sequential connectivity information for protein backbone assignment.

## Files in This Directory

### Time Domain Data (Raw)
- **hnco_bmr5106_origfid** (16 MB)
  - Raw FID (Free Induction Decay) data
  - Varian/Agilent format
  - Complex time-domain data for all 3 dimensions

### Parameters
- **hnco_bmr5106_procpar** (23 KB)
  - Varian/Agilent acquisition parameters
  - Contains spectral widths, carrier frequencies, number of points
  - Required for proper spectrum processing

### Peak List
- **hnco_bmr5106.peaks** (7 KB)
  - Picked peaks from processed spectrum
  - Format: typically includes chemical shifts and intensities
  - Useful for validation and testing

## Spectrum Dimensions

To extract dimension information, check the procpar file:

```bash
grep -E "^(np|sw|at)" hnco_bmr5106_procpar | head -20
```

Typical HNCO dimensions:
- **F3 (direct, ¹H):** ~512-1024 complex points, ~10-12 ppm spectral width
- **F2 (indirect, ¹⁵N):** ~32-64 complex points, ~25-35 ppm spectral width
- **F1 (indirect, ¹³C):** ~32-64 complex points, ~15-20 ppm spectral width

## Data Format

### Varian/Agilent FID Format
The `origfid` file contains binary float32 data in Varian format:
- Alternating real/imaginary pairs
- Order: F3 (direct) varies fastest, then F2, then F1 (slowest)
- Endianness: typically big-endian (check procpar for `bytordp`)

## Usage for Testing/Profiling

This dataset is ideal for:

1. **Testing 3D NMR processing pipelines**
   - Fourier transforms
   - Phase correction
   - Baseline correction
   - Peak picking

2. **Performance profiling**
   - 16 MB raw data provides realistic size
   - 3D operations stress test algorithms
   - Multiple processing steps can be benchmarked

3. **Algorithm validation**
   - Compare with provided peak list
   - Verify chemical shift accuracy
   - Test noise handling

### Ready-to-Use Tools

We've provided two comprehensive testing tools:

**1. Performance Profiling** ([profile_3d_processing.py](profile_3d_processing.py))
```bash
python3 profile_3d_processing.py
```
Profiles: File I/O, FFT, apodization, peak picking, memory usage

**2. Algorithm Validation** ([test_3d_algorithms.py](test_3d_algorithms.py))
```bash
pytest test_3d_algorithms.py -v
```
Tests: FFT accuracy, numerical stability, peak picking, 30+ test cases

**Quick Start Guide:** See [USAGE.md](USAGE.md) for detailed instructions

## Processing Workflow

Typical 3D NMR processing steps:

```python
import numpy as np
from nmrglue import varian  # or equivalent

# 1. Load raw FID
dic, data = varian.read_fid('hnco_bmr5106_origfid', 'hnco_bmr5106_procpar')

# 2. Zero-fill
data = zero_fill_3d(data, target_shape=(512, 128, 128))

# 3. Apodization
data = apply_window_3d(data, window_type='sine-bell')

# 4. Fourier transform
spectrum = fft_3d(data)

# 5. Phase correction
spectrum = phase_correct_3d(spectrum, p0, p1)

# 6. Peak picking
peaks = pick_peaks_3d(spectrum, threshold=5.0)

# 7. Compare with reference peaks
validate_peaks(peaks, 'hnco_bmr5106.peaks')
```

## Expected Results

After processing, you should observe:
- **Number of peaks:** ~100-200 (depending on threshold)
- **Signal-to-noise:** Moderate (typical for biological sample)
- **Resolution:** High enough for peak separation
- **Artifacts:** Minimal (well-acquired data)

## References

### HNCO Experiment
- **Protein NMR:** [https://protein-nmr.org.uk/solution-nmr/spectrum-descriptions/hnco/](https://protein-nmr.org.uk/solution-nmr/spectrum-descriptions/hnco/)
- **BMRB:** [https://bmrb.io/](https://bmrb.io/)

### Related Experiments
This dataset also includes other triple-resonance experiments:
- HNCACB
- CBCA(CO)NH
- HCCHTOCSY
- CC-TOCSY
- CN-NOESY

All available in the parent directory: [bmr5106/timedomain_data/](https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr5106/timedomain_data/)

## Troubleshooting

### File Format Issues
If you have trouble reading the FID:
- Check byte order in procpar (`bytordp` parameter)
- Verify float32 vs int32 data type
- Ensure correct complex point handling (real/imag interleaved)

### Large File Size
The 16 MB FID is time-domain data. After FFT and processing:
- Memory usage will increase (3D complex arrays)
- Consider using memory-mapped arrays for very large datasets
- Profile processing time for performance optimization

## Citation

If you use this data in publications, please cite:
- **BMRB:** Biological Magnetic Resonance Data Bank (https://bmrb.io/)
- **Original deposition:** Check BMRB entry 5106 for citation information

---

**Last Updated:** December 2025
**Dataset Size:** 16 MB (time domain) + 30 KB (metadata/peaks)
**Purpose:** Testing and profiling CcpNmr Python implementations
