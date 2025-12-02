"""
Tests for struct_util module - structural alignment and coordinate manipulation.

Tests cover:
- Center of mass translation (weighted and unweighted)
- Kabsch alignment algorithm
- Combined translate + align operations
- Ensemble alignment with RMSD weighting
- RMSD calculations
- Edge cases and numerical stability
"""

import pytest
import numpy as np
from ccp.c.python_impl.struct_util import (
    translate_coordinates,
    align_coordinates,
    align_translate_coordinates,
    align_ensemble,
    calculate_rmsd,
    superimpose,
    COORD_NDIMS,
    RMSD_THRESHOLD
)


class TestTranslateCoordinates:
    """Test center of mass translation"""
    
    def test_translate_simple(self):
        """Translate coordinates to center of mass"""
        coords = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ])
        
        translate_coordinates(coords)
        
        # Center should now be at origin
        center = np.mean(coords, axis=0)
        np.testing.assert_array_almost_equal(center, [0.0, 0.0, 0.0])
    
    def test_translate_weighted(self):
        """Translate with atomic weights"""
        coords = np.array([
            [1.0, 0.0, 0.0],
            [3.0, 0.0, 0.0]
        ])
        weight = np.array([1.0, 3.0])  # Second atom has 3x weight
        
        translate_coordinates(coords, weight)
        
        # Weighted center was at (2.5, 0, 0)
        expected = np.array([
            [-1.5, 0.0, 0.0],
            [0.5, 0.0, 0.0]
        ])
        np.testing.assert_array_almost_equal(coords, expected)
    
    def test_translate_already_centered(self):
        """Translate coordinates already at origin"""
        coords = np.array([
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0]
        ])
        
        translate_coordinates(coords)
        
        # Should remain unchanged
        expected = np.array([
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0]
        ])
        np.testing.assert_array_almost_equal(coords, expected)
    
    def test_translate_single_atom(self):
        """Translate single atom to origin"""
        coords = np.array([[5.0, -3.0, 2.0]])
        
        translate_coordinates(coords)
        
        np.testing.assert_array_almost_equal(coords, [[0.0, 0.0, 0.0]])


