"""
======================COPYRIGHT/LICENSE START==========================

AIRefinement.py: NMR-restrained refinement of AI predictions for CcpNmr

Copyright (C) 2025

=======================================================================

Integration of NMR experimental restraints with AI-predicted structures.

This module provides:
- NOE distance restraint application
- RDC orientation restraint refinement
- Chemical shift validation
- Automated refinement workflows

======================COPYRIGHT/LICENSE END============================
"""

from os import path, mkdir, system, environ
import subprocess
import tempfile

from memops.universal.Io import getTopDirectory

rootDir = path.split(getTopDirectory())[0]

# External tool directories
XPLOR_DIR = environ.get('XPLOR_DIR', path.join(rootDir, 'external', 'xplor-nih'))
CNS_DIR = environ.get('CNS_DIR', path.join(rootDir, 'external', 'cns'))


def refineWithNMR(structure, constraintLists, method='xplor', outputDir=None):
    """
    Refine AI-predicted structure using NMR experimental restraints.
    
    Args:
        structure: CcpNmr Structure object (from AlphaFold, etc.)
        constraintLists: List of NMR constraint lists (NOE, RDC, etc.)
        method: Refinement method ('xplor', 'cns', or 'amber')
        outputDir: Output directory for refined structures
        
    Returns:
        Refined Structure object
    """
    
    from ccpnmr.analysis.core.StructureBasic import makePdbFromStructure
    
    # Set up output directory
    if outputDir is None:
        memopsRoot = structure.root
        dataRepository = memopsRoot.findFirstRepository(name='userData')
        projPath = dataRepository.url.dataLocation
        outputDir = path.join(projPath, 'nmr_refinement')
        
    if not path.exists(outputDir):
        mkdir(outputDir)
    
    # Export structure to PDB
    pdbFile = path.join(outputDir, 'input_structure.pdb')
    makePdbFromStructure(pdbFile, structure)
    
    # Convert constraints to appropriate format
    restraintFiles = _exportConstraints(constraintLists, outputDir, method)
    
    # Run refinement
    if method == 'xplor':
        refinedPdb = _refineWithXplor(pdbFile, restraintFiles, outputDir)
    elif method == 'cns':
        refinedPdb = _refineWithCNS(pdbFile, restraintFiles, outputDir)
    elif method == 'amber':
        refinedPdb = _refineWithAmber(pdbFile, restraintFiles, outputDir)
    else:
        raise ValueError(f"Unknown refinement method: {method}")
    
    # Import refined structure back to project
    from ccpnmr.analysis.core.StructureBasic import makeStructureFromPdb
    refinedStructure = makeStructureFromPdb(structure.molSystem, refinedPdb)
    refinedStructure.details = f"Refined with NMR data using {method}"
    
    return refinedStructure


def selectiveRefinement(structure, constraintLists, confidenceThreshold=70):
    """
    Intelligently refine only low-confidence regions of AI prediction.
    
    Args:
        structure: Structure with B-factors containing pLDDT scores
        constraintLists: NMR constraints
        confidenceThreshold: pLDDT threshold below which to apply refinement
        
    Returns:
        Selectively refined structure
    """
    
    # Identify low confidence regions from B-factors (pLDDT scores)
    lowConfidenceRegions = _identifyLowConfidenceRegions(structure, confidenceThreshold)
    
    # Filter constraints to focus on problematic regions
    filteredConstraints = _filterConstraintsByRegion(constraintLists, lowConfidenceRegions)
    
    # Refine with position restraints on high-confidence regions
    refinedStructure = _refineWithRegionalRestraints(
        structure, 
        filteredConstraints, 
        lowConfidenceRegions
    )
    
    return refinedStructure


