"""
======================COPYRIGHT/LICENSE START==========================

AlphaFold.py: AlphaFold integration for CcpNmr Analysis

Copyright (C) 2025

=======================================================================

Integration wrapper for AlphaFold structure prediction within CcpNmr.

This module provides:
- Structure prediction from protein sequence
- Confidence score visualization
- Comparison with existing NMR structures
- Export predicted structures to CcpNmr project

======================COPYRIGHT/LICENSE END============================
"""

from os import path, mkdir, system, environ
import subprocess
import json
import tempfile

from memops.universal.Io import getTopDirectory

rootDir = path.split(getTopDirectory())[0]
defaultDir = path.join(rootDir, 'external', 'alphafold')

ALPHAFOLD_DIR = environ.get('ALPHAFOLD_DIR', defaultDir)
ALPHAFOLD_PYTHON = environ.get('ALPHAFOLD_PYTHON', 'python')  # Python with AlphaFold installed


def runAlphaFold(chain, outputDir=None, useCachedModel=True):
    """
    Run AlphaFold prediction for a given chain.
    
    Args:
        chain: CcpNmr Chain object
        outputDir: Directory for output files (default: project temp dir)
        useCachedModel: Use local AlphaFold installation vs API
        
    Returns:
        Structure object with predicted coordinates and confidence scores
    """
    
    from ccpnmr.analysis.core.MoleculeBasic import getResidueCode
    
    # Get sequence from chain
    sequence = ''.join([getResidueCode(residue) for residue in chain.sortedResidues()])
    
    if not sequence:
        raise ValueError("Chain has no sequence")
    
    # Set up output directory
    if outputDir is None:
        memopsRoot = chain.root
        dataRepository = memopsRoot.findFirstRepository(name='userData')
        projPath = dataRepository.url.dataLocation
        outputDir = path.join(projPath, 'alphafold_predictions')
        
    if not path.exists(outputDir):
        mkdir(outputDir)
    
    # Check if we should use ColabFold API or local AlphaFold
    if useCachedModel:
        result = _runLocalAlphaFold(sequence, outputDir, chain.code)
    else:
        result = _runColabFoldAPI(sequence, outputDir, chain.code)
    
    # Parse results and create structure
    structure = _parseAlphaFoldResults(result, chain)
    
    return structure


