#!/usr/bin/env python3
"""
Test and compare C extension vs pure Python implementations
"""
import time
import random
import numpy as np

try:
    from cextension import exponential_apodization as exp_apod_c
    C_EXT_AVAILABLE = True
except ImportError:
    print("C extension not available - run: python setup.py build_ext --inplace")
    C_EXT_AVAILABLE = False

from python_implementation import exponential_apodization_py, exponential_apodization_numpy

def generate_test_data(size=1000):
    """Generate synthetic FID data for testing"""
    fid_real = [random.gauss(0, 1) for _ in range(size)]
    fid_imag = [random.gauss(0, 1) for _ in range(size)]
    return fid_real, fid_imag

def test_correctness():
    """Test that all implementations produce the same results"""
    print("=== Correctness Test ===")
    
    fid_real, fid_imag = generate_test_data(100)
    lb = 1.0  # Line broadening
    
    # Test pure Python
    py_real, py_imag = exponential_apodization_py(fid_real, fid_imag, lb)
    
    # Test NumPy
    np_real, np_imag = exponential_apodization_numpy(
        np.array(fid_real), np.array(fid_imag), lb
    )
    
    # Test C extension if available
    if C_EXT_AVAILABLE:
        c_real, c_imag = exp_apod_c(fid_real, fid_imag, lb)
        
        # Compare C vs Python
        max_diff_real = max(abs(c_real[i] - py_real[i]) for i in range(len(py_real)))
        max_diff_imag = max(abs(c_imag[i] - py_imag[i]) for i in range(len(py_imag)))
        
        print(f"C vs Python - Max difference: {max_diff_real:.2e} (real), {max_diff_imag:.2e} (imag)")
        
        if max_diff_real < 1e-10 and max_diff_imag < 1e-10:
            print("✅ All implementations produce identical results")
        else:
            print("❌ Implementations differ!")
    
    # Compare Python vs NumPy
    max_diff_real = max(abs(np_real[i] - py_real[i]) for i in range(len(py_real)))
    max_diff_imag = max(abs(np_imag[i] - py_imag[i]) for i in range(len(py_imag)))
    print(f"NumPy vs Python - Max difference: {max_diff_real:.2e} (real), {max_diff_imag:.2e} (imag)")

def test_performance():
    """Compare performance of different implementations"""
    print("\n=== Performance Test ===")
    
    sizes = [100, 1000, 10000]
    
    for size in sizes:
        print(f"\nData size: {size}")
        fid_real, fid_imag = generate_test_data(size)
        lb = 1.0
        
        # Pure Python
        start = time.time()
        for _ in range(10):  # Multiple runs for better timing
            exponential_apodization_py(fid_real, fid_imag, lb)
        py_time = (time.time() - start) / 10
        print(f"  Pure Python: {py_time:.6f}s")
        
        # NumPy
        np_real, np_imag = np.array(fid_real), np.array(fid_imag)
        start = time.time()
        for _ in range(100):  # More runs since it's faster
            exponential_apodization_numpy(np_real, np_imag, lb)
        np_time = (time.time() - start) / 100
        print(f"  NumPy: {np_time:.6f}s ({py_time/np_time:.1f}x faster)")
        
        # C extension
        if C_EXT_AVAILABLE:
            start = time.time()
            for _ in range(100):
                exp_apod_c(fid_real, fid_imag, lb)
            c_time = (time.time() - start) / 100
            print(f"  C extension: {c_time:.6f}s ({py_time/c_time:.1f}x faster)")

def demonstrate_usage():
    """Show how each implementation would be used"""
    print("\n=== Usage Examples ===")
    
    # Sample FID data (simplified)
    fid_real = [1.0, 0.8, 0.6, 0.4, 0.2]
    fid_imag = [0.0, 0.1, 0.2, 0.1, 0.0]
    lb = 0.5  # Moderate line broadening
    
    print("Original FID (first 5 points):")
    print(f"  Real: {fid_real}")
    print(f"  Imag: {fid_imag}")
    
    # Pure Python
    py_real, py_imag = exponential_apodization_py(fid_real, fid_imag, lb)
    print("\nAfter apodization (Pure Python):")
    print(f"  Real: {[f'{x:.3f}' for x in py_real]}")
    print(f"  Imag: {[f'{x:.3f}' for x in py_imag]}")
    
    # NumPy
    np_real, np_imag = exponential_apodization_numpy(
        np.array(fid_real), np.array(fid_imag), lb
    )
    print("\nAfter apodization (NumPy):")
    print(f"  Real: {[f'{x:.3f}' for x in np_real]}")
    print(f"  Imag: {[f'{x:.3f}' for x in np_imag]}")

if __name__ == "__main__":
    test_correctness()
    test_performance() 
    demonstrate_usage()