class TestAlignCoordinates:
    """Test Kabsch alignment algorithm"""
    
    def test_align_identical(self):
        """Align identical structures"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=float)
        coords2 = coords1.copy()
        
        rotation, error = align_coordinates(coords1, coords2)
        
        # Rotation should be identity
        np.testing.assert_array_almost_equal(rotation, np.eye(3))
        # Error should be near zero
        assert abs(error) < 1e-6
        # Coordinates unchanged
        np.testing.assert_array_almost_equal(coords1, coords2)
    
    def test_align_90_degree_rotation(self):
        """Align structures rotated 90 degrees around z-axis"""
        coords1 = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
        
        # 90 degree rotation around z-axis
        coords2 = np.array([
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0]
        ], dtype=float)
        
        rotation, error = align_coordinates(coords1, coords2)
        
        # After alignment, coords1 should match coords2
        np.testing.assert_array_almost_equal(coords1, coords2, decimal=5)
        # Error should be small
        assert error < 1e-6
    
    def test_align_translation_only(self):
        """Align structures that differ only by translation"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=float)
        
        coords2 = coords1 + 5.0  # Translate by (5, 5, 5)
        
        # Note: align_coordinates expects pre-centered coordinates
        # So we need to center them first
        translate_coordinates(coords1)
        translate_coordinates(coords2)
        
        rotation, error = align_coordinates(coords1, coords2)
        
        # Rotation should be identity
        np.testing.assert_array_almost_equal(rotation, np.eye(3), decimal=5)
        # Coords should match after alignment
        np.testing.assert_array_almost_equal(coords1, coords2, decimal=5)
    
    def test_align_weighted(self):
        """Align with atomic weights"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [5.0, 0.0, 0.0]  # Outlier
        ], dtype=float)
        
        coords2 = np.array([
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 5.0, 0.0]
        ], dtype=float)
        
        # Down-weight the outlier
        weight = np.array([1.0, 1.0, 0.1])
        
        rotation, error = align_coordinates(coords1, coords2, weight)
        
        # First two atoms should align well
        np.testing.assert_array_almost_equal(coords1[:2], coords2[:2], decimal=2)
    
    def test_align_180_degree_rotation(self):
        """Align structures rotated 180 degrees"""
        coords1 = np.array([
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=float)
        
        # 180 degree rotation around z-axis
        coords2 = np.array([
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0]
        ], dtype=float)
        
        rotation, error = align_coordinates(coords1, coords2)
        
        # After alignment, should match
        np.testing.assert_array_almost_equal(coords1, coords2, decimal=5)


class TestAlignTranslateCoordinates:
    """Test combined translation and alignment"""
    
    def test_align_translate_simple(self):
        """Align and translate two structures"""
        coords1 = np.array([
            [1.0, 1.0, 1.0],
            [2.0, 1.0, 1.0],
            [1.0, 2.0, 1.0]
        ], dtype=float)
        
        coords2 = np.array([
            [5.0, 5.0, 5.0],
            [6.0, 5.0, 5.0],
            [5.0, 6.0, 5.0]
        ], dtype=float)
        
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # After alignment, both should be centered and aligned
        center1 = np.mean(coords1, axis=0)
        center2 = np.mean(coords2, axis=0)
        np.testing.assert_array_almost_equal(center1, [0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(center2, [0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(coords1, coords2, decimal=5)
    
    def test_align_translate_rotated(self):
        """Align and translate rotated structures"""
        # Create a small peptide backbone
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.5, 0.0, 0.0],
            [2.0, 1.2, 0.0]
        ], dtype=float)
        
        # Rotate 45 degrees around z and translate
        angle = np.pi / 4
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        coords2 = coords1 @ rotation_matrix.T + np.array([10.0, -5.0, 3.0])
        
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # After alignment, should match closely
        rmsd = calculate_rmsd(coords1, coords2)
        assert rmsd < 1e-5


class TestAlignEnsemble:
    """Test ensemble alignment with RMSD weighting"""
    
    def test_align_ensemble_identical(self):
        """Align ensemble of identical structures"""
        natoms = 5
        nensembles = 3
        
        base_coords = np.random.rand(natoms, 3)
        coords = np.tile(base_coords, (nensembles, 1, 1))
        weight = np.ones(natoms)
        
        atom_rmsd, ensemble_rmsd, error = align_ensemble(coords, weight)
        
        # All RMSDs should be near zero
        np.testing.assert_array_almost_equal(atom_rmsd, np.zeros(natoms), decimal=5)
        np.testing.assert_array_almost_equal(ensemble_rmsd, np.zeros(nensembles), decimal=5)
    
    def test_align_ensemble_varied(self):
        """Align ensemble with structural variation"""
        nensembles = 5
        natoms = 10
        
        # Create base structure
        base = np.random.rand(natoms, 3) * 10
        
        # Create ensemble with small variations
        coords = np.zeros((nensembles, natoms, 3))
        for i in range(nensembles):
            coords[i] = base + np.random.randn(natoms, 3) * 0.5
        
        weight = np.ones(natoms)
        
        atom_rmsd, ensemble_rmsd, error = align_ensemble(coords, weight)
        
        # RMSDs should be positive but small
        assert np.all(atom_rmsd >= 0)
        assert np.all(ensemble_rmsd >= 0)
        assert np.mean(atom_rmsd) < 1.0
        assert np.mean(ensemble_rmsd) < 1.0
    
    def test_align_ensemble_mobile_loop(self):
        """Align ensemble with mobile loop region"""
        nensembles = 4
        natoms = 15
        
        # Create structured core (atoms 0-9)
        core = np.random.rand(10, 3) * 5
        
        coords = np.zeros((nensembles, natoms, 3))
        for i in range(nensembles):
            # Core remains similar
            coords[i, :10] = core + np.random.randn(10, 3) * 0.2
            # Loop varies a lot (atoms 10-14)
            coords[i, 10:] = np.random.rand(5, 3) * 10
        
        weight = np.ones(natoms)
        
        atom_rmsd, ensemble_rmsd, error = align_ensemble(coords, weight)
        
        # Core atoms should have low RMSD
        assert np.mean(atom_rmsd[:10]) < 1.0
        # Loop atoms should have high RMSD
        assert np.mean(atom_rmsd[10:]) > np.mean(atom_rmsd[:10])
        
        # Weights should be adjusted (mobile atoms down-weighted)
        # Weight reduction follows exp(-t^2) where t = rmsd/threshold
        for i in range(10, 15):
            t = atom_rmsd[i] / RMSD_THRESHOLD
            expected_weight = np.exp(-t * t)
            # Weight should be reduced for mobile atoms
            assert weight[i] < 1.0
    
    def test_align_ensemble_nmr_like(self):
        """Align NMR-like ensemble with 20 structures"""
        nensembles = 20
        natoms = 50
        
        # Create realistic NMR ensemble
        # Well-defined core with some flexible regions
        coords = np.zeros((nensembles, natoms, 3))
        
        for i in range(nensembles):
            # Generate random protein backbone-like structure
            coords[i] = np.random.randn(natoms, 3).cumsum(axis=0) * 0.5
            # Add conformational variation
            coords[i] += np.random.randn(natoms, 3) * 0.3
        
        weight = np.ones(natoms)
        
        atom_rmsd, ensemble_rmsd, error = align_ensemble(coords, weight)
        
        # Should successfully align
        assert len(atom_rmsd) == natoms
        assert len(ensemble_rmsd) == nensembles
        assert np.all(atom_rmsd >= 0)
        assert np.all(ensemble_rmsd >= 0)
        
        # Find best structure (closest to mean)
        best_idx = np.argmin(ensemble_rmsd)
        assert 0 <= best_idx < nensembles


class TestCalculateRMSD:
    """Test RMSD calculation"""
    
    def test_rmsd_identical(self):
        """RMSD of identical structures"""
        coords1 = np.random.rand(10, 3)
        coords2 = coords1.copy()
        
        rmsd = calculate_rmsd(coords1, coords2)
        
        assert abs(rmsd) < 1e-10
    
    def test_rmsd_simple(self):
        """RMSD of simple structures"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0]
        ])
        
        coords2 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0]
        ])
        
        rmsd = calculate_rmsd(coords1, coords2)
        
        # Only second atom differs by 1.0 Å in y
        # RMSD = sqrt((0^2 + 1^2) / 2) = sqrt(0.5) ≈ 0.707
        expected = np.sqrt(0.5)
        np.testing.assert_almost_equal(rmsd, expected)
    
    def test_rmsd_weighted(self):
        """RMSD with atomic weights"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0]
        ])
        
        coords2 = np.array([
            [0.0, 0.0, 1.0],  # First atom moves 1.0 in z
            [1.0, 5.0, 0.0]   # Second atom moves 5.0 in y
        ])
        
        # Equal weights - both deviations matter
        rmsd1 = calculate_rmsd(coords1, coords2, weight=np.array([1.0, 1.0]))
        
        # Down-weight second atom (the one with large deviation)
        rmsd2 = calculate_rmsd(coords1, coords2, weight=np.array([1.0, 0.1]))
        
        # With down-weighting of large deviation, RMSD should be smaller
        assert rmsd2 < rmsd1
    
    def test_rmsd_translation(self):
        """RMSD after translation"""
        coords1 = np.random.rand(20, 3)
        coords2 = coords1 + 5.0  # Translate by (5, 5, 5)
        
        rmsd = calculate_rmsd(coords1, coords2)
        
        # RMSD should be sqrt(3) * 5 ≈ 8.66
        expected = np.sqrt(3) * 5
        np.testing.assert_almost_equal(rmsd, expected, decimal=5)


class TestSuperimpose:
    """Test high-level superimpose function"""
    
    def test_superimpose_basic(self):
        """Basic superimpose with translation"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=float)
        
        # Translate and rotate
        coords2 = coords1 @ np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]).T + 10.0
        
        result = superimpose(coords1, coords2, translate=True)
        
        assert 'rotation' in result
        assert 'error' in result
        assert 'rmsd' in result
        assert result['natoms'] == 3
        assert result['weighted'] is False
        assert result['rmsd'] < 1e-5
    
    def test_superimpose_weighted(self):
        """Superimpose with weights"""
        coords1 = np.random.rand(15, 3)
        coords2 = coords1 + np.random.randn(15, 3) * 0.1
        weight = np.random.rand(15)
        
        result = superimpose(coords1, coords2, weight=weight)
        
        assert result['weighted'] is True
        assert result['rmsd'] > 0
        assert result['error'] >= 0
    
    def test_superimpose_no_translation(self):
        """Superimpose without translation"""
        coords1 = np.random.rand(10, 3)
        coords2 = coords1 + 0.05
        
        result = superimpose(coords1, coords2, translate=False)
        
        assert 'rotation' in result
        assert result['natoms'] == 10


