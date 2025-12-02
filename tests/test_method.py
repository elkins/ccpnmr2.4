"""
Tests for method module.

Tests peak fitting methods (parabolic and Gaussian).
"""

import pytest
import numpy as np
from ccpnmr.analysis.python_impl.method import (
    fit_volume_gaussian3_method,
    fit_center_parabolic_method,
    fit_center_gaussian3_method,
    FIT_VOLUME_GAUSSIAN3_METHOD, NFIT_VOLUME_METHODS,
    FIT_CENTER_PARABOLIC_METHOD, FIT_CENTER_GAUSSIAN3_METHOD,
    NFIT_CENTER_METHODS,
    SMALL_VALUE, FUDGE_MULT,
    _fit_center3
)


class TestConstants:
    """Test method constants."""
    
    def test_volume_method_constants(self):
        """Test volume fitting method constants."""
        assert FIT_VOLUME_GAUSSIAN3_METHOD == 0
        assert NFIT_VOLUME_METHODS == 1
        
    def test_center_method_constants(self):
        """Test center fitting method constants."""
        assert FIT_CENTER_PARABOLIC_METHOD == 0
        assert FIT_CENTER_GAUSSIAN3_METHOD == 1
        assert NFIT_CENTER_METHODS == 2
        
    def test_numerical_constants(self):
        """Test numerical threshold constants."""
        assert SMALL_VALUE == 1.0e-4
        assert FUDGE_MULT == 0.01


class TestFitCenter3:
    """Test internal three-point fitting function."""
    
    def test_symmetric_positive_parabolic(self):
        """Test symmetric positive peak with parabolic fit."""
        # Perfect parabola: y = 10 - x^2, so at x=-1,0,1: y=9,10,9
        offset, b = _fit_center3(9.0, 10.0, 9.0, use_log=False)
        
        assert abs(offset) < 1e-6  # Peak at center
        assert b > 0  # Positive for positive peak
        
    def test_symmetric_negative_parabolic(self):
        """Test symmetric negative peak with parabolic fit."""
        offset, b = _fit_center3(-9.0, -10.0, -9.0, use_log=False)
        
        assert abs(offset) < 1e-6  # Peak at center
        assert b < 0  # Negative for negative peak
        
    def test_offset_right_parabolic(self):
        """Test peak offset to the right."""
        # Peak between x=0 and x=1
        offset, b = _fit_center3(8.0, 10.0, 9.5, use_log=False)
        
        assert offset > 0  # Should be positive (toward w)
        assert offset < 0.5
        
    def test_offset_left_parabolic(self):
        """Test peak offset to the left."""
        # Peak between x=-1 and x=0
        offset, b = _fit_center3(9.5, 10.0, 8.0, use_log=False)
        
        assert offset < 0  # Should be negative (toward u)
        assert offset > -0.5
        
    def test_gaussian_fit(self):
        """Test Gaussian (log-space) fitting."""
        # Gaussian: exp(-x^2), at x=-1,0,1: exp(-1), 1, exp(-1)
        e_minus_1 = np.exp(-1)
        offset, b = _fit_center3(e_minus_1, 1.0, e_minus_1, use_log=True)
        
        assert abs(offset) < 0.01  # Should be centered
        
    def test_small_curvature(self):
        """Test behavior with very flat peak (small curvature)."""
        # Nearly flat
        offset, b = _fit_center3(10.0, 10.0001, 10.0, use_log=False)
        
        # Should return zero offset when curvature is tiny
        assert abs(offset) < 0.5
        
    def test_clamping(self):
        """Test that offsets are clamped to [-0.499, 0.499]."""
        # Extreme asymmetry
        offset, b = _fit_center3(1.0, 10.0, 1.0, use_log=False)
        
        assert offset >= -0.499
        assert offset <= 0.499


