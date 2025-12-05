#!/usr/bin/env python3
"""
Performance Profiling for 3D NMR Spectrum Processing
====================================================

IMPORTANT: This is a STANDALONE BENCHMARK script, NOT part of the CcpNmr codebase.

PURPOSE:
--------
1. Establish **performance baselines** for pure Python/NumPy implementations
   of 3D NMR processing operations (FFT, apodization, peak picking)

2. Provide **correctness validation** with known algorithms and test data

3. Serve as **reference implementation** for future C-to-Python conversions
   of CcpNmr's C modules (e.g., fit.c, geometry.c, cpmg.c)

This script does NOT use existing CcpNmr code. It's written from scratch
to benchmark what pure Python can achieve before optimizing or converting
the existing C/Python hybrid codebase.

RELATIONSHIP TO CCPNMR:
-----------------------
- CcpNmr has C modules in ccpnmr2.4/c/memops/global/ for NMR processing
- This script provides performance targets for converting those C modules
- See CONVERSION_PROGRESS.md for ongoing C→Python conversion work

Operations profiled:
1. File I/O (reading raw FID data)
2. Data manipulation (transpose, reshape, slicing)
3. FFT operations (1D, 2D, 3D)
4. Apodization/windowing
5. Phase correction
6. Baseline correction
7. Peak picking
8. Memory usage

Author: CcpNmr Python Modernization Project
Date: December 2025
"""

import sys
import os
import time
import struct
import numpy as np
from typing import Tuple, List, Dict, Any
import tracemalloc
from contextlib import contextmanager

# Add Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'python'))


@contextmanager
def profile_time(operation_name: str):
    """Context manager for timing operations."""
    start_time = time.perf_counter()
    start_mem = tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0

    yield

    elapsed = time.perf_counter() - start_time
    end_mem = tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0
    mem_delta = (end_mem - start_mem) / 1024 / 1024  # MB

    print(f"  ⏱  {operation_name:<40} {elapsed:>8.3f} s  ({mem_delta:>+7.1f} MB)")