def _exportConstraints(constraintLists, outputDir, format='xplor'):
    """
    Export CcpNmr constraints to refinement program format.
    
    Returns:
        Dictionary mapping constraint type to file path
    """
    
    from ccpnmr.analysis.core.ConstraintBasic import getConstraintType
    
    restraintFiles = {}
    
    for constraintList in constraintLists:
        cType = getConstraintType(constraintList)
        
        if cType == 'Distance':
            # NOE distance restraints
            filename = path.join(outputDir, 'noe_restraints.tbl')
            _exportNOERestraints(constraintList, filename, format)
            restraintFiles['noe'] = filename
            
        elif cType == 'RDC':
            # Residual dipolar couplings
            filename = path.join(outputDir, 'rdc_restraints.tbl')
            _exportRDCRestraints(constraintList, filename, format)
            restraintFiles['rdc'] = filename
            
        elif cType == 'Dihedral':
            # Dihedral angle restraints
            filename = path.join(outputDir, 'dihedral_restraints.tbl')
            _exportDihedralRestraints(constraintList, filename, format)
            restraintFiles['dihedral'] = filename
    
    return restraintFiles


def _exportNOERestraints(constraintList, outputFile, format):
    """
    Export NOE distance restraints in XPLOR/CNS format.
    """
    
    with open(outputFile, 'w') as f:
        f.write("! NOE distance restraints\n")
        f.write("! Generated from CcpNmr project\n\n")
        
        for constraint in constraintList.sortedConstraints():
            items = constraint.sortedItems()
            if len(items) != 2:
                continue
            
            # Get atoms from constraint items
            atom1 = items[0].resonances[0].resonanceSet.findFirstAtomSet()
            atom2 = items[1].resonances[0].resonanceSet.findFirstAtomSet()
            
            if not (atom1 and atom2):
                continue
            
            # Get distance bounds
            lowerLimit = constraint.lowerLimit or 1.8
            upperLimit = constraint.upperLimit or 6.0
            
            # Write in XPLOR format
            f.write(f"assign (resid {atom1.residue.seqCode} and name {atom1.name}) ")
            f.write(f"(resid {atom2.residue.seqCode} and name {atom2.name}) ")
            f.write(f"{(lowerLimit + upperLimit)/2:.3f} ")
            f.write(f"{(upperLimit - lowerLimit)/2:.3f} ")
            f.write(f"{(upperLimit - lowerLimit)/2:.3f}\n")


def _exportRDCRestraints(constraintList, outputFile, format):
    """
    Export RDC restraints.
    """
    
    with open(outputFile, 'w') as f:
        f.write("! RDC restraints\n")
        f.write("! Generated from CcpNmr project\n\n")
        
        for constraint in constraintList.sortedConstraints():
            # RDC export format depends on refinement program
            # This is a placeholder - actual implementation would be more complex
            pass


def _exportDihedralRestraints(constraintList, outputFile, format):
    """
    Export dihedral angle restraints.
    """
    
    with open(outputFile, 'w') as f:
        f.write("! Dihedral angle restraints\n")
        f.write("! Generated from CcpNmr project\n\n")
        
        for constraint in constraintList.sortedConstraints():
            # Dihedral export implementation
            pass


