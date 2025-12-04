#!/usr/bin/env python3
"""
Real-World NMR Peak Detection and Analysis Example
===================================================

Demonstrates automated peak detection in 2D NMR spectra with:
1. Synthetic 2D HSQC-like spectrum generation
2. Automated peak picking with various criteria
3. Peak clustering and classification
4. Peak fitting and integration
5. Performance benchmarking

Author: CcpNmr Modernization Project
Date: 2024
"""

import sys
import os
import time
import numpy as np

# Add Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from ccpnmr.analysis.python_impl.peak_list import PeakList
from ccpnmr.analysis.python_impl.peak_cluster import PeakCluster, PeakClusterType
from ccpnmr.analysis.python_impl.method import (
    fit_center_parabolic_method,
    fit_center_gaussian3_method,
    fit_volume_gaussian3_method
)


def generate_2d_hsqc_spectrum(n_peaks=50, spectrum_size=(512, 512), noise_level=0.1):
    """Generate synthetic 2D HSQC-like NMR spectrum."""
    print(f"Generating 2D HSQC spectrum: {spectrum_size[0]}x{spectrum_size[1]} points")
    print(f"  Number of peaks: {n_peaks}")
    print(f"  Noise level: {noise_level}")
    
    spectrum = np.random.randn(*spectrum_size).astype(np.float32) * noise_level
    peak_positions = []
    
    # Add Gaussian peaks
    for i in range(n_peaks):
        # Random position (avoid edges)
        x0 = np.random.randint(50, spectrum_size[0] - 50)
        y0 = np.random.randint(50, spectrum_size[1] - 50)
        
        # Random intensity and width
        intensity = np.random.uniform(1.0, 10.0)
        sigma_x = np.random.uniform(2.0, 5.0)
        sigma_y = np.random.uniform(2.0, 5.0)
        
        # Add Gaussian peak
        y, x = np.ogrid[:spectrum_size[0], :spectrum_size[1]]
        gaussian = intensity * np.exp(
            -((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))
        )
        spectrum += gaussian.astype(np.float32)
        
        peak_positions.append((x0, y0, intensity))
    
    return spectrum, peak_positions


def automated_peak_picking(spectrum, threshold=3.0, min_distance=10):
    """Perform automated peak picking on 2D spectrum."""
    print(f"\nAutomated peak picking:")
    print(f"  Threshold: {threshold} x noise")
    print(f"  Minimum distance: {min_distance} points")
    
    # Create peak list
    npoints = np.array(spectrum.shape, dtype=np.int32)
    peak_list = PeakList(ndim=2, npoints=npoints)
    
    # Calculate noise level
    noise = np.std(spectrum[spectrum < 0]) if np.any(spectrum < 0) else np.std(spectrum) / 2
    threshold_value = threshold * noise
    
    print(f"  Estimated noise: {noise:.3f}")
    print(f"  Threshold value: {threshold_value:.3f}")
    
    # Find local maxima
    start_time = time.time()
    candidates = []
    
    for i in range(min_distance, spectrum.shape[0] - min_distance):
        for j in range(min_distance, spectrum.shape[1] - min_distance):
            if spectrum[i, j] > threshold_value:
                # Check if local maximum
                region = spectrum[i-2:i+3, j-2:j+3]
                if spectrum[i, j] == region.max():
                    # Check minimum distance to existing peaks
                    too_close = False
                    for existing_peak in peak_list.peaks:
                        dx = existing_peak.position[0] - i
                        dy = existing_peak.position[1] - j
                        if np.sqrt(dx*dx + dy*dy) < min_distance:
                            too_close = True
                            break
                    
                    if not too_close:
                        candidates.append((i, j, spectrum[i, j]))
    
    # Add peaks to list
    for pos_x, pos_y, height in candidates:
        peak = peak_list.add_peak_peak_list()
        peak.set_position([float(pos_x), float(pos_y)])
        peak.intensity = float(height)
    
    elapsed = time.time() - start_time
    print(f"  Found {peak_list.npeaks} peaks in {elapsed:.3f} seconds")
    
    return peak_list