class TestParabolicCenterFitting:
    """Test parabolic center fitting."""
    
    def test_1d_centered(self):
        """Test 1D peak at grid center."""
        center = np.zeros(1)
        ym = np.array([9.0])
        yp = np.array([9.0])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, center, 10.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.01  # Centered
        
    def test_1d_offset_right(self):
        """Test 1D peak offset to the right."""
        center = np.zeros(1)
        ym = np.array([8.0])
        yp = np.array([9.5])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, center, 10.0, ym, yp, dim_done)
        
        assert center[0] > 0  # Offset toward yp
        
    def test_1d_offset_left(self):
        """Test 1D peak offset to the left."""
        center = np.zeros(1)
        ym = np.array([9.5])
        yp = np.array([8.0])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, center, 10.0, ym, yp, dim_done)
        
        assert center[0] < 0  # Offset toward ym
        
    def test_2d_both_dimensions(self):
        """Test 2D peak with fitting in both dimensions."""
        center = np.zeros(2)
        ym = np.array([9.0, 8.5])
        yp = np.array([9.0, 9.5])
        dim_done = np.array([True, True])
        
        fit_center_parabolic_method(2, center, 10.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.01  # Dim 0 centered
        assert center[1] > 0  # Dim 1 offset right
        
    def test_2d_one_dimension_disabled(self):
        """Test 2D with only one dimension fitted."""
        center = np.zeros(2)
        ym = np.array([9.0, 8.5])
        yp = np.array([9.0, 9.5])
        dim_done = np.array([True, False])
        
        fit_center_parabolic_method(2, center, 10.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.01  # Dim 0 fitted
        assert center[1] == 0.0  # Dim 1 not fitted
        
    def test_3d_mixed(self):
        """Test 3D with mixed enabled dimensions."""
        center = np.zeros(3)
        ym = np.array([9.0, 8.5, 9.5])
        yp = np.array([9.0, 9.5, 8.0])
        dim_done = np.array([True, True, False])
        
        fit_center_parabolic_method(3, center, 10.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.01  # Dim 0 centered
        assert center[1] > 0  # Dim 1 offset right
        assert center[2] == 0.0  # Dim 2 disabled
        
    def test_negative_peak(self):
        """Test parabolic fit with negative peak."""
        center = np.zeros(1)
        ym = np.array([-9.0])
        yp = np.array([-9.0])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, center, -10.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.01  # Still centered


class TestGaussianCenterFitting:
    """Test Gaussian center fitting."""
    
    def test_1d_gaussian_centered(self):
        """Test 1D Gaussian peak at center."""
        center = np.zeros(1)
        # Gaussian values: exp(-1), 1, exp(-1)
        e_minus_1 = np.exp(-1)
        ym = np.array([e_minus_1])
        yp = np.array([e_minus_1])
        dim_done = np.array([True])
        
        fit_center_gaussian3_method(1, center, 1.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.05  # Should be very close to center
        
    def test_1d_gaussian_offset(self):
        """Test 1D Gaussian peak with offset."""
        center = np.zeros(1)
        # Asymmetric Gaussian
        ym = np.array([0.5])
        yp = np.array([0.8])
        dim_done = np.array([True])
        
        fit_center_gaussian3_method(1, center, 1.0, ym, yp, dim_done)
        
        # Should be offset toward higher neighbor
        assert center[0] > 0
        
    def test_2d_gaussian(self):
        """Test 2D Gaussian fitting."""
        center = np.zeros(2)
        e_minus_1 = np.exp(-1)
        ym = np.array([e_minus_1, 0.6])
        yp = np.array([e_minus_1, 0.9])
        dim_done = np.array([True, True])
        
        fit_center_gaussian3_method(2, center, 1.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.05  # Dim 0 centered
        assert center[1] > 0  # Dim 1 offset right
        
    def test_disabled_dimension(self):
        """Test Gaussian fit with disabled dimension."""
        center = np.zeros(2)
        ym = np.array([0.8, 0.8])
        yp = np.array([0.8, 0.8])
        dim_done = np.array([True, False])
        
        fit_center_gaussian3_method(2, center, 1.0, ym, yp, dim_done)
        
        assert center[1] == 0.0  # Disabled dimension


class TestVolumeCalculation:
    """Test Gaussian volume calculation."""
    
    def test_1d_symmetric(self):
        """Test 1D symmetric peak volume."""
        ym = np.array([0.5])
        yp = np.array([0.5])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, 1.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)
        
    def test_1d_asymmetric(self):
        """Test 1D asymmetric peak volume."""
        ym = np.array([0.3])
        yp = np.array([0.7])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, 1.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)
        
    def test_2d_volume(self):
        """Test 2D peak volume."""
        ym = np.array([0.6, 0.5])
        yp = np.array([0.6, 0.5])
        dim_done = np.array([True, True])
        
        volume = fit_volume_gaussian3_method(2, 1.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)
        
    def test_3d_volume(self):
        """Test 3D peak volume."""
        ym = np.array([0.6, 0.5, 0.7])
        yp = np.array([0.6, 0.5, 0.7])
        dim_done = np.array([True, True, True])
        
        volume = fit_volume_gaussian3_method(3, 1.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)
        
    def test_partial_dimensions(self):
        """Test volume with only some dimensions enabled."""
        ym = np.array([0.6, 0.5])
        yp = np.array([0.6, 0.5])
        dim_done = np.array([True, False])
        
        volume = fit_volume_gaussian3_method(2, 1.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)
        
    def test_negative_peak_volume(self):
        """Test volume calculation for negative peak."""
        ym = np.array([-0.6])
        yp = np.array([-0.6])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, -1.0, ym, yp, dim_done)
        
        assert volume < 0  # Negative peak has negative volume
        assert np.isfinite(volume)
        
    def test_tall_narrow_peak(self):
        """Test volume of tall narrow peak."""
        # Sharp peak (small neighbors)
        ym = np.array([0.1])
        yp = np.array([0.1])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, 10.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)
        
    def test_broad_peak(self):
        """Test volume of broad flat peak."""
        # Broad peak (large neighbors)
        ym = np.array([0.9])
        yp = np.array([0.9])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, 1.0, ym, yp, dim_done)
        
        assert volume > 0
        assert np.isfinite(volume)


