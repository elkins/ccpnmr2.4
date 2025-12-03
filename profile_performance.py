#!/usr/bin/env python
"""
Performance profiling script for key CcpNmr modules.

This script profiles critical code paths and generates performance reports:
- Peak detection and fitting
- Contour generation
- Structural alignment (Kabsch)
- Block file I/O
- Linear algebra operations

Usage:
    python profile_performance.py [--detailed] [--module=MODULE]
    
    --detailed: Generate line-by-line profiling
    --module: Profile specific module (peak, contour, structure, block, linalg)
"""

import sys
import time
import cProfile
import pstats
from pstats import SortKey
import numpy as np
from io import StringIO
import argparse


def profile_peak_detection():
    """Profile peak detection and clustering."""
    print("\n" + "="*60)
    print("PROFILING: Peak Detection")
    print("="*60)
    
    from ccpnmr.analysis.python_impl.peak_list import PeakList
    from ccpnmr.analysis.python_impl.peak_cluster import cluster_peaks
    
    # Create test spectrum data
    size = 512
    data = np.random.randn(size, size).astype(np.float32)
    # Add some peaks
    for _ in range(50):
        x, y = np.random.randint(50, size-50, 2)
        data[x-2:x+3, y-2:y+3] += 10.0
    
    # Profile peak finding
    peak_list = PeakList(ndim=2, npoints=np.array([size, size]))
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    start = time.perf_counter()
    
    # Simulate peak picking
    threshold = 2.0
    candidates = np.argwhere(data > threshold)
    for pos in candidates[:100]:  # Limit to 100 peaks
        peak = peak_list.add_peak_peak_list()
        peak.set_position(pos.astype(np.float32))
        peak.set_height(float(data[tuple(pos)]))
    
    # Cluster peaks
    if peak_list.npeaks > 0:
        clusters = cluster_peaks(peak_list, threshold=5.0)
    
    end = time.perf_counter()
    
    profiler.disable()
    
    # Print results
    print(f"Time: {(end-start)*1000:.2f} ms")
    print(f"Peaks found: {peak_list.npeaks}")
    print(f"Throughput: {peak_list.npeaks/(end-start):.0f} peaks/sec")
    print("\nTop 10 functions:")
    
    s = StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
    print(s.getvalue())


def profile_contour_generation():
    """Profile contour generation with marching squares."""
    print("\n" + "="*60)
    print("PROFILING: Contour Generation")
    print("="*60)
    
    from memops.global_.python_impl.contourer import calculate_contours, ContoururInfo
    
    # Create test data (gaussian peaks)
    size = 256
    x = np.linspace(-3, 3, size)
    y = np.linspace(-3, 3, size)
    X, Y = np.meshgrid(x, y)
    data = np.exp(-(X**2 + Y**2)) + 0.5*np.exp(-((X-1)**2 + (Y-1)**2))
    data = data.astype(np.float32)
    
    # Row access function
    def get_row(user_data):
        return user_data['data'][user_data['row'], :]
    
    user_data = {'data': data, 'row': 0}
    info = ContoururInfo(
        user_data=user_data,
        nlevels=5,
        levels=np.array([0.1, 0.2, 0.4, 0.6, 0.8]),
        npoints=np.array([size, size]),
        offset=np.array([0.0, 0.0]),
        scale=np.array([1.0, 1.0]),
        get_row_func=get_row
    )
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    start = time.perf_counter()
    
    # Generate contours
    contours = calculate_contours(info)
    
    end = time.perf_counter()
    
    profiler.disable()
    
    # Print results
    total_vertices = sum(c.nvertices for c in contours.vertices)
    print(f"Time: {(end-start)*1000:.2f} ms")
    print(f"Levels: {contours.n}")
    print(f"Total vertices: {total_vertices}")
    print(f"Throughput: {size*size/(end-start)/1e6:.2f} Mpixels/sec")
    print("\nTop 10 functions:")
    
    s = StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
    print(s.getvalue())


def profile_kabsch_alignment():
    """Profile Kabsch alignment (RMSD calculation and superposition)."""
    print("\n" + "="*60)
    print("PROFILING: Kabsch Alignment (RMSD + Superposition)")
    print("="*60)
    
    from ccp.c.python_impl.struct_util import align_coordinates, calculate_rmsd
    
    # Create test structures (100 atoms)
    natoms = 100
    coords1 = np.random.randn(natoms, 3).astype(np.float32)
    
    # Create second structure with rotation + noise
    angle = 0.5
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)
    coords2 = coords1 @ R.T + 0.1 * np.random.randn(natoms, 3).astype(np.float32)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    start = time.perf_counter()
    
    # Run alignments
    for _ in range(100):
        initial_rmsd = calculate_rmsd(coords1, coords2)
        rotation, translation = align_coordinates(coords1, coords2)
        # Apply transformation to coords2
        aligned = (coords2 - translation) @ rotation.T
        final_rmsd = calculate_rmsd(coords1, aligned)
    
    end = time.perf_counter()
    
    profiler.disable()
    
    # Print results
    avg_time = (end - start) / 100
    print(f"Average time per alignment: {avg_time*1000:.2f} ms")
    print(f"Atoms: {natoms}")
    print(f"Initial RMSD: {initial_rmsd:.4f} Å")
    print(f"Final RMSD: {final_rmsd:.4f} Å")
    print(f"Throughput: {100/(end-start):.0f} alignments/sec")
    print("\nTop 10 functions:")
    
    s = StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
    print(s.getvalue())