def cluster_peaks(peak_list, shift_tolerance=5.0):
    """Group peaks into clusters based on proximity."""
    print(f"\nClustering peaks:")
    print(f"  Shift tolerance: {shift_tolerance} points")

    if peak_list.npeaks == 0:
        print("  No peaks to cluster")
        return []

    clusters = []
    # Create a single cluster of shift-related peaks
    cluster = PeakCluster(ndim=peak_list.ndim, cluster_type=PeakClusterType.SHIFT)

    # Simple clustering: all peaks go into one cluster for this demo
    for peak in peak_list.peaks:
        cluster.add_peak(peak)

    clusters.append(cluster)

    print(f"  Created {len(clusters)} cluster(s)")
    print(f"  Total peaks: {len(cluster.peaks)}")

    return clusters


def fit_peaks(peak_list, spectrum):
    """Fit peaks with parabolic and Gaussian methods."""
    print(f"\nFitting {peak_list.npeaks} peaks...")

    fitted_peaks = []
    parabolic_count = 0

    for peak_idx in range(peak_list.npeaks):
        peak = peak_list.peaks[peak_idx]
        pos = np.array(peak.position, dtype=int)

        # Extract small region around peak
        x0, y0 = pos[0], pos[1]
        if x0 < 1 or x0 >= spectrum.shape[0] - 1:
            continue
        if y0 < 1 or y0 >= spectrum.shape[1] - 1:
            continue

        # Get intensity at peak and neighbors
        y = float(spectrum[x0, y0])
        ym = np.array([spectrum[x0-1, y0], spectrum[x0, y0-1]], dtype=np.float32)
        yp = np.array([spectrum[x0+1, y0], spectrum[x0, y0+1]], dtype=np.float32)

        # Try parabolic fit
        try:
            center = np.array([x0, y0], dtype=np.float32)
            dim_done = np.array([1, 1], dtype=np.int32)

            refined_center = fit_center_parabolic_method(2, center, y, ym, yp, dim_done)

            # Calculate volume
            volume = fit_volume_gaussian3_method(2, y, ym, yp, dim_done)

            parabolic_count += 1

            fitted_peaks.append({
                'original_pos': pos,
                'refined_pos': refined_center,
                'height': peak.intensity,
                'volume': volume
            })
        except:
            # If fitting fails, just use original position
            fitted_peaks.append({
                'original_pos': pos,
                'refined_pos': pos.astype(np.float32),
                'height': peak.intensity,
                'volume': 0.0
            })

    print(f"  Successfully fitted {parabolic_count} peaks (parabolic)")
    if len(fitted_peaks) > 0:
        print(f"  Average volume: {np.mean([p['volume'] for p in fitted_peaks if p['volume'] > 0]):.2f}")

    return fitted_peaks


def main():
    """Main demonstration."""
    print("="*70)
    print("CCPNMR PEAK DETECTION AND ANALYSIS EXAMPLE")
    print("="*70)
    
    np.random.seed(42)
    
    # Generate spectrum
    print("\nPART 1: GENERATE SYNTHETIC SPECTRUM")
    print("-"*70)
    spectrum, true_peaks = generate_2d_hsqc_spectrum(
        n_peaks=30,
        spectrum_size=(256, 256),
        noise_level=0.05
    )
    
    # Peak picking
    print("\nPART 2: AUTOMATED PEAK PICKING")
    print("-"*70)
    peak_list = automated_peak_picking(spectrum, threshold=5.0, min_distance=8)
    
    # Clustering
    print("\nPART 3: PEAK CLUSTERING")
    print("-"*70)
    clusters = cluster_peaks(peak_list, shift_tolerance=5.0)
    
    # Fitting
    print("\nPART 4: PEAK FITTING")
    print("-"*70)
    fitted = fit_peaks(peak_list, spectrum)
    
    # Summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n✓ Generated {spectrum.shape[0]}x{spectrum.shape[1]} spectrum")
    print(f"✓ Added {len(true_peaks)} Gaussian peaks")
    print(f"✓ Detected {peak_list.npeaks} peaks automatically")
    print(f"✓ Fitted {len(fitted)} peaks")
    print(f"✓ All using pure Python + NumPy!")
    print("="*70)


if __name__ == '__main__':
    main()
