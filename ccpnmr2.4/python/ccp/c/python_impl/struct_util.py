"""
Pure Python implementation of structural alignment and coordinate manipulation.

This module provides functions for aligning molecular structures, translating
coordinates to center of mass, and calculating RMSD for ensembles. Uses SVD-based
Kabsch algorithm for optimal structural superposition.

Based on structural bioinformatics algorithms.

Original C code: ccpnmr2.4/c/ccp/structure/struct_util.c
"""

import numpy as np
from typing import List, Tuple, Optional
from scipy.linalg import eigh


COORD_NDIMS = 3
RMSD_THRESHOLD = 0.8


def translate_coordinates(coords: np.ndarray, weight: Optional[np.ndarray] = None) -> None:
    """
    Translate coordinates to center of mass.
    
    Modifies coords in-place to center them at the origin, optionally
    using atomic weights for the center of mass calculation.
    
    Args:
        coords: Coordinate array of shape (natoms, 3)
        weight: Optional weight array of shape (natoms,). If None, all atoms
                have equal weight.
    
    Example:
        >>> coords = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        >>> translate_coordinates(coords)
        >>> # coords now centered at origin
    """
    natoms = coords.shape[0]
    
    if weight is None:
        # Equal weights
        center = np.mean(coords, axis=0)
    else:
        # Weighted center of mass
        total_weight = np.sum(weight)
        center = np.sum(coords * weight[:, np.newaxis], axis=0) / total_weight
    
    # Translate to center
    coords -= center


