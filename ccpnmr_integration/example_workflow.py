#!/usr/bin/env python
"""
example_workflow.py

Demonstration of CcpNmr AI integration workflow.

This script shows how to:
1. Load a CcpNmr project
2. Run AlphaFold prediction
3. Refine with NMR data
4. Compare and validate results

Usage:
    python example_workflow.py --project /path/to/ccpnmr/project
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Demonstrate CcpNmr AI integration workflow'
    )
    parser.add_argument(
        '--project',
        help='Path to CcpNmr project directory'
    )
    parser.add_argument(
        '--chain',
        default='A',
        help='Chain ID to predict (default: A)'
    )
    parser.add_argument(
        '--skip-prediction',
        action='store_true',
        help='Skip prediction step (use existing structure)'
    )
    parser.add_argument(
        '--skip-refinement',
        action='store_true',
        help='Skip refinement step'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CcpNmr AI Integration - Example Workflow")
    print("=" * 70)
    print()
    
    # Step 1: Import CcpNmr modules
    print("[1/5] Importing CcpNmr modules...")
    try:
        from ccpnmr.analysis.wrappers.AlphaFold import runAlphaFold, compareWithNMR
        from ccpnmr.analysis.wrappers.AIRefinement import refineWithNMR, calculateRefinementImprovement
        print("    ✓ Imports successful\n")
    except ImportError as e:
        print(f"    ✗ Import failed: {e}")
        print("    → Make sure CcpNmr is in PYTHONPATH")
        print("    → Run: export PYTHONPATH=~/nmr/ccpnmr2.4/ccpnmr2.4/python:$PYTHONPATH")
        sys.exit(1)
    
    # Step 2: Load project (or create demo)
    print("[2/5] Loading CcpNmr project...")
    if args.project:
        project = load_project(args.project)
        print(f"    ✓ Loaded project: {args.project}\n")
    else:
        print("    ⓘ No project specified, using demo data")
        project = create_demo_project()
        print(f"    ✓ Created demo project\n")
    
    # Get chain
    chain = get_chain(project, args.chain)
    print(f"    → Working with chain: {chain.code}")
    print(f"    → Sequence: {get_sequence(chain)[:50]}...\n")
    
    # Step 3: Run AI prediction
    if not args.skip_prediction:
        print("[3/5] Running AI structure prediction...")
        print("    → Using ESMFold (fast, no MSA required)")
        try:
            aiStructure = runAlphaFold(chain, useCachedModel=True)
            print(f"    ✓ Prediction complete")
            print(f"    → Structure: {aiStructure}")
            print(f"    → Average confidence: {get_avg_confidence(aiStructure):.1f}\n")
        except Exception as e:
            print(f"    ✗ Prediction failed: {e}")
            print(f"    → Try: pip install fair-esm torch")
            sys.exit(1)
    else:
        print("[3/5] Skipping prediction (--skip-prediction)")
        aiStructure = project.structures[0]  # Use existing
        print(f"    → Using existing structure: {aiStructure}\n")
    
    # Step 4: Refine with NMR data (if available)
    if not args.skip_refinement:
        print("[4/5] Refining with NMR data...")
        
        constraintLists = get_nmr_constraints(project)
        
        if constraintLists:
            print(f"    → Found {len(constraintLists)} constraint lists")
            try:
                refinedStructure = refineWithNMR(
                    aiStructure,
                    constraintLists,
                    method='xplor'
                )
                print(f"    ✓ Refinement complete")
                print(f"    → Refined structure: {refinedStructure}\n")
                
                # Calculate improvement
                improvement = calculateRefinementImprovement(
                    aiStructure,
                    refinedStructure,
                    {'noe_constraints': constraintLists}
                )
                print(f"    → Improvement metrics:")
                print(f"       RMSD change: {improvement['rmsd_change']:.2f} Å")
                print(f"       NOE violations: {improvement['noe_violations']['before']} → {improvement['noe_violations']['after']}")
                
            except Exception as e:
                print(f"    ⚠ Refinement failed: {e}")
                print(f"    → Continuing with unrefined structure")
                refinedStructure = aiStructure
        else:
            print(f"    ⓘ No NMR constraints found, skipping refinement")
            refinedStructure = aiStructure
        print()
    else:
        print("[4/5] Skipping refinement (--skip-refinement)\n")
        refinedStructure = aiStructure
    
    # Step 5: Comparison and validation
    print("[5/5] Validation and comparison...")
    
    # Compare with experimental structure if available
    nmrStructure = find_nmr_structure(project)
    
    if nmrStructure:
        print(f"    → Found experimental NMR structure")
        comparison = compareWithNMR(refinedStructure, nmrStructure)
        print(f"    → Global RMSD: {comparison['global_rmsd']:.2f} Å")
        
        if comparison['high_disagreement_regions']:
            print(f"    → High disagreement regions:")
            for resNum, rmsd in comparison['high_disagreement_regions'][:5]:
                print(f"       Residue {resNum}: {rmsd:.2f} Å")
    else:
        print(f"    ⓘ No experimental structure for comparison")
    
    # Generate report
    print(f"\n    ✓ Workflow complete!")
    print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Chain: {chain.code}")
    print(f"AI Structure: {aiStructure}")
    if refinedStructure != aiStructure:
        print(f"Refined Structure: {refinedStructure}")
    if nmrStructure:
        print(f"Experimental Structure: {nmrStructure}")
        print(f"AI vs NMR RMSD: {comparison['global_rmsd']:.2f} Å")
    print("=" * 70)


def load_project(project_path):
    """Load CcpNmr project."""
    from ccp.gui.Io import loadProject
    return loadProject(project_path)


def create_demo_project():
    """Create a demo project for testing."""
    print("    → Creating demo project with test sequence")
    
    # This would create a minimal CcpNmr project
    # For actual implementation, would use CcpNmr API
    
    class DemoProject:
        def __init__(self):
            self.structures = []
    
    class DemoChain:
        def __init__(self):
            self.code = 'A'
            self.residues = []
    
    project = DemoProject()
    return project


def get_chain(project, chain_id):
    """Get chain from project."""
    for chain in project.currentNmrProject.sortedChains():
        if chain.code == chain_id:
            return chain
    
    # Fallback: return first chain
    return project.currentNmrProject.sortedChains()[0]


def get_sequence(chain):
    """Extract sequence from chain."""
    from ccpnmr.analysis.core.MoleculeBasic import getResidueCode
    return ''.join([getResidueCode(res) for res in chain.sortedResidues()])


def get_avg_confidence(structure):
    """Calculate average pLDDT from structure B-factors."""
    total = 0
    count = 0
    
    for chain in structure.coordChains:
        for residue in chain.residues:
            for atom in residue.atoms:
                total += atom.bFactor
                count += 1
    
    return total / count if count > 0 else 0.0


def get_nmr_constraints(project):
    """Get NMR constraint lists from project."""
    constraints = []
    
    if hasattr(project, 'currentNmrProject'):
        for store in project.currentNmrProject.nmrConstraintStores:
            constraints.extend(store.constraintLists)
    
    return constraints


def find_nmr_structure(project):
    """Find experimental NMR structure in project."""
    for structure in project.structures:
        if 'NMR' in structure.details or 'experimental' in structure.details.lower():
            return structure
    return None


if __name__ == '__main__':
    main()
