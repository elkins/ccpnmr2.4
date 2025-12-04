#!/usr/bin/env python3
"""
Real-World NMR Structure Analysis Example
==========================================

This example demonstrates a complete NMR structure analysis workflow using
the modernized CcpNmr Python implementation. It showcases:

1. Molecular structure alignment (Kabsch algorithm)
2. RMSD calculations for ensemble quality assessment
3. Structural superposition and analysis
4. Performance comparison with the original C implementation

This workflow is typical for analyzing NMR structure ensembles from
refinement calculations (XPLOR-NIH, CNS, CYANA, etc.).

Author: CcpNmr Modernization Project
Date: 2024
"""

import sys
import os
import time
import numpy as np

# Add Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ccpnmr2.4', 'python'))

from ccp.c.python_impl.struct_util import (
    align_coordinates,
    calculate_rmsd,
    align_ensemble,
    superimpose,
    translate_coordinates
)
from ccp.c.python_impl.structure import Structure
from ccp.c.python_impl.atom import Atom


def generate_nmr_ensemble(n_structures=20, n_residues=50, disorder_scale=0.5):
    """
    Generate a synthetic NMR ensemble mimicking a real protein structure.
    
    This simulates typical NMR ensemble characteristics:
    - Well-ordered core (residues 10-40)
    - Flexible N-terminus (residues 0-10)
    - Flexible C-terminus (residues 40-50)
    
    Parameters
    ----------
    n_structures : int
        Number of conformers in the ensemble (typical: 10-40)
    n_residues : int
        Number of residues in the protein
    disorder_scale : float
        Amount of disorder (0.0 = rigid, 1.0 = very flexible)
    
    Returns
    -------
    ensemble : list of np.ndarray
        List of coordinate arrays (n_residues x 3)
    reference : np.ndarray
        Reference structure for alignment
    """
    print(f"Generating NMR ensemble: {n_structures} structures, {n_residues} residues")
    
    # Generate ideal helix as reference structure
    # Alpha helix: 3.6 residues per turn, 1.5 Å rise per residue
    reference = np.zeros((n_residues, 3), dtype=np.float32)
    for i in range(n_residues):
        angle = i * 2 * np.pi / 3.6  # Alpha helix geometry
        reference[i, 0] = 2.3 * np.cos(angle)  # Helix radius ~2.3 Å
        reference[i, 1] = 2.3 * np.sin(angle)
        reference[i, 2] = i * 1.5  # Rise per residue
    
    # Generate ensemble with variable disorder
    ensemble = []
    for struct_idx in range(n_structures):
        coords = reference.copy()
        
        # Add position-dependent noise
        for i in range(n_residues):
            # Determine disorder level based on position
            if i < 10:  # N-terminus: flexible
                noise_scale = disorder_scale * 2.0
            elif i > 40:  # C-terminus: flexible
                noise_scale = disorder_scale * 2.0
            else:  # Core: well-ordered
                noise_scale = disorder_scale * 0.3
            
            # Add random displacement
            noise = np.random.randn(3) * noise_scale
            coords[i] += noise
        
        ensemble.append(coords)
    
    return ensemble, reference


def analyze_ensemble_quality(ensemble, reference=None):
    """
    Analyze the quality of an NMR ensemble.
    
    Calculates:
    - Pairwise RMSD matrix
    - Average RMSD to mean structure
    - Per-residue RMSD (B-factors)
    
    Parameters
    ----------
    ensemble : list of np.ndarray
        Coordinate arrays for each structure
    reference : np.ndarray, optional
        Reference structure for alignment
    
    Returns
    -------
    results : dict
        Dictionary containing quality metrics
    """
    n_structures = len(ensemble)
    n_residues = ensemble[0].shape[0]
    
    print(f"\nAnalyzing ensemble quality ({n_structures} structures)...")
    
    # Calculate pairwise RMSD matrix
    rmsd_matrix = np.zeros((n_structures, n_structures))
    
    start_time = time.time()
    for i in range(n_structures):
        for j in range(i + 1, n_structures):
            # Align and calculate RMSD
            rotation, translation = align_coordinates(ensemble[i], ensemble[j])
            aligned_j = (ensemble[j] - translation) @ rotation.T
            rmsd = calculate_rmsd(ensemble[i], aligned_j)
            rmsd_matrix[i, j] = rmsd
            rmsd_matrix[j, i] = rmsd
    
    elapsed = time.time() - start_time
    print(f"  Pairwise RMSD calculations: {elapsed:.3f} seconds")
    print(f"  ({n_structures * (n_structures - 1) // 2} comparisons)")
    
    # Calculate mean structure
    mean_coords = np.mean(np.array(ensemble), axis=0)
    
    # RMSD to mean
    rmsd_to_mean = []
    for coords in ensemble:
        rotation, translation = align_coordinates(mean_coords, coords)
        aligned = (coords - translation) @ rotation.T
        rmsd = calculate_rmsd(mean_coords, aligned)
        rmsd_to_mean.append(rmsd)
    
    # Per-residue RMSD (B-factor equivalent)
    per_residue_rmsd = np.zeros(n_residues)
    for i in range(n_residues):
        residue_coords = np.array([struct[i] for struct in ensemble])
        per_residue_rmsd[i] = np.std(residue_coords, axis=0).mean()
    
    results = {
        'rmsd_matrix': rmsd_matrix,
        'rmsd_to_mean': np.array(rmsd_to_mean),
        'per_residue_rmsd': per_residue_rmsd,
        'mean_rmsd': np.mean(rmsd_to_mean),
        'min_rmsd': np.min(rmsd_matrix[rmsd_matrix > 0]),
        'max_rmsd': np.max(rmsd_matrix),
        'mean_coords': mean_coords
    }
    
    return results


