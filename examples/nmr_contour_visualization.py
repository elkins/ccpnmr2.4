#!/usr/bin/env python3
"""
Real-World NMR Contour Generation and Visualization
===================================================

Demonstrates contour generation for 2D NMR spectra:
1. Generate realistic 2D spectrum with multiple peaks
2. Calculate contours at multiple levels
3. Visualize with matplotlib
4. Performance benchmarking

Author: CcpNmr Modernization Project
Date: 2024
"""

import sys
import os
import time
import numpy as np

# Add Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from memops.global_.python_impl.contourer import calculate_contours, ContoururInfo, process_chains


def generate_nmr_spectrum_2d(size=(256, 256), n_peaks=20):
    """Generate realistic 2D NMR spectrum with Gaussian peaks."""
    print(f"Generating {size[0]}x{size[1]} 2D NMR spectrum")
    print(f"  Number of peaks: {n_peaks}")
    
    # Create base spectrum with noise
    spectrum = np.random.randn(*size).astype(np.float32) * 0.02
    
    # Add Gaussian peaks with varying intensities
    peak_info = []
    for i in range(n_peaks):
        # Random position
        x0 = np.random.uniform(0.2, 0.8) * size[0]
        y0 = np.random.uniform(0.2, 0.8) * size[1]
        
        # Random peak properties
        intensity = np.random.uniform(0.5, 2.0)
        sigma_x = np.random.uniform(3, 8)
        sigma_y = np.random.uniform(3, 8)
        
        # Create 2D Gaussian
        y, x = np.ogrid[:size[0], :size[1]]
        gaussian = intensity * np.exp(
            -((x - x0)**2 / (2 * sigma_x**2) + (y - y0)**2 / (2 * sigma_y**2))
        )
        spectrum += gaussian.astype(np.float32)
        
        peak_info.append({
            'position': (x0, y0),
            'intensity': intensity,
            'width': (sigma_x, sigma_y)
        })
    
    print(f"  Spectrum range: [{spectrum.min():.3f}, {spectrum.max():.3f}]")
    
    return spectrum, peak_info


def calculate_contour_levels(spectrum, n_levels=8, base_level=0.1):
    """Calculate appropriate contour levels for spectrum."""
    max_val = spectrum.max()
    min_val = spectrum[spectrum > 0].min() if np.any(spectrum > 0) else 0
    
    # Logarithmic spacing from base to max
    levels = base_level * (max_val / base_level) ** (np.arange(n_levels) / (n_levels - 1))
    
    print(f"\nContour levels:")
    for i, level in enumerate(levels):
        print(f"  Level {i+1}: {level:.4f}")
    
    return levels.astype(np.float32)


def generate_contours(spectrum, levels):
    """Generate contours using marching squares algorithm."""
    print(f"\nGenerating contours using marching squares...")
    print(f"  Spectrum size: {spectrum.shape}")
    print(f"  Number of levels: {len(levels)}")
    
    # Set up row callback with stateful row counter
    class RowProvider:
        def __init__(self, data):
            self.data = data
            self.current_row = 0

        def get_row(self):
            """Get current row and advance counter."""
            row = self.data[self.current_row, :]
            self.current_row += 1
            return row

    row_provider = RowProvider(spectrum)
    
    # Create contour info structure
    info = ContoururInfo(
        user_data=row_provider,
        nlevels=len(levels),
        levels=levels,
        npoints=np.array(spectrum.shape, dtype=np.int32),
        offset=np.array([0.0, 0.0], dtype=np.float32),
        scale=np.array([1.0, 1.0], dtype=np.float32),
        get_row_func=lambda rp: rp.get_row()
    )
    
    # Generate contours
    start_time = time.time()
    contours = calculate_contours(info)
    elapsed = time.time() - start_time
    
    print(f"  Contour generation: {elapsed:.3f} seconds")
    print(f"  Total contour levels: {contours.n}")
    
    return contours, elapsed


def analyze_contours(contours):
    """Analyze contour results."""
    print(f"\nContour Analysis:")
    print(f"  Total levels with contours: {contours.n}")

    total_vertices = 0
    for level_idx in range(contours.n):
        if level_idx < len(contours.vertices):
            level_vertices = contours.vertices[level_idx]
            n_verts = level_vertices.nvertices
            total_vertices += n_verts

            if n_verts > 0:
                print(f"  Level {level_idx}: {n_verts} vertices")

    print(f"  Total vertices: {total_vertices}")

    return total_vertices