def profile_block_file():
    """Profile block file I/O operations."""
    print("\n" + "="*60)
    print("PROFILING: Block File I/O")
    print("="*60)
    
    import tempfile
    import os
    from memops.global_.python_impl.block_file import new_block_file
    from memops.global_.python_impl.mem_cache import new_mem_cache
    
    # Create temporary file
    fd, tmpfile = tempfile.mkstemp(suffix='.dat')
    os.close(fd)
    
    try:
        # Create block file (512x512 2D spectrum)
        size = 512
        block_size = 32
        
        cache = new_mem_cache(remove_callback=None, cache_size=50)
        block_file = new_block_file(
            file=tmpfile,
            ndim=2,
            points=np.array([size, size]),
            block_size=np.array([block_size, block_size]),
            dim_wrapped=np.array([False, False]),
            bytes_per_point=4,
            big_endian=False,
            padded=True,
            header=0,
            integer=False,
            writeable=True,
            block_header=0
        )
        
        block_file.open_file()
        
        # Write test data
        print("Writing test data...")
        test_data = np.random.randn(size, size).astype(np.float32)
        for i in range(0, size, block_size):
            for j in range(0, size, block_size):
                block_file.set_box(
                    box_min=np.array([i, j]),
                    box_max=np.array([min(i+block_size, size), min(j+block_size, size)]),
                    values=test_data[i:i+block_size, j:j+block_size]
                )
        block_file.save()
        
        # Profile random access
        profiler = cProfile.Profile()
        profiler.enable()
        
        start = time.perf_counter()
        
        # Random point access
        for _ in range(1000):
            x, y = np.random.randint(0, size, 2)
            value = block_file.get_point(np.array([x, y]))
        
        # Random box access
        for _ in range(100):
            x, y = np.random.randint(0, size-block_size, 2)
            box = block_file.get_box(
                box_min=np.array([x, y]),
                box_max=np.array([x+block_size, y+block_size])
            )
        
        end = time.perf_counter()
        
        profiler.disable()
        
        block_file.close_file()
        
        # Print results
        print(f"Time: {(end-start)*1000:.2f} ms")
        print(f"Point accesses: 1000")
        print(f"Box accesses: 100")
        print(f"Throughput: {1100/(end-start):.0f} ops/sec")
        print("\nTop 10 functions:")
        
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats(SortKey.CUMULATIVE)
        stats.print_stats(10)
        print(s.getvalue())
    
    finally:
        # Cleanup
        if os.path.exists(tmpfile):
            os.unlink(tmpfile)


def profile_linear_algebra():
    """Profile linear algebra operations."""
    print("\n" + "="*60)
    print("PROFILING: Linear Algebra")
    print("="*60)
    
    from memops.c.python_impl.linalg import solve_linear_system, determinant
    
    # Test various matrix sizes
    sizes = [10, 50, 100, 200]
    
    for n in sizes:
        A = np.random.randn(n, n).astype(np.float32)
        b = np.random.randn(n).astype(np.float32)
        
        # Make A well-conditioned
        A = A @ A.T + n * np.eye(n, dtype=np.float32)
        
        start = time.perf_counter()
        
        for _ in range(10):
            x = solve_linear_system(A, b)
            det = determinant(A)
        
        end = time.perf_counter()
        
        avg_time = (end - start) / 10
        print(f"\nMatrix size {n}x{n}:")
        print(f"  Average time: {avg_time*1000:.2f} ms")
        print(f"  Throughput: {10/(end-start):.1f} solves/sec")
        
        # Verify solution
        residual = np.linalg.norm(A @ x - b)
        print(f"  Residual: {residual:.2e}")


def main():
    parser = argparse.ArgumentParser(description='Profile CcpNmr performance')
    parser.add_argument('--detailed', action='store_true',
                       help='Generate detailed line profiling')
    parser.add_argument('--module', type=str, default='all',
                       choices=['all', 'peak', 'contour', 'structure', 'block', 'linalg'],
                       help='Module to profile')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CcpNmr Performance Profiling")
    print("="*60)
    print(f"NumPy version: {np.__version__}")
    print(f"Python version: {sys.version}")
    
    # Profile selected modules
    if args.module in ['all', 'peak']:
        profile_peak_detection()
    
    if args.module in ['all', 'contour']:
        profile_contour_generation()
    
    if args.module in ['all', 'structure']:
        profile_kabsch_alignment()
    
    if args.module in ['all', 'block']:
        profile_block_file()
    
    if args.module in ['all', 'linalg']:
        profile_linear_algebra()
    
    print("\n" + "="*60)
    print("Profiling Complete")
    print("="*60)
    print("\nSee OPTIMIZATION_GUIDE.md for performance tips.")


if __name__ == '__main__':
    # Set up path
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ccpnmr2.4', 'python'))
    
    main()
