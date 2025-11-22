#ifndef SPECTRAL_PROCESSING_H
#define SPECTRAL_PROCESSING_H

void exponential_apodization(double* fid_real, double* fid_imag, int size, double lb);
double calculate_noise_level(double* spectrum, int start, int end);

#endif