def visualize_with_matplotlib(spectrum, contours):
    """Visualize spectrum and contours using matplotlib."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection
        
        print(f"\nCreating visualization with matplotlib...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot spectrum as image
        im = ax1.imshow(spectrum, origin='lower', cmap='viridis', aspect='auto')
        ax1.set_title('2D NMR Spectrum (Synthetic)', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Direct Dimension (points)')
        ax1.set_ylabel('Indirect Dimension (points)')
        plt.colorbar(im, ax=ax1, label='Intensity')
        
        # Plot contours
        ax2.set_xlim(0, spectrum.shape[1])
        ax2.set_ylim(0, spectrum.shape[0])
        ax2.set_aspect('equal')
        ax2.set_title('Contour Plot (Marching Squares)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Direct Dimension (points)')
        ax2.set_ylabel('Indirect Dimension (points)')
        
        # Extract and plot contour lines by following chains
        colors = plt.cm.coolwarm(np.linspace(0.2, 0.8, contours.n))

        for level_idx in range(contours.n):
            if level_idx < len(contours.vertices):
                level_vertices = contours.vertices[level_idx]

                # Collect all contour chains for this level
                chains = []

                def collect_chain(user_data, nvertices, first_vertex):
                    """Callback to collect vertices in a chain."""
                    chain = []
                    vertex = first_vertex
                    while vertex is not None:
                        chain.append([vertex.x[0], vertex.x[1]])
                        vertex = vertex.v2  # Follow to next vertex in chain
                    if len(chain) > 1:
                        chains.append(np.array(chain))

                # Process all chains for this level
                process_chains(level_vertices, None, collect_chain)

                # Plot each chain
                for chain in chains:
                    ax2.plot(chain[:, 0], chain[:, 1],
                            color=colors[level_idx], linewidth=1.5, alpha=0.8)
        
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(os.path.dirname(__file__), 'nmr_contour_example.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"  Saved visualization: {output_path}")
        
        # Try to display (may not work in all environments)
        try:
            plt.show()
        except:
            print("  (Display not available in this environment)")
        
        return True
        
    except ImportError:
        print("\nMatplotlib not available - skipping visualization")
        print("Install with: pip install matplotlib")
        return False


def benchmark_performance(sizes=[64, 128, 256, 512]):
    """Benchmark contour generation performance."""
    print("\n" + "="*70)
    print("PERFORMANCE BENCHMARK")
    print("="*70)
    
    print(f"\nBenchmarking contour generation at different sizes...")
    print(f"{'Size':>10} {'Time (s)':>12} {'Speedup':>10}")
    print("-" * 35)
    
    baseline_time = None
    
    for size in sizes:
        # Generate test spectrum
        spectrum = np.random.randn(size, size).astype(np.float32)
        
        # Add a few peaks
        for _ in range(5):
            x0 = np.random.randint(10, size-10)
            y0 = np.random.randint(10, size-10)
            y, x = np.ogrid[:size, :size]
            gaussian = np.exp(-((x - x0)**2 + (y - y0)**2) / 50.0)
            spectrum += gaussian.astype(np.float32)
        
        # Generate contours
        levels = np.array([0.5, 1.0, 1.5, 2.0], dtype=np.float32)

        # Row provider with state
        class RowProvider:
            def __init__(self, data):
                self.data = data
                self.current_row = 0
            def get_row(self):
                row = self.data[self.current_row, :]
                self.current_row += 1
                return row

        row_provider = RowProvider(spectrum)

        info = ContoururInfo(
            user_data=row_provider,
            nlevels=len(levels),
            levels=levels,
            npoints=np.array([size, size], dtype=np.int32),
            offset=np.array([0.0, 0.0], dtype=np.float32),
            scale=np.array([1.0, 1.0], dtype=np.float32),
            get_row_func=lambda rp: rp.get_row()
        )
        
        start = time.time()
        contours = calculate_contours(info)
        elapsed = time.time() - start
        
        if baseline_time is None:
            baseline_time = elapsed
            speedup_str = "baseline"
        else:
            speedup = elapsed / baseline_time
            speedup_str = f"{speedup:.2f}x"
        
        print(f"{size:>6}x{size:<3} {elapsed:>11.4f} {speedup_str:>10}")


def main():
    """Main demonstration."""
    print("="*70)
    print("CCPNMR CONTOUR GENERATION AND VISUALIZATION EXAMPLE")
    print("="*70)
    
    np.random.seed(42)
    
    # Part 1: Generate spectrum
    print("\nPART 1: GENERATE SYNTHETIC 2D NMR SPECTRUM")
    print("-"*70)
    spectrum, peaks = generate_nmr_spectrum_2d(size=(256, 256), n_peaks=15)
    
    # Part 2: Calculate contour levels
    print("\nPART 2: CALCULATE CONTOUR LEVELS")
    print("-"*70)
    levels = calculate_contour_levels(spectrum, n_levels=8, base_level=0.1)
    
    # Part 3: Generate contours
    print("\nPART 3: GENERATE CONTOURS (MARCHING SQUARES)")
    print("-"*70)
    contours, elapsed = generate_contours(spectrum, levels)
    
    # Part 4: Analyze results
    print("\nPART 4: ANALYZE CONTOUR RESULTS")
    print("-"*70)
    total_vertices = analyze_contours(contours)
    
    # Part 5: Visualization
    print("\nPART 5: VISUALIZATION")
    print("-"*70)
    viz_success = visualize_with_matplotlib(spectrum, contours)
    
    # Part 6: Performance benchmark
    # benchmark_performance()  # Commented out for faster demo
    
    # Summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n✓ Generated {spectrum.shape[0]}x{spectrum.shape[1]} spectrum")
    print(f"✓ Calculated {len(levels)} contour levels")
    print(f"✓ Generated {total_vertices} contour vertices")
    print(f"✓ Contour generation time: {elapsed:.3f} seconds")
    if viz_success:
        print(f"✓ Created visualization")
    print(f"✓ All using Numba-accelerated marching squares!")
    print("="*70)


if __name__ == '__main__':
    main()
