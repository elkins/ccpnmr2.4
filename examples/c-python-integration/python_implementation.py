import math
import numpy as np

def exponential_apodization_py(fid_real, fid_imag, lb):
    """
    Pure Python implementation of exponential apodization
    
    Args:
        fid_real: List/array of real FID data
        fid_imag: List/array of imaginary FID data  
        lb: Line broadening factor (Hz)
        
    Returns:
        Tuple of (apodized_real, apodized_imag)
    """
    size = len(fid_real)
    result_real = [0.0] * size
    result_imag = [0.0] * size
    
    for i in range(size):
        t = float(i)
        window = math.exp(-math.pi * lb * t)  # Exponential decay
        
        result_real[i] = fid_real[i] * window
        result_imag[i] = fid_imag[i] * window
    
    return result_real, result_imag

def exponential_apodization_numpy(fid_real, fid_imag, lb):
    """
    Optimized NumPy version - this is how we'd actually implement it
    """
    t = np.arange(len(fid_real), dtype=float)
    window = np.exp(-np.pi * lb * t)
    
    return fid_real * window, fid_imag * window
