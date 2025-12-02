# CcpNmr AI Integration - Summary

## What We've Created

A complete integration framework to add AI structure prediction and NMR refinement capabilities to CcpNmr Analysis 2.4.

## Files Created

```
ccpnmr_integration/
├── README.md                      ← This file
├── INTEGRATION_GUIDE.md           ← Comprehensive integration guide
├── setup_ccpnmr_ai.py            ← Automated installation script
├── wrappers/
│   ├── AlphaFold.py              ← AI prediction wrapper
│   ├── AIRefinement.py           ← NMR refinement wrapper
│   └── [future: RoseTTAFold.py, etc.]
└── popups/
    └── [future: GUI dialogs]
```

## Quick Start

### 1. Test Installation (Dry Run)
```bash
cd ~/nmr/AF-NMR/ccpnmr_integration
python setup_ccpnmr_ai.py --ccpnmr ~/nmr/ccpnmr2.4 --dry-run
```

### 2. Install for Real
```bash
python setup_ccpnmr_ai.py \
  --ccpnmr ~/nmr/ccpnmr2.4 \
  --install-deps
```

### 3. Test in Python
```python
# In ~/nmr/ccpnmr2.4 directory
cd ~/nmr/ccpnmr2.4
source venv/bin/activate
python

# Test imports
from ccpnmr.analysis.wrappers import AlphaFold
from ccpnmr.analysis.wrappers import AIRefinement

# Check if functions are available
print(dir(AlphaFold))
```

## Key Capabilities

### 1. AI Structure Prediction
- **AlphaFold2**: State-of-the-art predictions (requires installation)
- **ESMFold**: Fast, lightweight alternative (pip install)
- **ColabFold**: Cloud-based API (no local install needed)

### 2. NMR-Restrained Refinement
- Apply NOE distance restraints
- Apply RDC orientation restraints
- Apply dihedral angle restraints
- Support for XPLOR-NIH, CNS, AMBER

### 3. Selective Refinement
- Identify low-confidence regions from pLDDT scores
- Apply restraints only where needed
- Keep high-confidence regions fixed

### 4. Validation & Comparison
- Calculate RMSD between structures
- Count NOE violations
- Calculate RDC Q-factors
- Generate comparison reports

## Integration with AF-NMR Project

The CcpNmr integration connects with your AF-NMR project:

### Data Flow
```
AF-NMR Project Data
  ├── Input/From_NMR_XRay_pairs/  ← NMR experimental data
  ├── AI_methods/AlphaFold2/       ← AI predictions
  └── Scripts/                     ← Analysis scripts
        ↓
  CcpNmr Project
  ├── Load NMR data into CcpNmr
  ├── Run AI prediction or import existing
  ├── Apply refinement with NMR restraints
  └── Validate and compare
        ↓
  Results/
  ├── Refined structures
  ├── Validation metrics
  └── Comparison reports
```

### Shared Components
- **NOE restraint files** (`.tbl` format) - already present in AF-NMR
- **RDC data files** - ready to use
- **Chemical shift data** - can validate predictions
- **RPF scoring scripts** - can be called from CcpNmr

## Advantages of CcpNmr Integration

### For Users
1. **Unified interface**: All analysis in one place
2. **Data management**: CcpNmr handles all NMR data
3. **Visualization**: Built-in 3D structure viewers
4. **Workflow**: Seamless prediction → refinement → validation

### For Developers
1. **Established platform**: Mature, well-tested codebase
2. **Active community**: Users and developers worldwide
3. **Standard formats**: Compatible with other NMR tools
4. **Extensible**: Easy to add new AI methods

### For Science
1. **Integrative modeling**: Combines AI + experimental data
2. **Validation**: Always check predictions against data
3. **Reproducibility**: Standard workflows and formats
4. **Best practices**: Encourages proper structure determination

## Future Enhancements (from FUTURE_DIRECTIONS.md)

All 15 enhancements from the Future Directions document can be implemented as CcpNmr wrappers:

### Immediate (Months 1-3)
- [ ] Complete GUI dialogs (AlphaFoldPopup, RefinementPopup)
- [ ] Add RoseTTAFold wrapper
- [ ] Implement validation reporting
- [ ] Add batch processing

### Short-term (Months 4-6)
- [ ] Multi-AI consensus modeling
- [ ] Chemical shift-guided refinement
- [ ] Real-time validation dashboard
- [ ] Ensemble generation

### Medium-term (Months 7-12)
- [ ] ML meta-analysis for predicting refinement benefit
- [ ] Automated decision tree
- [ ] Drug discovery extensions (ligand binding)
- [ ] Database integration