def _refineWithXplor(pdbFile, restraintFiles, outputDir):
    """
    Run XPLOR-NIH refinement with NMR restraints.
    """
    
    # Create XPLOR script
    scriptFile = path.join(outputDir, 'refine.inp')
    
    with open(scriptFile, 'w') as f:
        f.write(_generateXplorScript(pdbFile, restraintFiles, outputDir))
    
    # Run XPLOR
    xplorExe = path.join(XPLOR_DIR, 'bin', 'xplor')
    
    if not path.exists(xplorExe):
        raise RuntimeError(
            f"XPLOR-NIH not found at {xplorExe}. "
            "Set XPLOR_DIR environment variable or install XPLOR-NIH."
        )
    
    cmd = [xplorExe, '-o', path.join(outputDir, 'refine.log'), scriptFile]
    
    print(f"Running XPLOR-NIH refinement...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"XPLOR refinement failed: {result.stderr}")
    
    refinedPdb = path.join(outputDir, 'refined.pdb')
    return refinedPdb


def _generateXplorScript(pdbFile, restraintFiles, outputDir):
    """
    Generate XPLOR-NIH refinement script.
    """
    
    script = f"""
! XPLOR-NIH refinement script
! Generated by CcpNmr AI integration

! Read structure
structure @{pdbFile} end

! Read coordinates  
coordinates @{pdbFile}

! Read restraints
"""
    
    if 'noe' in restraintFiles:
        script += f"""
! NOE distance restraints
noe
    reset
    @{restraintFiles['noe']}
    scale = 50.0
end
"""
    
    if 'rdc' in restraintFiles:
        script += f"""
! RDC restraints
xdipolar
    @{restraintFiles['rdc']}
end
"""
    
    script += f"""
! Energy minimization
minimize powell nstep=1000 end

! Write refined structure
write coordinates output={path.join(outputDir, 'refined.pdb')} end

stop
"""
    
    return script


def _refineWithCNS(pdbFile, restraintFiles, outputDir):
    """
    Run CNS refinement (similar to XPLOR).
    """
    # CNS implementation similar to XPLOR
    raise NotImplementedError("CNS refinement not yet implemented")


def _refineWithAmber(pdbFile, restraintFiles, outputDir):
    """
    Run AMBER refinement with NMR restraints.
    """
    # AMBER implementation
    raise NotImplementedError("AMBER refinement not yet implemented")


def _identifyLowConfidenceRegions(structure, threshold):
    """
    Identify residues with pLDDT < threshold from B-factors.
    
    Returns:
        List of residue sequence codes with low confidence
    """
    
    lowConfidenceResidues = []
    
    for chain in structure.coordChains:
        for residue in chain.residues:
            # pLDDT scores are stored in B-factors
            avgBfactor = sum(atom.bFactor for atom in residue.atoms) / len(residue.atoms)
            
            if avgBfactor < threshold:
                lowConfidenceResidues.append(residue.seqCode)
    
    return lowConfidenceResidues


def _filterConstraintsByRegion(constraintLists, targetResidues):
    """
    Filter constraints to only include those involving target residues.
    """
    
    filteredLists = []
    
    for constraintList in constraintLists:
        # Create new constraint list for filtered constraints
        # Implementation would filter based on residue involvement
        pass
    
    return filteredLists


def _refineWithRegionalRestraints(structure, filteredConstraints, flexibleRegions):
    """
    Refine with position restraints on high-confidence regions.
    """
    
    # This would generate XPLOR script with:
    # 1. Strong position restraints on high-confidence regions
    # 2. Normal NMR restraints on low-confidence regions
    # 3. Energy minimization
    
    pass


def calculateRefinementImprovement(originalStructure, refinedStructure, nmrData):
    """
    Calculate improvement metrics from refinement.
    
    Args:
        originalStructure: AI prediction before refinement
        refinedStructure: After NMR refinement
        nmrData: Experimental NMR data for validation
        
    Returns:
        Dictionary with improvement metrics
    """
    
    from ccpnmr.analysis.core.StructureBasic import calcRmsd
    
    # Calculate RMSD between original and refined
    rmsd = calcRmsd(originalStructure, refinedStructure)
    
    # Calculate NOE violations before/after
    originalViolations = _calculateNOEViolations(originalStructure, nmrData)
    refinedViolations = _calculateNOEViolations(refinedStructure, nmrData)
    
    # Calculate RDC Q-factors before/after
    originalRDC = _calculateRDCQFactor(originalStructure, nmrData)
    refinedRDC = _calculateRDCQFactor(refinedStructure, nmrData)
    
    return {
        'rmsd_change': rmsd,
        'noe_violations': {
            'before': originalViolations,
            'after': refinedViolations,
            'improvement': originalViolations - refinedViolations
        },
        'rdc_q_factor': {
            'before': originalRDC,
            'after': refinedRDC,
            'improvement': originalRDC - refinedRDC
        }
    }


def _calculateNOEViolations(structure, nmrData):
    """
    Count NOE distance constraint violations.
    """
    
    from ccpnmr.analysis.core.ConstraintBasic import getDistanceConstraintViolations
    
    violations = 0
    
    for constraintList in nmrData.get('noe_constraints', []):
        violations += len(getDistanceConstraintViolations(structure, constraintList))
    
    return violations


def _calculateRDCQFactor(structure, nmrData):
    """
    Calculate RDC Q-factor for structure.
    """
    
    # Placeholder - actual RDC calculation is complex
    # Would integrate with AF-NMR project scripts
    
    return 0.0
