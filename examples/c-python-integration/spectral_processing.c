#include <math.h>
#include <stdlib.h>

/* 
 * Typical NMR C function: Apodization (line broadening)
 * This applies an exponential window function to FID data
 * Commonly used in NMR signal processing
 */
void exponential_apodization(double* fid_real, double* fid_imag, int size, double lb) {
    /*
     * fid_real, fid_imag: Real and imaginary parts of FID
     * size: Number of data points
     * lb: Line broadening factor (Hz)
     */
    for (int i = 0; i < size; i++) {
        double t = (double)i;  // Time point
        double window = exp(-M_PI * lb * t);  // Exponential decay
        
        fid_real[i] *= window;
        fid_imag[i] *= window;
    }
}

/* 
 * Another common NMR function: Calculate spectral noise level
 * Simple RMS noise calculation from a region of the spectrum
 */
double calculate_noise_level(double* spectrum, int start, int end) {
    double sum_squares = 0.0;
    int count = end - start;
    
    for (int i = start; i < end; i++) {
        sum_squares += spectrum[i] * spectrum[i];
    }
    
    return sqrt(sum_squares / count);
}