def align_translate_coordinates(coords1: np.ndarray, coords2: np.ndarray,
                                weight: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
    """
    Align coords1 to coords2 after translating both to center of mass.
    
    First translates both coordinate sets to their respective centers of mass,
    then computes the optimal rotation matrix to align coords1 onto coords2.
    Modifies coords1 in-place.
    
    Args:
        coords1: Coordinate array to be aligned, shape (natoms, 3).
                 Modified in-place.
        coords2: Reference coordinate array, shape (natoms, 3).
                 Modified in-place (translated to center).
        weight: Optional weight array, shape (natoms,)
    
    Returns:
        tuple: (rotation_matrix, error) where:
            - rotation_matrix: 3x3 rotation matrix applied to coords1
            - error: Weighted squared error between aligned structures
    
    Example:
        >>> coords1 = np.random.rand(10, 3)
        >>> coords2 = np.random.rand(10, 3)
        >>> rotation, error = align_translate_coordinates(coords1, coords2)
        >>> print(f"Alignment error: {error:.4f}")
    """
    # Translate both to center of mass
    translate_coordinates(coords1, weight)
    translate_coordinates(coords2, weight)
    
    return align_coordinates(coords1, coords2, weight)


def align_coordinates(coords1: np.ndarray, coords2: np.ndarray,
                     weight: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
    """
    Align coords1 to coords2 using Kabsch algorithm.
    
    Computes the optimal rotation matrix to align coords1 onto coords2 without
    translation. Uses SVD-based Kabsch algorithm. Modifies coords1 in-place.
    
    The Kabsch algorithm finds the optimal rotation matrix by:
    1. Computing the cross-covariance matrix R = coords2^T * W * coords1
    2. Computing SVD of R^T * R
    3. Constructing rotation from eigenvectors
    
    Args:
        coords1: Coordinate array to be aligned, shape (natoms, 3).
                 Modified in-place.
        coords2: Reference coordinate array, shape (natoms, 3)
        weight: Optional weight array, shape (natoms,). If None, all atoms
                have equal weight.
    
    Returns:
        tuple: (rotation_matrix, error) where:
            - rotation_matrix: 3x3 rotation matrix
            - error: Weighted squared error after alignment
    
    Raises:
        ValueError: If eigenvalue decomposition fails
    
    Reference:
        Kabsch, W. (1976). "A solution for the best rotation to relate
        two sets of vectors". Acta Crystallographica A32: 922-923.
    
    Example:
        >>> # Align two protein conformations
        >>> coords1 = backbone_coords_conf1  # shape (100, 3)
        >>> coords2 = backbone_coords_conf2  # shape (100, 3)
        >>> weight = np.ones(100)  # Equal weights
        >>> rotation, rmsd = align_coordinates(coords1, coords2, weight)
        >>> print(f"RMSD: {np.sqrt(rmsd):.3f} Å")
    """
    natoms = coords1.shape[0]
    
    # Set up weights
    if weight is None:
        w = np.ones(natoms)
    else:
        w = weight
    
    # Calculate initial error (before alignment)
    error = 0.5 * (
        np.sum(w * np.sum(coords1**2, axis=1)) +
        np.sum(w * np.sum(coords2**2, axis=1))
    )
    
    # Calculate rotation matrix R = coords2^T * W * coords1
    # R[i,j] = sum_k( w_k * coords2[k,i] * coords1[k,j] )
    rotation = np.zeros((COORD_NDIMS, COORD_NDIMS))
    for i in range(COORD_NDIMS):
        for j in range(COORD_NDIMS):
            rotation[i, j] = np.sum(w * coords2[:, i] * coords1[:, j])
    
    # Calculate R^T * R
    RtR = rotation.T @ rotation
    
    # Compute eigenvalues and eigenvectors of R^T * R
    try:
        eigenvalues, eigenvectors = eigh(RtR)
    except np.linalg.LinAlgError as e:
        raise ValueError(f"Eigenvalue decomposition failed: {e}")
    
    # Sort eigenvalues in decreasing order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Transpose eigenvectors (column vectors -> row vectors)
    eigenvectors = eigenvectors.T
    
    # Extract eigenvector components
    e0 = eigenvectors[0]
    e1 = eigenvectors[1]
    e2 = np.cross(e0, e1)  # Ensure right-handed coordinate system
    
    # Calculate b vectors: b_i = R * e_i / sqrt(lambda_i)
    v0 = rotation @ e0
    v1 = rotation @ e1
    v2 = rotation @ e2
    
    s0 = np.sqrt(max(eigenvalues[0], 0))
    s1 = np.sqrt(max(eigenvalues[1], 0))
    s2 = np.sqrt(max(eigenvalues[2], 0))
    
    # Avoid division by zero
    if s0 > 1e-10:
        b0 = v0 / s0
    else:
        b0 = np.zeros(COORD_NDIMS)
    
    if s1 > 1e-10:
        b1 = v1 / s1
    else:
        b1 = np.zeros(COORD_NDIMS)
    
    b2 = np.cross(b0, b1)
    
    # Construct rotation matrix
    rotation = np.zeros((COORD_NDIMS, COORD_NDIMS))
    for i in range(COORD_NDIMS):
        for j in range(COORD_NDIMS):
            rotation[i, j] = b0[i]*e0[j] + b1[i]*e1[j] + b2[i]*e2[j]
    
    # Determine sign
    if np.dot(b2, v2) < 0:
        s = -1
    else:
        s = 1
    
    # Calculate final error
    final_error = error - (s0 + s1 + s * s2)
    
    # Apply rotation to coords1 (in-place)
    coords1[:] = coords1 @ rotation.T
    
    return rotation, final_error


def align_ensemble(coords: np.ndarray, weight: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Align an ensemble of coordinate sets.
    
    Performs iterative structural alignment of multiple conformations:
    1. Translates all structures to center of mass
    2. Initial alignment to first structure
    3. Calculates per-atom and per-ensemble RMSD
    4. Identifies structure closest to mean
    5. Re-weights atoms based on RMSD (down-weight mobile atoms)
    6. Final alignment to best structure
    
    This iterative procedure with RMSD-based weighting provides robust
    alignment even when structures have mobile loops or poorly defined regions.
    
    Args:
        coords: Coordinate array of shape (nensembles, natoms, 3).
                Modified in-place during alignment.
        weight: Weight array of shape (natoms,). Modified in-place to
                include RMSD-based weighting.
    
    Returns:
        tuple: (atom_rmsd, ensemble_rmsd, total_error) where:
            - atom_rmsd: Per-atom RMSD array, shape (natoms,)
            - ensemble_rmsd: Per-ensemble RMSD array, shape (nensembles,)
            - total_error: Total alignment error across ensemble
    
    Example:
        >>> # Align NMR ensemble of 20 structures
        >>> coords = load_nmr_ensemble()
        # shape (20, 150, 3)
        >>> weight = np.ones(150)  # Equal initial weights
        >>> atom_rmsd, ens_rmsd, err = align_ensemble(coords, weight)
        >>> print(f"Average per-atom RMSD: {np.mean(atom_rmsd):.3f} Å")
        >>> print(f"Most ordered residues: {np.argsort(atom_rmsd)[:5]}")
    """
    nensembles, natoms, _ = coords.shape
    
    # Translate all coordinates to center of mass
    for i in range(nensembles):
        translate_coordinates(coords[i], weight)
    
    # Allocate rotation matrix
    rotation = np.zeros((COORD_NDIMS, COORD_NDIMS))
    
    # Initial alignment: fit all structures to first ensemble member
    for i in range(1, nensembles):
        rotation, err = align_coordinates(coords[i], coords[0], weight)
    
    # Calculate atom_rmsd and ensemble_rmsd
    atom_rmsd, ensemble_rmsd = _calculate_rmsds(coords, weight)
    
    # Determine ensemble member closest to mean
    best_ensemble = np.argmin(ensemble_rmsd)
    
    # Adjust weights based on RMSD (down-weight highly mobile atoms)
    t = atom_rmsd / RMSD_THRESHOLD
    weight *= np.exp(-t * t)
    
    # Final alignment: fit all structures to best ensemble member
    total_error = 0.0
    for i in range(nensembles):
        if i != best_ensemble:
            rotation, err = align_coordinates(coords[i], coords[best_ensemble], weight)
            total_error += err
    
    # Recalculate RMSDs with final alignment
    atom_rmsd, ensemble_rmsd = _calculate_rmsds(coords, weight)
    
    return atom_rmsd, ensemble_rmsd, total_error


def _calculate_rmsds(coords: np.ndarray, weight: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate per-atom and per-ensemble RMSDs.
    
    Helper function for align_ensemble. Computes RMSD of each atom across
    all ensemble members and RMSD of each ensemble member from the mean.
    
    Args:
        coords: Coordinate array, shape (nensembles, natoms, 3)
        weight: Weight array, shape (natoms,)
    
    Returns:
        tuple: (atom_rmsd, ensemble_rmsd)
            - atom_rmsd: shape (natoms,) - RMSD per atom across ensemble
            - ensemble_rmsd: shape (nensembles,) - RMSD per structure from mean
    """
    nensembles, natoms, _ = coords.shape
    
    # Calculate mean coordinates across ensemble
    mean_coords = np.mean(coords, axis=0)  # shape (natoms, 3)
    
    # Calculate per-atom RMSD
    atom_rmsd = np.zeros(natoms)
    for i in range(natoms):
        # Sum of squared deviations from mean for this atom
        deviations = coords[:, i, :] - mean_coords[i, :]
        sq_dev = np.sum(deviations**2)
        atom_rmsd[i] = np.sqrt(sq_dev / nensembles)
    
    # Calculate per-ensemble RMSD (weighted)
    ensemble_rmsd = np.zeros(nensembles)
    total_weight = np.sum(weight)
    
    for j in range(nensembles):
        # Weighted squared deviation from mean
        deviations = coords[j] - mean_coords
        sq_dev = np.sum(deviations**2, axis=1)  # Per-atom squared deviations
        weighted_sq_dev = np.sum(weight * sq_dev)
        ensemble_rmsd[j] = np.sqrt(weighted_sq_dev / total_weight)
    
    return atom_rmsd, ensemble_rmsd


def calculate_rmsd(coords1: np.ndarray, coords2: np.ndarray,
                  weight: Optional[np.ndarray] = None) -> float:
    """
    Calculate RMSD between two coordinate sets.
    
    Convenience function to compute root-mean-square deviation between
    two structures without performing alignment.
    
    Args:
        coords1: First coordinate array, shape (natoms, 3)
        coords2: Second coordinate array, shape (natoms, 3)
        weight: Optional weight array, shape (natoms,)
    
    Returns:
        RMSD value in same units as coordinates (typically Ångströms)
    
    Example:
        >>> rmsd = calculate_rmsd(model1_coords, xray_coords)
        >>> print(f"Model vs X-ray RMSD: {rmsd:.2f} Å")
    """
    natoms = coords1.shape[0]
    
    if weight is None:
        w = np.ones(natoms)
        total_weight = natoms
    else:
        w = weight
        total_weight = np.sum(w)
    
    # Calculate weighted squared deviations
    diff = coords1 - coords2
    sq_dev = np.sum(diff**2, axis=1)
    weighted_sq_dev = np.sum(w * sq_dev)
    
    return np.sqrt(weighted_sq_dev / total_weight)


def superimpose(coords1: np.ndarray, coords2: np.ndarray,
               weight: Optional[np.ndarray] = None,
               translate: bool = True) -> dict:
    """
    Superimpose coords1 onto coords2 and return alignment statistics.
    
    High-level function that performs structural alignment and returns
    comprehensive statistics about the superposition quality.
    
    Args:
        coords1: Coordinate array to align, shape (natoms, 3).
                 Modified in-place.
        coords2: Reference coordinates, shape (natoms, 3).
                 Modified in-place if translate=True.
        weight: Optional weight array, shape (natoms,)
        translate: Whether to translate to center of mass first
    
    Returns:
        dict: {
            'rotation': 3x3 rotation matrix,
            'error': Alignment error,
            'rmsd': Root-mean-square deviation,
            'natoms': Number of atoms,
            'weighted': Whether weights were used
        }
    
    Example:
        >>> result = superimpose(mobile, reference, weight=ca_atoms)
        >>> print(f"C-alpha RMSD: {result['rmsd']:.2f} Å")
        >>> print(f"Rotation applied:\\n{result['rotation']}")
    """
    natoms = coords1.shape[0]
    
    if translate:
        rotation, error = align_translate_coordinates(coords1, coords2, weight)
    else:
        rotation, error = align_coordinates(coords1, coords2, weight)
    
    rmsd = calculate_rmsd(coords1, coords2, weight)
    
    return {
        'rotation': rotation,
        'error': error,
        'rmsd': rmsd,
        'natoms': natoms,
        'weighted': weight is not None
    }