class TestEdgeCases:
    """Test edge cases and numerical stability."""
    
    def test_flat_peak(self):
        """Test handling of completely flat region."""
        center = np.zeros(1)
        ym = np.array([10.0])
        yp = np.array([10.0])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, center, 10.0, ym, yp, dim_done)
        
        # Should handle gracefully
        assert abs(center[0]) < 0.5
        
    def test_all_dimensions_disabled(self):
        """Test with all dimensions disabled."""
        center = np.zeros(2)
        ym = np.array([9.0, 9.0])
        yp = np.array([9.0, 9.0])
        dim_done = np.array([False, False])
        
        fit_center_parabolic_method(2, center, 10.0, ym, yp, dim_done)
        
        assert center[0] == 0.0
        assert center[1] == 0.0
        
    def test_volume_all_disabled(self):
        """Test volume with all dimensions disabled."""
        ym = np.array([9.0, 9.0])
        yp = np.array([9.0, 9.0])
        dim_done = np.array([False, False])
        
        volume = fit_volume_gaussian3_method(2, 10.0, ym, yp, dim_done)
        
        # Should be just the central intensity
        assert volume == 10.0
        
    def test_zero_intensity(self):
        """Test handling of zero intensity peak."""
        center = np.zeros(1)
        ym = np.array([0.0])
        yp = np.array([0.0])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, center, 0.0, ym, yp, dim_done)
        
        # Should handle gracefully
        assert np.isfinite(center[0])
        
    def test_very_small_values(self):
        """Test with very small intensity values."""
        ym = np.array([1e-10])
        yp = np.array([1e-10])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, 1e-9, ym, yp, dim_done)
        
        assert np.isfinite(volume)
        
    def test_neighbor_larger_than_center(self):
        """Test when neighbor is larger than supposed peak."""
        # This shouldn't happen with real peaks, but test robustness
        ym = np.array([12.0])  # Larger than center!
        yp = np.array([9.0])
        dim_done = np.array([True])
        
        volume = fit_volume_gaussian3_method(1, 10.0, ym, yp, dim_done)
        
        # Should handle gracefully
        assert np.isfinite(volume)


class TestRealWorldScenarios:
    """Test realistic NMR peak scenarios."""
    
    def test_hsqc_peak(self):
        """Test typical HSQC peak (2D)."""
        # Realistic HSQC peak with some asymmetry
        center = np.zeros(2)
        ym = np.array([0.65, 0.70])
        yp = np.array([0.60, 0.75])
        dim_done = np.array([True, True])
        
        fit_center_gaussian3_method(2, center, 1.0, ym, yp, dim_done)
        
        assert abs(center[0]) < 0.3  # Some offset
        assert abs(center[1]) < 0.3
        
        volume = fit_volume_gaussian3_method(2, 1.0, ym, yp, dim_done)
        assert volume > 0
        
    def test_noesy_peak(self):
        """Test typical NOESY peak (3D)."""
        center = np.zeros(3)
        ym = np.array([0.6, 0.7, 0.5])
        yp = np.array([0.7, 0.6, 0.6])
        dim_done = np.array([True, True, True])
        
        fit_center_gaussian3_method(3, center, 1.0, ym, yp, dim_done)
        
        for i in range(3):
            assert abs(center[i]) < 0.5
            
        volume = fit_volume_gaussian3_method(3, 1.0, ym, yp, dim_done)
        assert volume > 0
        
    def test_comparison_parabolic_vs_gaussian(self):
        """Compare parabolic vs Gaussian fitting."""
        para_center = np.zeros(1)
        gauss_center = np.zeros(1)
        
        ym = np.array([0.6])
        yp = np.array([0.7])
        dim_done = np.array([True])
        
        fit_center_parabolic_method(1, para_center, 1.0, ym, yp, dim_done)
        fit_center_gaussian3_method(1, gauss_center, 1.0, ym, yp, dim_done)
        
        # Both should give positive offset but may differ slightly
        assert para_center[0] > 0
        assert gauss_center[0] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