class VarianFIDReader:
    """Read Varian/Agilent FID format."""

    def __init__(self, fid_path: str, procpar_path: str):
        self.fid_path = fid_path
        self.procpar_path = procpar_path
        self.params = {}

    def read_procpar(self) -> Dict[str, Any]:
        """Parse Varian procpar file."""
        params = {}

        with open(self.procpar_path, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 2:
                    param_name = parts[0]
                    # Get value from next line
                    if i + 1 < len(lines):
                        value_line = lines[i + 1].strip()
                        try:
                            # Try to parse as number
                            if '.' in value_line:
                                value = float(value_line.split()[0])
                            else:
                                value = int(value_line.split()[0])
                            params[param_name] = value
                        except (ValueError, IndexError):
                            params[param_name] = value_line
            i += 1

        self.params = params
        return params

    def read_fid(self) -> np.ndarray:
        """Read binary FID data."""
        # Get key parameters
        np_points = self.params.get('np', 1024)

        # Read binary data (Varian format: big-endian float32)
        with open(self.fid_path, 'rb') as f:
            # Skip file header (32 bytes)
            f.seek(32)

            # Read data
            data_bytes = f.read()

        # Convert to float32 array
        n_values = len(data_bytes) // 4
        data = struct.unpack(f'>{n_values}f', data_bytes)  # Big-endian

        return np.array(data, dtype=np.float32)

    def reshape_to_3d(self, data: np.ndarray) -> np.ndarray:
        """Reshape 1D data to 3D complex array."""
        # Varian stores real/imag interleaved
        # Reshape based on typical HNCO dimensions
        # This is approximate - real data would need proper dimension parsing

        # Assume dimensions from typical HNCO
        n1 = 64   # F1 (13C)
        n2 = 64   # F2 (15N)
        n3 = 512  # F3 (1H)

        # Total complex points
        total_complex = n1 * n2 * n3

        if len(data) >= total_complex * 2:
            # Separate real and imaginary
            data_complex = data[::2] + 1j * data[1::2]

            # Reshape to 3D
            data_3d = data_complex[:total_complex].reshape(n1, n2, n3)

            return data_3d
        else:
            print(f"  Warning: Data size mismatch. Expected {total_complex*2}, got {len(data)}")
            # Best effort reshape
            data_complex = data[::2] + 1j * data[1::2]
            return data_complex


class NMRProcessing3D:
    """3D NMR processing operations."""

    @staticmethod
    def apodize_1d(data: np.ndarray, window_type: str = 'sine-bell') -> np.ndarray:
        """Apply apodization window to 1D data."""
        n = len(data)

        if window_type == 'sine-bell':
            # Sine-bell: sin(πt/(n-1)) for t=0,1,...,n-1
            # This ensures window[0]=sin(0)=0 and window[n-1]=sin(π)=0
            window = np.sin(np.pi * np.arange(n) / (n - 1)) if n > 1 else np.ones(1)
        elif window_type == 'exponential':
            lb = 5.0  # Line broadening in Hz
            window = np.exp(-lb * np.arange(n) / n)
        elif window_type == 'gaussian':
            window = np.exp(-((np.arange(n) - n/2) / (n/4))**2)
        else:
            window = np.ones(n)

        return data * window

    @staticmethod
    def apodize_3d(data: np.ndarray, axis: int, window_type: str = 'sine-bell') -> np.ndarray:
        """Apply apodization along one axis of 3D data."""
        n = data.shape[axis]

        # Create window for the specified axis length
        if window_type == 'sine-bell':
            # Sine-bell: sin(πt/(n-1)) for t=0,1,...,n-1
            window = np.sin(np.pi * np.arange(n) / (n - 1)).astype(data.dtype) if n > 1 else np.ones(1, dtype=data.dtype)
        elif window_type == 'exponential':
            lb = 5.0
            window = np.exp(-lb * np.arange(n) / n).astype(data.dtype)
        elif window_type == 'gaussian':
            window = np.exp(-((np.arange(n) - n/2) / (n/4))**2).astype(data.dtype)
        else:
            return data

        # Apply window along the specified axis
        # Reshape window to broadcast correctly
        if axis == 0:
            window_shape = (n, 1, 1)
        elif axis == 1:
            window_shape = (1, n, 1)
        else:  # axis == 2
            window_shape = (1, 1, n)

        window_reshaped = window.reshape(window_shape)
        return data * window_reshaped

    @staticmethod
    def zero_fill_3d(data: np.ndarray, target_shape: Tuple[int, int, int]) -> np.ndarray:
        """Zero-fill to target shape."""
        result = np.zeros(target_shape, dtype=data.dtype)

        s1 = min(data.shape[0], target_shape[0])
        s2 = min(data.shape[1], target_shape[1])
        s3 = min(data.shape[2], target_shape[2])

        result[:s1, :s2, :s3] = data[:s1, :s2, :s3]

        return result

    @staticmethod
    def fft_1d(data: np.ndarray, axis: int = -1) -> np.ndarray:
        """1D FFT along specified axis."""
        return np.fft.fft(data, axis=axis)

    @staticmethod
    def fft_3d(data: np.ndarray) -> np.ndarray:
        """3D FFT."""
        return np.fft.fftn(data)

    @staticmethod
    def fft_3d_stepwise(data: np.ndarray) -> np.ndarray:
        """3D FFT performed axis by axis (more memory efficient)."""
        # F3 (direct dimension)
        result = np.fft.fft(data, axis=2)

        # F2
        result = np.fft.fft(result, axis=1)

        # F1
        result = np.fft.fft(result, axis=0)

        return result

    @staticmethod
    def magnitude_spectrum(data: np.ndarray) -> np.ndarray:
        """Calculate magnitude spectrum."""
        return np.abs(data)

    @staticmethod
    def phase_correct_1d(data: np.ndarray, p0: float = 0.0, p1: float = 0.0) -> np.ndarray:
        """Apply zero and first order phase correction."""
        n = len(data)
        phase = p0 + p1 * np.arange(n) / n
        phase_factor = np.exp(1j * phase * np.pi / 180.0)

        return data * phase_factor

    @staticmethod
    def baseline_correct_1d(data: np.ndarray, method: str = 'polynomial') -> np.ndarray:
        """Baseline correction."""
        if method == 'polynomial':
            # Simple polynomial baseline (order 2)
            x = np.arange(len(data))
            coeffs = np.polyfit(x, data.real, 2)
            baseline = np.polyval(coeffs, x)
            return data - baseline
        else:
            # Mean subtraction
            return data - np.mean(data.real)

    @staticmethod
    def pick_peaks_3d(data: np.ndarray, threshold: float = 5.0) -> List[Tuple[int, int, int, float]]:
        """Simple 3D peak picking."""
        # Calculate noise level from negative values
        # If no negative values, use overall std
        negative_data = data[data < 0]
        if len(negative_data) > 0:
            noise = np.std(negative_data)
        else:
            # Fallback: estimate noise from MAD (median absolute deviation)
            median = np.median(data)
            mad = np.median(np.abs(data - median))
            noise = 1.4826 * mad  # Convert MAD to std for Gaussian distribution

        # Handle edge case where noise is 0 or NaN
        if noise == 0 or not np.isfinite(noise):
            noise = np.std(data) if np.std(data) > 0 else 1.0

        threshold_abs = threshold * noise

        peaks = []

        # Find local maxima (simplified - checks 6 neighbors only)
        for i in range(1, data.shape[0] - 1):
            for j in range(1, data.shape[1] - 1):
                for k in range(1, data.shape[2] - 1):
                    val = data[i, j, k]

                    if val > threshold_abs:
                        # Check if local maximum
                        if (val > data[i-1, j, k] and val > data[i+1, j, k] and
                            val > data[i, j-1, k] and val > data[i, j+1, k] and
                            val > data[i, j, k-1] and val > data[i, j, k+1]):
                            peaks.append((i, j, k, float(val)))

        return peaks


class PerformanceProfiler:
    """Profile NMR processing operations."""

    def __init__(self, fid_path: str, procpar_path: str):
        self.fid_path = fid_path
        self.procpar_path = procpar_path
        self.results = {}

    def profile_file_io(self):
        """Profile file reading operations."""
        print("\n" + "="*70)
        print("FILE I/O PERFORMANCE")
        print("="*70)

        reader = VarianFIDReader(self.fid_path, self.procpar_path)

        with profile_time("Read procpar file"):
            params = reader.read_procpar()

        with profile_time("Read binary FID (16 MB)"):
            data_1d = reader.read_fid()

        print(f"\n  Data points read: {len(data_1d):,}")
        print(f"  Data size: {data_1d.nbytes / 1024 / 1024:.1f} MB")

        with profile_time("Reshape to 3D complex"):
            data_3d = reader.reshape_to_3d(data_1d)

        if isinstance(data_3d, np.ndarray) and data_3d.ndim == 3:
            print(f"  3D shape: {data_3d.shape}")
            print(f"  3D size: {data_3d.nbytes / 1024 / 1024:.1f} MB")
            self.results['data_3d'] = data_3d

        return data_3d

    def profile_fft(self, data: np.ndarray):
        """Profile FFT operations."""
        print("\n" + "="*70)
        print("FFT PERFORMANCE")
        print("="*70)

        # Try different FFT approaches
        print(f"\nInput shape: {data.shape}")

        # 1D FFT along each axis
        with profile_time("FFT 1D along axis 0"):
            result1 = NMRProcessing3D.fft_1d(data, axis=0)

        with profile_time("FFT 1D along axis 1"):
            result2 = NMRProcessing3D.fft_1d(data, axis=1)

        with profile_time("FFT 1D along axis 2"):
            result3 = NMRProcessing3D.fft_1d(data, axis=2)

        # Full 3D FFT
        with profile_time("FFT 3D (single call)"):
            result_3d = NMRProcessing3D.fft_3d(data)

        # Stepwise 3D FFT
        with profile_time("FFT 3D (stepwise, axis by axis)"):
            result_stepwise = NMRProcessing3D.fft_3d_stepwise(data)

        self.results['spectrum_3d'] = result_stepwise

        return result_stepwise

    def profile_apodization(self, data: np.ndarray):
        """Profile apodization operations."""
        print("\n" + "="*70)
        print("APODIZATION PERFORMANCE")
        print("="*70)

        for window_type in ['sine-bell', 'exponential', 'gaussian']:
            with profile_time(f"Apodize axis 0 ({window_type})"):
                _ = NMRProcessing3D.apodize_3d(data.copy(), axis=0, window_type=window_type)

            with profile_time(f"Apodize axis 2 ({window_type})"):
                _ = NMRProcessing3D.apodize_3d(data.copy(), axis=2, window_type=window_type)

    def profile_zero_fill(self, data: np.ndarray):
        """Profile zero-filling operations."""
        print("\n" + "="*70)
        print("ZERO-FILLING PERFORMANCE")
        print("="*70)

        original_shape = data.shape
        print(f"Original shape: {original_shape}")

        # 2x zero-fill
        target = (original_shape[0] * 2, original_shape[1] * 2, original_shape[2] * 2)
        with profile_time(f"Zero-fill to {target}"):
            result = NMRProcessing3D.zero_fill_3d(data, target)

        print(f"  Result size: {result.nbytes / 1024 / 1024:.1f} MB")

        return result

    def profile_magnitude(self, data: np.ndarray):
        """Profile magnitude calculation."""
        print("\n" + "="*70)
        print("MAGNITUDE SPECTRUM PERFORMANCE")
        print("="*70)

        with profile_time("Calculate magnitude (np.abs)"):
            mag = NMRProcessing3D.magnitude_spectrum(data)

        print(f"  Result shape: {mag.shape}")
        print(f"  Result dtype: {mag.dtype}")

        self.results['magnitude'] = mag

        return mag

    def profile_phase_correction(self, data: np.ndarray):
        """Profile phase correction."""
        print("\n" + "="*70)
        print("PHASE CORRECTION PERFORMANCE")
        print("="*70)

        # Phase correct along direct dimension
        n_traces = data.shape[0] * data.shape[1]

        with profile_time(f"Phase correct {n_traces} 1D traces"):
            result = data.copy()
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    result[i, j, :] = NMRProcessing3D.phase_correct_1d(
                        result[i, j, :], p0=0.0, p1=0.0
                    )

    def profile_peak_picking(self, data: np.ndarray):
        """Profile peak picking."""
        print("\n" + "="*70)
        print("PEAK PICKING PERFORMANCE")
        print("="*70)

        # Use magnitude data
        if data.dtype == np.complex64 or data.dtype == np.complex128:
            data = np.abs(data)

        with profile_time("Pick peaks (threshold=5.0)"):
            peaks = NMRProcessing3D.pick_peaks_3d(data, threshold=5.0)

        print(f"  Peaks found: {len(peaks)}")

        if len(peaks) > 0:
            intensities = [p[3] for p in peaks]
            print(f"  Peak intensity range: [{min(intensities):.1f}, {max(intensities):.1f}]")

        self.results['peaks'] = peaks

        return peaks

    def profile_memory_operations(self, data: np.ndarray):
        """Profile memory-intensive operations."""
        print("\n" + "="*70)
        print("MEMORY OPERATIONS PERFORMANCE")
        print("="*70)

        # Transpose
        with profile_time("Transpose (0,1,2) → (2,1,0)"):
            transposed = np.transpose(data, (2, 1, 0))

        # Copy
        with profile_time("Deep copy (np.copy)"):
            copied = np.copy(data)

        # Slicing
        with profile_time("Extract plane [32, :, :]"):
            plane = data[32, :, :]

        with profile_time("Extract spectrum region [16:48, 16:48, :]"):
            region = data[16:48, 16:48, :]

    def run_full_profile(self):
        """Run complete profiling suite."""
        print("="*70)
        print("3D NMR SPECTRUM PROCESSING - PERFORMANCE PROFILE")
        print("="*70)
        print(f"\nDataset: BMRB 5106 HNCO")
        print(f"File: {os.path.basename(self.fid_path)}")

        # Start memory tracking
        tracemalloc.start()

        try:
            # 1. File I/O
            data_3d = self.profile_file_io()

            if isinstance(data_3d, np.ndarray) and data_3d.ndim == 3:
                # 2. Apodization
                self.profile_apodization(data_3d)

                # 3. Zero-filling
                # data_zf = self.profile_zero_fill(data_3d)

                # 4. FFT
                spectrum = self.profile_fft(data_3d)

                # 5. Magnitude
                mag_spectrum = self.profile_magnitude(spectrum)

                # 6. Phase correction
                self.profile_phase_correction(spectrum)

                # 7. Peak picking (use smaller subset for speed)
                small_region = mag_spectrum[:32, :32, :128]
                self.profile_peak_picking(small_region)

                # 8. Memory operations
                self.profile_memory_operations(data_3d)

        finally:
            # Print memory summary
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            print("\n" + "="*70)
            print("MEMORY USAGE SUMMARY")
            print("="*70)
            print(f"  Current memory: {current / 1024 / 1024:.1f} MB")
            print(f"  Peak memory: {peak / 1024 / 1024:.1f} MB")

        print("\n" + "="*70)
        print("PROFILING COMPLETE")
        print("="*70)

        return self.results


def main():
    """Run performance profiling."""
    # File paths
    data_dir = os.path.dirname(__file__)
    fid_path = os.path.join(data_dir, 'hnco_bmr5106_origfid')
    procpar_path = os.path.join(data_dir, 'hnco_bmr5106_procpar')

    # Check files exist
    if not os.path.exists(fid_path):
        print(f"Error: FID file not found: {fid_path}")
        print("Run this script from the test_3d_spectrum directory")
        return 1

    if not os.path.exists(procpar_path):
        print(f"Error: Procpar file not found: {procpar_path}")
        return 1

    # Run profiling
    profiler = PerformanceProfiler(fid_path, procpar_path)
    results = profiler.run_full_profile()

    # Save results
    print("\nResults stored in profiler.results dict")
    print(f"Available keys: {list(results.keys())}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