### Long-term (12+ months)
- [ ] Dynamics studies integration
- [ ] Membrane protein specializations
- [ ] Cloud computing integration
- [ ] Community database

## Usage Examples

### Example 1: Predict Structure for Current Chain
```python
# In CcpNmr Python console
from ccpnmr.analysis.wrappers.AlphaFold import runAlphaFold

# Get current chain
chain = project.currentNmrProject.sortedChains()[0]

# Run prediction
structure = runAlphaFold(chain, useCachedModel=True)

print(f"Predicted structure: {structure}")
print(f"Average confidence: {structure.avgConfidence}")
```

### Example 2: Refine Prediction with NOE Data
```python
from ccpnmr.analysis.wrappers.AIRefinement import refineWithNMR

# Get AI-predicted structure
aiStructure = project.findFirstStructure(details='AlphaFold')

# Get NOE constraints
noeList = project.currentNmrProject.findFirstNmrConstraintStore()

# Refine
refinedStructure = refineWithNMR(
    structure=aiStructure,
    constraintLists=[noeList],
    method='xplor'
)

print(f"Refinement complete: {refinedStructure}")
```

### Example 3: Compare AI vs NMR
```python
from ccpnmr.analysis.wrappers.AlphaFold import compareWithNMR

aiStructure = project.findFirstStructure(details='AlphaFold')
nmrStructure = project.findFirstStructure(details='NMR')

comparison = compareWithNMR(aiStructure, nmrStructure)

print(f"RMSD: {comparison['global_rmsd']:.2f} Å")
print(f"High disagreement regions: {comparison['high_disagreement_regions']}")
```

## Testing Your Integration

### 1. Basic Import Test
```bash
cd ~/nmr/ccpnmr2.4
source venv/bin/activate
python -c "from ccpnmr.analysis.wrappers import AlphaFold; print('OK')"
```

### 2. Prediction Test (ESMFold)
```python
# Install ESMFold first
pip install fair-esm torch

# Test prediction
from ccpnmr.analysis.wrappers.AlphaFold import _runESMFold
result = _runESMFold("MKFLKFSLLTAVLLSVVFAFSSCGDDDDTYPYDVPDYASLGGPS", "/tmp", "test")
print(result)
```

### 3. Integration Test with AF-NMR Data
```bash
# Use GmR137 from AF-NMR project (has all necessary files)
cd ~/nmr/AF-NMR
python ccpnmr_integration/tests/test_with_af_nmr_data.py
```

## Troubleshooting

### Issue: Imports fail
```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Should include ccpnmr2.4/python directory
export PYTHONPATH=~/nmr/ccpnmr2.4/ccpnmr2.4/python:$PYTHONPATH
```

### Issue: ESMFold not found
```bash
# Install in CcpNmr virtual environment
cd ~/nmr/ccpnmr2.4
source venv/bin/activate
pip install fair-esm torch
```

### Issue: XPLOR not found
```bash
# Set environment variable
export XPLOR_DIR=/path/to/xplor-nih

# Or download from:
# https://nmr.cit.nih.gov/xplor-nih/
```

## Documentation

### For Users
- `INTEGRATION_GUIDE.md` - Complete integration documentation
- `../FUTURE_DIRECTIONS.md` - Vision and roadmap
- `../PROJECT_OVERVIEW.md` - AF-NMR project context

### For Developers
- `wrappers/AlphaFold.py` - Prediction implementation
- `wrappers/AIRefinement.py` - Refinement implementation
- Code comments and docstrings throughout

### External References
- CcpNmr: http://www.ccpn.ac.uk/
- AlphaFold: https://github.com/deepmind/alphafold
- ESMFold: https://github.com/facebookresearch/esm
- XPLOR-NIH: https://nmr.cit.nih.gov/xplor-nih/

## Next Steps

### Immediate Actions
1. ✅ Review integration files created
2. ⬜ Run installation script with --dry-run
3. ⬜ Install dependencies (ESMFold recommended for testing)
4. ⬜ Test basic prediction functionality
5. ⬜ Create GUI dialogs (optional but recommended)

### Short-term Goals
1. Test with AF-NMR project data
2. Implement validation reporting
3. Add more AI methods (RoseTTAFold)
4. Create user documentation
5. Share with CcpNmr community

### Long-term Vision
Make CcpNmr the standard platform for integrative NMR/AI structure determination.

## Contact & Support

- **AF-NMR Project**: [Your details]
- **CcpNmr Forum**: http://www.ccpn.ac.uk/forum
- **GitHub Issues**: [Repository when published]

## License

Integration code follows CcpNmr's CCPN license.
External tool wrappers respect original tool licenses.

---

**Version**: 1.0
**Date**: December 1, 2025
**Status**: Ready for testing