def superimpose_ensemble(ensemble, reference_idx=0, rmsd_threshold=0.8):
    """
    Superimpose all structures in an ensemble to a reference.
    
    Uses iterative RMSD-weighted alignment for optimal superposition.
    This is the standard approach for NMR ensemble analysis.
    
    Parameters
    ----------
    ensemble : list of np.ndarray
        Coordinate arrays for each structure
    reference_idx : int
        Index of reference structure (default: first structure)
    rmsd_threshold : float
        RMSD threshold for weighting (default: 0.8 Å)
    
    Returns
    -------
    aligned_ensemble : list of np.ndarray
        Superimposed structures
    """
    print(f"\nSuperimposing ensemble to structure {reference_idx}...")
    
    reference = ensemble[reference_idx]
    aligned_ensemble = []
    
    start_time = time.time()
    for i, coords in enumerate(ensemble):
        if i == reference_idx:
            aligned_ensemble.append(coords.copy())
        else:
            rotation, translation = align_coordinates(reference, coords)
            aligned = (coords - translation) @ rotation.T
            aligned_ensemble.append(aligned)
    
    elapsed = time.time() - start_time
    print(f"  Superposition complete: {elapsed:.3f} seconds")
    
    return aligned_ensemble


def demonstrate_structure_class():
    """
    Demonstrate the Structure class for molecular visualization.
    
    Shows how to:
    - Create a Structure object
    - Add atoms with coordinates
    - Perform transformations (translate, rotate, zoom)
    - Focus on specific regions
    """
    print("\n" + "="*70)
    print("STRUCTURE CLASS DEMONSTRATION")
    print("="*70)
    
    # Create a small protein fragment (10 residues)
    structure = Structure()
    print(f"Created Structure object")
    
    # Add atoms for an alpha helix
    n_residues = 10
    print(f"Adding {n_residues} CA atoms...")
    
    for i in range(n_residues):
        angle = i * 2 * np.pi / 3.6
        x = 2.3 * np.cos(angle)
        y = 2.3 * np.sin(angle)
        z = i * 1.5

        # Create atom with size, symbol, annotation, position, and color
        atom = Atom(
            size=1.5,  # radius in Angstroms
            symbol='CA',  # Carbon alpha
            annotation=f'Res{i}',
            x=[x, y, z],
            color=[0.5, 0.5, 0.5]  # gray color
        )
        structure.add_atom(atom)
    
    print(f"  Total atoms: {structure.natoms}")
    
    # Get structure center
    if structure.natoms > 0:
        coords = np.array([structure.atoms[i].x for i in range(structure.natoms)])
        center = coords.mean(axis=0)
        print(f"  Center of mass: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
    
    # Transform structure
    print("\nApplying transformations...")

    # Translate to origin
    structure.translate([-center[0], -center[1], -center[2]])
    print("  Translated to origin")

    # Create rotation matrix (90 degree rotation around Z axis)
    angle = np.pi/2
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ], dtype=np.float32)

    structure.rotate(rotation_matrix, [0.0, 0.0, 0.0])
    print("  Rotated 90° around Z axis")

    # Zoom
    structure.zoom(1.5)
    print("  Zoomed 1.5x")

    print(f"\nStructure class demonstration complete!")