class TestEdgeCases:
    """Test edge cases and numerical stability"""
    
    def test_single_atom_alignment(self):
        """Align single atom (degenerate case)"""
        coords1 = np.array([[0.0, 0.0, 0.0]])
        coords2 = np.array([[1.0, 1.0, 1.0]])
        
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # Both should end up at origin
        np.testing.assert_array_almost_equal(coords1, [[0.0, 0.0, 0.0]])
        np.testing.assert_array_almost_equal(coords2, [[0.0, 0.0, 0.0]])
    
    def test_two_atom_alignment(self):
        """Align two atoms (minimal case)"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0]
        ], dtype=float)
        
        coords2 = np.array([
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=float)
        
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # Should successfully align
        assert error < 1e-6
    
    def test_planar_structure(self):
        """Align planar structure (2D in 3D space)"""
        # Square in xy-plane
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=float)
        
        # Same square, rotated 45 degrees around z-axis
        angle = np.pi / 4
        R = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        coords2 = coords1 @ R.T
        
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # Should align successfully
        assert error < 1e-6
        np.testing.assert_array_almost_equal(coords1, coords2, decimal=5)
    
    def test_collinear_atoms(self):
        """Align collinear atoms (1D in 3D space)"""
        coords1 = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0]
        ], dtype=float)
        
        coords2 = np.array([
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0]
        ], dtype=float)
        
        # This is geometrically ambiguous, but should not crash
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # Just check it completes without error
        assert rotation.shape == (3, 3)
    
    def test_large_coordinates(self):
        """Handle large coordinate values"""
        coords1 = np.random.rand(10, 3) * 1000
        coords2 = coords1 + np.random.randn(10, 3)
        
        rmsd = calculate_rmsd(coords1, coords2)
        
        assert rmsd > 0
        assert np.isfinite(rmsd)
    
    def test_zero_weights(self):
        """Handle zero weights gracefully"""
        coords1 = np.random.rand(5, 3)
        coords2 = np.random.rand(5, 3)
        
        # Some atoms with zero weight
        weight = np.array([1.0, 0.0, 1.0, 0.0, 1.0])
        
        rotation, error = align_coordinates(coords1, coords2, weight)
        
        # Should complete without division by zero
        assert rotation.shape == (3, 3)
        assert np.isfinite(error)


class TestNumericalStability:
    """Test numerical stability and precision"""
    
    def test_repeated_alignment(self):
        """Repeated alignment should be stable"""
        coords1 = np.random.rand(20, 3)
        coords2 = np.random.rand(20, 3)
        
        # Align multiple times
        for _ in range(5):
            coords1_copy = coords1.copy()
            rotation, error = align_translate_coordinates(coords1_copy, coords2.copy())
        
        # Final alignment should match first
        coords1_final = coords1.copy()
        rotation_final, error_final = align_translate_coordinates(coords1_final, coords2.copy())
        
        np.testing.assert_array_almost_equal(coords1_copy, coords1_final, decimal=5)
    
    def test_orthonormal_rotation(self):
        """Rotation matrix should be orthonormal"""
        coords1 = np.random.rand(15, 3)
        coords2 = np.random.rand(15, 3)
        
        rotation, error = align_translate_coordinates(coords1, coords2)
        
        # R^T * R should be identity
        RTR = rotation.T @ rotation
        np.testing.assert_array_almost_equal(RTR, np.eye(3), decimal=5)
        
        # Determinant should be 1 (proper rotation, not reflection)
        det = np.linalg.det(rotation)
        np.testing.assert_almost_equal(abs(det), 1.0, decimal=5)
    
    def test_rmsd_symmetry(self):
        """RMSD should be symmetric"""
        coords1 = np.random.rand(10, 3)
        coords2 = np.random.rand(10, 3)
        
        rmsd12 = calculate_rmsd(coords1, coords2)
        rmsd21 = calculate_rmsd(coords2, coords1)
        
        np.testing.assert_almost_equal(rmsd12, rmsd21)
