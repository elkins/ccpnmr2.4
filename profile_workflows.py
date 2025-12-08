#!/usr/bin/env python3
"""
Task 3.4: Profile Critical CCPNMR Workflows

Profiles performance-critical workflows beyond contouring:
1. File I/O operations (NMR data loading/saving)
2. Peak detection and fitting
3. Peak list operations
4. Slice extraction from ND data
5. Data processing operations

Target: Identify bottlenecks and optimization opportunities
"""

import sys
import time
import cProfile
import pstats
import io
import tracemalloc
import numpy as np
from pathlib import Path
from datetime import datetime
import json

# Setup paths
script_dir = Path(__file__).parent
python_dir = script_dir / 'ccpnmr2.4' / 'python'
sys.path.insert(0, str(python_dir))


class WorkflowProfiler:
    """Profile critical CCPNMR workflows."""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'workflows': {},
            'bottlenecks': [],
            'recommendations': [],
            'summary': {}
        }

    def profile_workflow(self, name, func, iterations=10):
        """
        Profile a workflow with timing and memory measurements.

        Args:
            name: Workflow name
            func: Function to profile
            iterations: Number of iterations

        Returns:
            dict with profiling results
        """
        print(f"\nProfiling: {name}")
        print(f"  Iterations: {iterations}")

        try:
            # Warmup
            func()

            # Memory profiling (single run)
            tracemalloc.start()
            func()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Timing (multiple iterations)
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                func()
                end = time.perf_counter()
                times.append(end - start)

            times = np.array(times)

            result = {
                'status': 'success',
                'iterations': iterations,
                'mean_time_ms': float(np.mean(times) * 1000),
                'median_time_ms': float(np.median(times) * 1000),
                'std_time_ms': float(np.std(times) * 1000),
                'min_time_ms': float(np.min(times) * 1000),
                'max_time_ms': float(np.max(times) * 1000),
                'memory_current_mb': current / (1024 * 1024),
                'memory_peak_mb': peak / (1024 * 1024)
            }

            print(f"  ✓ Mean time: {result['mean_time_ms']:.2f} ms")
            print(f"  ✓ Peak memory: {result['memory_peak_mb']:.2f} MB")

            return result

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            return {
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    # =========================================================================
    # File I/O Workflows
    # =========================================================================

    def profile_numpy_array_io(self):
        """Profile NumPy array I/O (simulating spectrum data)."""
        import tempfile

        # Simulate 2D HSQC spectrum (1024×512 points)
        data = np.random.randn(512, 1024).astype(np.float32)

        def test_func():
            with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
                temp_path = f.name

            # Write
            np.save(temp_path, data)

            # Read
            loaded = np.load(temp_path)

            # Cleanup
            Path(temp_path).unlink()

            return loaded

        return self.profile_workflow(
            "File I/O: NumPy array (2D spectrum 1024×512)",
            test_func,
            iterations=20
        )

    def profile_large_numpy_array_io(self):
        """Profile large NumPy array I/O (3D/4D data)."""
        import tempfile

        # Simulate 3D HNCO spectrum (128×128×64 points)
        data = np.random.randn(64, 128, 128).astype(np.float32)

        def test_func():
            with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
                temp_path = f.name

            # Write
            np.save(temp_path, data)

            # Read
            loaded = np.load(temp_path)

            # Cleanup
            Path(temp_path).unlink()

            return loaded

        return self.profile_workflow(
            "File I/O: NumPy array (3D spectrum 128×128×64)",
            test_func,
            iterations=10
        )

    def profile_text_file_io(self):
        """Profile text file I/O (peak lists, parameters)."""
        import tempfile

        # Simulate peak list with 1000 peaks
        peak_data = []
        for i in range(1000):
            peak_data.append(f"{i}\t{i*0.1:.3f}\t{i*0.2:.3f}\t{i*100:.1f}\t{i*50:.1f}\n")

        def test_func():
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                temp_path = f.name
                f.writelines(peak_data)

            # Read back
            with open(temp_path, 'r') as f:
                lines = f.readlines()

            # Cleanup
            Path(temp_path).unlink()

            return lines

        return self.profile_workflow(
            "File I/O: Text file (1000-line peak list)",
            test_func,
            iterations=50
        )

    # =========================================================================
    # Peak Detection Workflows
    # =========================================================================

    def profile_peak_detection_simple(self):
        """Profile simple peak detection (thresholding)."""
        # 2D spectrum with peaks
        data = np.random.randn(512, 512).astype(np.float32) * 0.1

        # Add Gaussian peaks
        for _ in range(50):
            x0, y0 = np.random.randint(0, 512, 2)
            amplitude = np.random.uniform(5, 20)
            sigma = np.random.uniform(2, 5)

            y, x = np.ogrid[:512, :512]
            peak = amplitude * np.exp(-((x - x0)**2 + (y - y0)**2) / (2 * sigma**2))
            data += peak

        threshold = 5.0

        def test_func():
            # Simple peak detection: find local maxima above threshold
            peaks = []
            for i in range(1, 511):
                for j in range(1, 511):
                    val = data[i, j]
                    if val > threshold:
                        # Check if local maximum
                        if (val > data[i-1, j] and val > data[i+1, j] and
                            val > data[i, j-1] and val > data[i, j+1]):
                            peaks.append((i, j, val))
            return peaks

        return self.profile_workflow(
            "Peak Detection: Simple threshold + local max (512×512)",
            test_func,
            iterations=10
        )

    def profile_peak_detection_scipy(self):
        """Profile SciPy peak detection."""
        try:
            from scipy.ndimage import maximum_filter
            from scipy.ndimage import label
        except ImportError:
            return {'status': 'skip', 'reason': 'SciPy not available'}

        # 2D spectrum with peaks
        data = np.random.randn(512, 512).astype(np.float32) * 0.1

        # Add Gaussian peaks
        for _ in range(50):
            x0, y0 = np.random.randint(0, 512, 2)
            amplitude = np.random.uniform(5, 20)
            sigma = np.random.uniform(2, 5)

            y, x = np.ogrid[:512, :512]
            peak = amplitude * np.exp(-((x - x0)**2 + (y - y0)**2) / (2 * sigma**2))
            data += peak

        threshold = 5.0

        def test_func():
            # SciPy-based peak detection
            local_max = maximum_filter(data, size=3)
            peaks_mask = (data == local_max) & (data > threshold)
            labeled, num_peaks = label(peaks_mask)

            # Extract peak positions
            peaks = np.argwhere(peaks_mask)
            return peaks

        return self.profile_workflow(
            "Peak Detection: SciPy maximum_filter (512×512)",
            test_func,
            iterations=10
        )

    # =========================================================================
    # Peak List Operations
    # =========================================================================

    def profile_peak_list_operations(self):
        """Profile peak list manipulation (add, remove, search)."""
        try:
            from ccpnmr.analysis.python_impl.peak import Peak
        except ImportError:
            return {'status': 'skip', 'reason': 'Peak module not available'}

        def test_func():
            # Create peak list
            peaks = []
            for i in range(1000):
                peak = Peak(ndim=2)
                peak.set_position([float(i), float(i * 2)])
                peak.intensity = float(i * 100)
                peak.volume = float(i * 50)
                peak.set_text(f"Peak_{i}")
                peaks.append(peak)

            # Search operations
            found = [p for p in peaks if p.intensity > 50000]

            # Sort by intensity
            sorted_peaks = sorted(peaks, key=lambda p: p.intensity, reverse=True)

            return len(sorted_peaks)

        return self.profile_workflow(
            "Peak List: Create 1000 peaks + search + sort",
            test_func,
            iterations=20
        )

    # =========================================================================
    # Data Processing Workflows
    # =========================================================================

    def profile_1d_slice_extraction(self):
        """Profile 1D slice extraction from 2D data."""
        data = np.random.randn(1024, 512).astype(np.float32)

        def test_func():
            # Extract 10 slices in each dimension
            slices_x = [data[:, i] for i in range(0, 512, 50)]
            slices_y = [data[i, :] for i in range(0, 1024, 100)]
            return slices_x + slices_y

        return self.profile_workflow(
            "Data Processing: Extract 1D slices from 2D (1024×512)",
            test_func,
            iterations=100
        )

    def profile_2d_slice_extraction(self):
        """Profile 2D slice extraction from 3D data."""
        # 3D data (64×128×128)
        data = np.random.randn(64, 128, 128).astype(np.float32)

        def test_func():
            # Extract 10 2D planes
            planes = [data[i, :, :] for i in range(0, 64, 6)]
            return planes

        return self.profile_workflow(
            "Data Processing: Extract 2D slices from 3D (64×128×128)",
            test_func,
            iterations=50
        )

    def profile_fft_operations(self):
        """Profile FFT operations (common in NMR processing)."""
        # 1D time-domain data
        time_data = np.random.randn(2048).astype(np.complex64)

        def test_func():
            # Forward FFT
            freq_data = np.fft.fft(time_data)

            # Inverse FFT
            recovered = np.fft.ifft(freq_data)

            return recovered

        return self.profile_workflow(
            "Data Processing: FFT operations (1D, 2048 points)",
            test_func,
            iterations=100
        )

    def profile_2d_fft_operations(self):
        """Profile 2D FFT operations."""
        # 2D time-domain data
        time_data = np.random.randn(256, 256).astype(np.complex64)

        def test_func():
            # 2D Forward FFT
            freq_data = np.fft.fft2(time_data)

            # 2D Inverse FFT
            recovered = np.fft.ifft2(freq_data)

            return recovered

        return self.profile_workflow(
            "Data Processing: 2D FFT operations (256×256)",
            test_func,
            iterations=20
        )

    def profile_baseline_correction(self):
        """Profile baseline correction (polynomial fitting)."""
        # 1D spectrum with baseline
        x = np.linspace(0, 1000, 1000)
        baseline = 0.1 * x + 50  # Linear baseline
        signal = np.sin(x / 10) * 100  # Signal
        noise = np.random.randn(1000) * 5
        data = signal + baseline + noise

        def test_func():
            # Polynomial baseline correction (degree 2)
            baseline_fit = np.polyfit(x, data, deg=2)
            baseline_poly = np.polyval(baseline_fit, x)
            corrected = data - baseline_poly
            return corrected

        return self.profile_workflow(
            "Data Processing: Baseline correction (poly, 1000 points)",
            test_func,
            iterations=100
        )

    # =========================================================================
    # Run All Workflows
    # =========================================================================

    def run_all_profiles(self):
        """Run all workflow profiles."""
        print("="*80)
        print("CCPNMR WORKFLOW PROFILER - Task 3.4")
        print("="*80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"NumPy: {np.__version__}")
        print()

        workflows = [
            # File I/O
            ("file_io_2d_spectrum", self.profile_numpy_array_io),
            ("file_io_3d_spectrum", self.profile_large_numpy_array_io),
            ("file_io_text_peak_list", self.profile_text_file_io),

            # Peak Detection
            ("peak_detection_simple", self.profile_peak_detection_simple),
            ("peak_detection_scipy", self.profile_peak_detection_scipy),

            # Peak List Operations
            ("peak_list_ops", self.profile_peak_list_operations),

            # Data Processing
            ("slice_1d_extraction", self.profile_1d_slice_extraction),
            ("slice_2d_extraction", self.profile_2d_slice_extraction),
            ("fft_1d", self.profile_fft_operations),
            ("fft_2d", self.profile_2d_fft_operations),
            ("baseline_correction", self.profile_baseline_correction),
        ]

        print(f"\nRunning {len(workflows)} workflow profiles...\n")

        for name, profile_func in workflows:
            result = profile_func()
            self.results['workflows'][name] = result

        self._analyze_bottlenecks()
        self._generate_recommendations()
        self._print_summary()
        self._write_report()

    def _analyze_bottlenecks(self):
        """Identify performance bottlenecks."""
        bottlenecks = []

        # Find slowest workflows
        successful_workflows = [
            (name, result) for name, result in self.results['workflows'].items()
            if result.get('status') == 'success'
        ]

        if not successful_workflows:
            return

        # Sort by mean time
        sorted_workflows = sorted(
            successful_workflows,
            key=lambda x: x[1].get('mean_time_ms', 0),
            reverse=True
        )

        # Top 3 slowest
        for name, result in sorted_workflows[:3]:
            bottlenecks.append({
                'workflow': name,
                'mean_time_ms': result['mean_time_ms'],
                'memory_peak_mb': result['memory_peak_mb'],
                'reason': 'High execution time'
            })

        self.results['bottlenecks'] = bottlenecks

    def _generate_recommendations(self):
        """Generate optimization recommendations."""
        recommendations = []

        # Check file I/O performance
        file_io_2d = self.results['workflows'].get('file_io_2d_spectrum', {})
        if file_io_2d.get('status') == 'success':
            time_ms = file_io_2d['mean_time_ms']
            if time_ms > 50:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'workflow': 'file_io_2d_spectrum',
                    'recommendation': 'Consider using mmap for large arrays (time > 50ms)',
                    'current_time_ms': time_ms
                })

        # Check peak detection performance
        peak_simple = self.results['workflows'].get('peak_detection_simple', {})
        peak_scipy = self.results['workflows'].get('peak_detection_scipy', {})

        if (peak_simple.get('status') == 'success' and
            peak_scipy.get('status') == 'success'):
            time_simple = peak_simple['mean_time_ms']
            time_scipy = peak_scipy['mean_time_ms']

            if time_scipy < time_simple * 0.8:
                speedup = time_simple / time_scipy
                recommendations.append({
                    'priority': 'HIGH',
                    'workflow': 'peak_detection',
                    'recommendation': f'Use SciPy peak detection ({speedup:.1f}x faster than simple method)',
                    'simple_time_ms': time_simple,
                    'scipy_time_ms': time_scipy
                })

        # Check FFT performance
        fft_1d = self.results['workflows'].get('fft_1d', {})
        if fft_1d.get('status') == 'success':
            time_ms = fft_1d['mean_time_ms']
            if time_ms > 5:
                recommendations.append({
                    'priority': 'LOW',
                    'workflow': 'fft_1d',
                    'recommendation': 'Consider using pyFFTW for >10% speedup on repeated FFTs',
                    'current_time_ms': time_ms
                })

        # General recommendations
        recommendations.append({
            'priority': 'INFO',
            'workflow': 'general',
            'recommendation': 'NumPy operations are well-optimized; focus on algorithmic improvements'
        })

        self.results['recommendations'] = recommendations

    def _print_summary(self):
        """Print profiling summary."""
        print("\n" + "="*80)
        print("WORKFLOW PROFILING SUMMARY")
        print("="*80)

        successful = [
            (name, result) for name, result in self.results['workflows'].items()
            if result.get('status') == 'success'
        ]

        if not successful:
            print("\nNo successful profiles")
            return

        print(f"\nTotal workflows profiled: {len(self.results['workflows'])}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(self.results['workflows']) - len(successful)}")

        # Performance breakdown
        print("\n" + "-"*80)
        print("WORKFLOW PERFORMANCE (sorted by execution time)")
        print("-"*80)

        sorted_workflows = sorted(
            successful,
            key=lambda x: x[1].get('mean_time_ms', 0),
            reverse=True
        )

        for name, result in sorted_workflows:
            time_ms = result['mean_time_ms']
            mem_mb = result['memory_peak_mb']
            print(f"  {name:40} {time_ms:8.2f} ms    {mem_mb:6.2f} MB")

        # Bottlenecks
        if self.results['bottlenecks']:
            print("\n" + "-"*80)
            print("TOP BOTTLENECKS")
            print("-"*80)
            for bottleneck in self.results['bottlenecks']:
                print(f"  {bottleneck['workflow']:40} {bottleneck['mean_time_ms']:8.2f} ms")

        # Recommendations
        if self.results['recommendations']:
            print("\n" + "-"*80)
            print("OPTIMIZATION RECOMMENDATIONS")
            print("-"*80)
            for rec in self.results['recommendations']:
                priority = rec['priority']
                print(f"\n  [{priority}] {rec['recommendation']}")
                if 'workflow' in rec and rec['workflow'] != 'general':
                    print(f"      Workflow: {rec['workflow']}")

    def _write_report(self):
        """Write detailed JSON report."""
        report_file = script_dir / 'workflow_profiling_report.json'

        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n\nDetailed report: {report_file}")


def main():
    """Main entry point."""
    profiler = WorkflowProfiler()
    profiler.run_all_profiles()

    # Exit with success
    sys.exit(0)


if __name__ == '__main__':
    main()