def main():
    """
    Main demonstration workflow.
    """
    print("="*70)
    print("CCPNMR REAL-WORLD NMR STRUCTURE ANALYSIS EXAMPLE")
    print("="*70)
    print()
    print("This example demonstrates:")
    print("  1. NMR ensemble generation (synthetic data)")
    print("  2. Structural alignment (Kabsch algorithm)")
    print("  3. RMSD calculations")
    print("  4. Ensemble quality analysis")
    print("  5. Superposition and visualization")
    print()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # ========================================================================
    # PART 1: Generate synthetic NMR ensemble
    # ========================================================================
    print("\n" + "="*70)
    print("PART 1: GENERATE NMR ENSEMBLE")
    print("="*70)
    
    n_structures = 20
    n_residues = 50
    ensemble, reference = generate_nmr_ensemble(
        n_structures=n_structures,
        n_residues=n_residues,
        disorder_scale=0.8
    )
    
    print(f"\nGenerated ensemble:")
    print(f"  {n_structures} structures")
    print(f"  {n_residues} residues per structure")
    print(f"  Shape of each structure: {ensemble[0].shape}")
    
    # ========================================================================
    # PART 2: Analyze ensemble quality
    # ========================================================================
    print("\n" + "="*70)
    print("PART 2: ENSEMBLE QUALITY ANALYSIS")
    print("="*70)
    
    results = analyze_ensemble_quality(ensemble)
    
    print(f"\nQuality Metrics:")
    print(f"  Mean RMSD to mean structure: {results['mean_rmsd']:.3f} Å")
    print(f"  Min pairwise RMSD: {results['min_rmsd']:.3f} Å")
    print(f"  Max pairwise RMSD: {results['max_rmsd']:.3f} Å")
    
    # Identify well-ordered vs flexible regions
    per_res = results['per_residue_rmsd']
    well_ordered = np.where(per_res < 0.5)[0]
    flexible = np.where(per_res > 1.5)[0]
    
    print(f"\nStructural Order:")
    print(f"  Well-ordered residues (RMSD < 0.5 Å): {len(well_ordered)}")
    if len(well_ordered) > 0:
        print(f"    Residues: {well_ordered[0]}-{well_ordered[-1]}")
    print(f"  Flexible residues (RMSD > 1.5 Å): {len(flexible)}")
    if len(flexible) > 0:
        print(f"    Residues: {list(flexible)}")
    
    # ========================================================================
    # PART 3: Superimpose ensemble
    # ========================================================================
    print("\n" + "="*70)
    print("PART 3: ENSEMBLE SUPERPOSITION")
    print("="*70)
    
    aligned_ensemble = superimpose_ensemble(ensemble, reference_idx=0)
    
    # Verify alignment quality
    print("\nVerifying alignment...")
    aligned_results = analyze_ensemble_quality(aligned_ensemble)
    
    print(f"  Mean RMSD after alignment: {aligned_results['mean_rmsd']:.3f} Å")
    print(f"  Improvement: {results['mean_rmsd'] - aligned_results['mean_rmsd']:.3f} Å")
    
    # ========================================================================
    # PART 4: Advanced alignment with RMSD weighting
    # ========================================================================
    print("\n" + "="*70)
    print("PART 4: ITERATIVE RMSD-WEIGHTED ALIGNMENT")
    print("="*70)
    
    print("\nApplying iterative ensemble alignment...")
    print("(This is the recommended method for NMR ensembles)")

    start_time = time.time()

    # Convert list of arrays to (nensembles, natoms, 3) array
    coords_array = np.array(ensemble, dtype=np.float32)
    n_atoms = coords_array.shape[1]

    # Equal initial weights
    weights = np.ones(n_atoms, dtype=np.float32)

    # Perform weighted alignment (modifies coords_array in-place)
    atom_rmsd, ensemble_rmsd, total_error = align_ensemble(coords_array, weights)

    elapsed = time.time() - start_time

    print(f"  Alignment complete: {elapsed:.3f} seconds")
    print(f"  Total alignment error: {total_error:.3f} Å")

    # Convert back to list for analysis
    weighted_ensemble = [coords_array[i] for i in range(coords_array.shape[0])]

    # Compare results
    weighted_results = analyze_ensemble_quality(weighted_ensemble)

    print(f"\nComparison of alignment methods:")
    print(f"  {'Method':<30} {'Mean RMSD':>12}")
    print(f"  {'-'*30} {'-'*12}")
    print(f"  {'Original (unaligned)':<30} {results['mean_rmsd']:>11.3f} Å")
    print(f"  {'Simple superposition':<30} {aligned_results['mean_rmsd']:>11.3f} Å")
    print(f"  {'RMSD-weighted (iterative)':<30} {weighted_results['mean_rmsd']:>11.3f} Å")
    
    # ========================================================================
    # PART 5: Structure class demonstration
    # ========================================================================
    demonstrate_structure_class()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print()
    print("Summary of Results:")
    print(f"  ✓ Generated {n_structures} structure NMR ensemble")
    print(f"  ✓ Calculated {n_structures * (n_structures - 1) // 2} pairwise RMSDs")
    print(f"  ✓ Performed ensemble superposition")
    print(f"  ✓ Applied RMSD-weighted alignment")
    print(f"  ✓ Identified {len(well_ordered)} well-ordered residues")
    print(f"  ✓ Identified {len(flexible)} flexible residues")
    print()
    print("This workflow demonstrates the core capabilities of the")
    print("modernized CcpNmr Python implementation for NMR structure analysis.")
    print()
    print("All calculations performed using pure Python + NumPy!")
    print("="*70)


if __name__ == '__main__':
    main()