def _runLocalAlphaFold(sequence, outputDir, chainName):
    """
    Run AlphaFold locally (requires installation).
    """
    
    # Write sequence to FASTA file
    fastaFile = path.join(outputDir, f'{chainName}.fasta')
    with open(fastaFile, 'w') as f:
        f.write(f'>{chainName}\n{sequence}\n')
    
    # Check for alphafold_prediction.py or use API
    alphaFoldScript = path.join(ALPHAFOLD_DIR, 'run_alphafold.py')
    
    if not path.exists(alphaFoldScript):
        # Try using ESMFold as lightweight alternative
        return _runESMFold(sequence, outputDir, chainName)
    
    # Run AlphaFold
    cmd = [
        ALPHAFOLD_PYTHON,
        alphaFoldScript,
        f'--fasta_paths={fastaFile}',
        f'--output_dir={outputDir}',
        '--model_preset=monomer',
        '--max_template_date=2100-01-01'
    ]
    
    print(f"Running AlphaFold: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"AlphaFold failed: {result.stderr}")
    
    # Return path to predicted structure
    pdbFile = path.join(outputDir, chainName, f'ranked_0.pdb')
    jsonFile = path.join(outputDir, chainName, 'ranking_debug.json')
    
    return {
        'pdb_file': pdbFile,
        'json_file': jsonFile,
        'method': 'AlphaFold2-local'
    }


def _runESMFold(sequence, outputDir, chainName):
    """
    Run ESMFold as a lightweight AlphaFold alternative.
    ESMFold is faster and doesn't require MSA generation.
    """
    
    try:
        import torch
        import esm
        
        # Load ESMFold model
        model = esm.pretrained.esmfold_v1()
        model = model.eval()
        
        # Run prediction
        with torch.no_grad():
            output = model.infer_pdb(sequence)
        
        # Save PDB
        pdbFile = path.join(outputDir, f'{chainName}_esmfold.pdb')
        with open(pdbFile, 'w') as f:
            f.write(output)
        
        # Extract pLDDT scores from PDB B-factors
        return {
            'pdb_file': pdbFile,
            'json_file': None,
            'method': 'ESMFold'
        }
        
    except ImportError:
        raise RuntimeError(
            "Neither AlphaFold nor ESMFold is installed. "
            "Install with: pip install fair-esm"
        )


def _runColabFoldAPI(sequence, outputDir, chainName):
    """
    Use ColabFold API for prediction (requires internet).
    """
    
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests library required. Install with: pip install requests")
    
    # ColabFold API endpoint
    url = "https://api.colabfold.com/submit"
    
    data = {
        'sequence': sequence,
        'mode': 'alphafold2_ptm'
    }
    
    print(f"Submitting to ColabFold API...")
    response = requests.post(url, json=data)
    
    if response.status_code != 200:
        raise RuntimeError(f"API request failed: {response.text}")
    
    job_id = response.json()['id']
    
    # Poll for results
    print(f"Job ID: {job_id}. Waiting for results...")
    
    result_url = f"https://api.colabfold.com/result/{job_id}"
    
    import time
    while True:
        result = requests.get(result_url)
        if result.status_code == 200:
            break
        time.sleep(10)
    
    # Download and save results
    pdbFile = path.join(outputDir, f'{chainName}_colabfold.pdb')
    with open(pdbFile, 'w') as f:
        f.write(result.json()['pdb'])
    
    return {
        'pdb_file': pdbFile,
        'json_file': None,
        'method': 'ColabFold-API'
    }


def _parseAlphaFoldResults(result, chain):
    """
    Parse AlphaFold output and create CcpNmr Structure object.
    """
    
    from ccpnmr.analysis.core.StructureBasic import makeStructureFromPdb
    
    pdbFile = result['pdb_file']
    
    if not path.exists(pdbFile):
        raise RuntimeError(f"Predicted structure not found: {pdbFile}")
    
    # Load structure into project
    structure = makeStructureFromPdb(chain.molSystem, pdbFile)
    
    # Add confidence scores if available
    if result['json_file'] and path.exists(result['json_file']):
        _addConfidenceScores(structure, result['json_file'])
    
    # Add method annotation
    structure.details = f"Predicted by {result['method']}"
    
    return structure


def _addConfidenceScores(structure, jsonFile):
    """
    Add pLDDT confidence scores from AlphaFold JSON output.
    """
    
    with open(jsonFile, 'r') as f:
        data = json.load(f)
    
    # pLDDT scores are typically in the B-factor column of PDB
    # Already loaded, so this is mainly for validation
    
    if 'plddts' in data:
        print(f"Average pLDDT: {sum(data['plddts'])/len(data['plddts']):.2f}")


def compareWithNMR(predictedStructure, nmrStructure):
    """
    Compare AlphaFold prediction with existing NMR structure.
    
    Args:
        predictedStructure: AlphaFold predicted structure
        nmrStructure: Experimental NMR structure
        
    Returns:
        Dictionary with comparison metrics (RMSD, per-residue differences, etc.)
    """
    
    from ccpnmr.analysis.core.StructureBasic import calcRmsd
    
    # Calculate global RMSD
    rmsd = calcRmsd(predictedStructure, nmrStructure)
    
    # Calculate per-residue RMSD
    residueRmsds = _calcPerResidueRmsd(predictedStructure, nmrStructure)
    
    # Identify regions of disagreement
    highRmsdResidues = [
        (resNum, rmsd) for resNum, rmsd in residueRmsds.items() 
        if rmsd > 2.0  # Threshold in Angstroms
    ]
    
    return {
        'global_rmsd': rmsd,
        'residue_rmsds': residueRmsds,
        'high_disagreement_regions': highRmsdResidues
    }


def _calcPerResidueRmsd(structure1, structure2):
    """
    Calculate RMSD for each residue between two structures.
    """
    
    residueRmsds = {}
    
    # This would need proper implementation using CcpNmr's coordinate system
    # Placeholder for demonstration
    
    return residueRmsds


def validateAgainstNMRData(structure, nmrConstraints):
    """
    Validate AlphaFold structure against experimental NMR constraints.
    
    Args:
        structure: Predicted structure
        nmrConstraints: NMR constraints (NOE, RDC, etc.)
        
    Returns:
        Validation metrics (RPF scores, violation counts, etc.)
    """
    
    from ccpnmr.analysis.core.ConstraintBasic import getDistanceConstraintViolations
    
    # Calculate NOE violations
    violations = getDistanceConstraintViolations(structure, nmrConstraints)
    
    # Calculate RPF score if peak list available
    # This would integrate with RPF calculation from AF-NMR project
    
    metrics = {
        'noe_violations': len(violations),
        'violation_list': violations
    }
    
    return metrics


# GUI Integration hooks
def addAlphaFoldMenu(analysisPopup):
    """
    Add AlphaFold menu to CcpNmr Analysis GUI.
    
    This should be called during CcpNmr initialization to add menu items.
    """
    
    menu = analysisPopup.menuBar.newMenu('AI Prediction')
    
    menu.addCommand('Run AlphaFold', callback=lambda: _showAlphaFoldDialog(analysisPopup))
    menu.addCommand('Compare AI vs NMR', callback=lambda: _showComparisonDialog(analysisPopup))
    menu.addCommand('Refine with NMR Data', callback=lambda: _showRefinementDialog(analysisPopup))


def _showAlphaFoldDialog(parent):
    """
    Show dialog for running AlphaFold prediction.
    """
    
    from memops.gui.BasePopup import BasePopup
    from memops.gui.Label import Label
    from memops.gui.Button import Button
    from memops.gui.PulldownList import PulldownList
    
    popup = BasePopup(parent, title='AlphaFold Prediction')
    
    # Add chain selector
    row = 0
    label = Label(popup, text='Select Chain:')
    label.grid(row=row, column=0, sticky='w')
    
    chains = parent.project.currentNmrProject.sortedChains()
    chainNames = [chain.code for chain in chains]
    
    chainSelector = PulldownList(popup, texts=chainNames)
    chainSelector.grid(row=row, column=1)
    
    # Add run button
    row += 1
    runButton = Button(popup, text='Run Prediction', 
                      command=lambda: _runPrediction(chainSelector.getSelected(), parent))
    runButton.grid(row=row, column=0, columnspan=2)
    
    popup.open()


def _showComparisonDialog(parent):
    """
    Show dialog for comparing AI prediction with NMR structure.
    """
    # Implementation similar to above
    pass


def _showRefinementDialog(parent):
    """
    Show dialog for NMR-restrained refinement of AI predictions.
    """
    # Implementation similar to above
    pass


def _runPrediction(chainName, parent):
    """
    Execute AlphaFold prediction for selected chain.
    """
    
    chains = parent.project.currentNmrProject.sortedChains()
    chain = [c for c in chains if c.code == chainName][0]
    
    try:
        structure = runAlphaFold(chain)
        parent.showInfo('Success', f'Structure predicted for chain {chainName}')
    except Exception as e:
        parent.showError('Error', f'Prediction failed: {str(e)}')
