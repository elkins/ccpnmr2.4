# CcpNmr AI Integration Strategy

## Overview

This document outlines the strategy for integrating AI structure prediction and NMR refinement capabilities into CcpNmr Analysis 2.4.

## Architecture

### Current CcpNmr Structure
```
ccpnmr2.4/
├── python/
│   ├── ccpnmr/
│   │   └── analysis/
│   │       ├── AnalysisGui.py          # Main GUI
│   │       ├── core/                    # Core functionality
│   │       ├── popups/                  # Dialog windows
│   │       └── wrappers/                # External tool integrations
│   │           ├── Shiftx.py           # Chemical shift prediction
│   │           ├── Mars.py             # Structure calculation
│   │           ├── Psipred.py          # Secondary structure
│   │           └── [new AI tools]      # ← ADD HERE
│   ├── ccp/
│   └── memops/
```

### New AI Integration Components
```
wrappers/
├── AlphaFold.py              # AlphaFold prediction
├── RoseTTAFold.py            # Alternative AI method
├── ESMFold.py                # Lightweight alternative
├── AIRefinement.py           # NMR-restrained refinement
├── AIValidation.py           # AI vs NMR comparison
└── IntegrativeModeling.py    # Full pipeline

popups/
├── AlphaFoldPopup.py         # GUI for predictions
├── RefinementPopup.py        # GUI for refinement
└── AIComparisonPopup.py      # GUI for comparisons
```

## Installation Steps

### 1. Copy Integration Files

```bash
# Copy wrappers to CcpNmr
cp ccpnmr_integration/wrappers/*.py \
   ~/nmr/ccpnmr2.4/ccpnmr2.4/python/ccpnmr/analysis/wrappers/

# Copy popups (when created)
cp ccpnmr_integration/popups/*.py \
   ~/nmr/ccpnmr2.4/ccpnmr2.4/python/ccpnmr/analysis/popups/
```

### 2. Modify AnalysisGui.py

Add AI menu to main interface:

```python
# In AnalysisGui.py, add to menu creation:

from ccpnmr.analysis.wrappers import AlphaFold, AIRefinement

# Add AI Prediction menu
def _setupMenus(self):
    # ... existing menus ...
    
    # NEW: AI Integration menu
    aiMenu = self.menuBar.newMenu('AI Tools')
    aiMenu.addCommand('Predict Structure (AlphaFold)', 
                     callback=self._runAlphaFold)
    aiMenu.addCommand('Refine with NMR Data', 
                     callback=self._refineWithNMR)
    aiMenu.addCommand('Compare AI vs NMR', 
                     callback=self._compareStructures)
    aiMenu.addCommand('Integrative Modeling...', 
                     callback=self._integrativeModeling)

def _runAlphaFold(self):
    from ccpnmr.analysis.popups.AlphaFoldPopup import AlphaFoldPopup
    popup = AlphaFoldPopup(self)
    popup.open()

def _refineWithNMR(self):
    from ccpnmr.analysis.popups.RefinementPopup import RefinementPopup
    popup = RefinementPopup(self)
    popup.open()
```

### 3. Install Dependencies

```bash
# Activate CcpNmr environment
cd ~/nmr/ccpnmr2.4
source venv/bin/activate

# Install AI tools (choose based on needs)

# Option 1: ESMFold (lightweight, 5GB)
pip install fair-esm torch

# Option 2: ColabFold (uses API, no local install)
pip install requests

# Option 3: Full AlphaFold (requires significant resources)
# See: https://github.com/deepmind/alphafold

# Install refinement tools
pip install biopython numpy scipy

# Optional: XPLOR-NIH for refinement
# Download from: https://nmr.cit.nih.gov/xplor-nih/
```

## Usage Workflows

### Workflow 1: Quick Structure Prediction

```
User Action: AI Tools → Predict Structure (AlphaFold)
↓
Dialog: Select chain from project
↓
System: Extracts sequence from CcpNmr project
↓
System: Runs ESMFold/AlphaFold/API prediction
↓
System: Imports predicted structure into project
↓
Result: New structure ensemble with confidence scores
```

### Workflow 2: NMR-Refined Prediction

```
User Action: AI Tools → Refine with NMR Data
↓
Dialog: Select AI-predicted structure + NMR constraints
↓
System: Exports structure and constraints
↓
System: Runs XPLOR-NIH/CNS refinement
↓
System: Imports refined structure
↓
Result: Improved structure fitting NMR data
```

### Workflow 3: Validation & Comparison

```
User Action: AI Tools → Compare AI vs NMR
↓
Dialog: Select AI structure vs NMR structure
↓
System: Calculates RMSD, per-residue differences
↓
System: Validates against NMR constraints (NOE, RDC)
↓
Result: Detailed comparison report & visualization
```

### Workflow 4: Integrative Modeling Pipeline

```
User Action: AI Tools → Integrative Modeling
↓
Dialog: Configure full pipeline
↓
System: 
  1. Runs AlphaFold prediction
  2. Identifies low-confidence regions
  3. Applies NMR restraints selectively
  4. Refines with XPLOR
  5. Validates against all NMR data
↓
Result: Optimized structure + detailed report
```

## Integration with Existing CcpNmr Features

### Structure Management
- AI predictions stored as new Structure ensembles
- Confidence scores stored in B-factor fields
- Compatible with existing structure viewers

### Constraint Management  
- Uses existing NOE, RDC, dihedral constraint lists
- Exports to standard formats (XPLOR, CNS)
- Violation analysis uses existing tools

### Assignment Integration
- Can use AI predictions to guide assignments
- Chemical shift validation against predicted structure
- Automated NOE assignment based on AI geometry

### Visualization
- AI structures displayed in existing 3D viewers
- Confidence coloring by pLDDT scores
- Side-by-side comparison views

## Performance Considerations

### Prediction Speed
- **ESMFold**: ~1 minute for 200aa protein
- **ColabFold API**: ~5-15 minutes (internet required)
- **Local AlphaFold**: ~10-60 minutes (GPU recommended)

### Refinement Speed
- **Quick refinement**: ~5-10 minutes
- **Full refinement**: ~30-120 minutes
- **Ensemble generation**: ~2-8 hours

### Resource Requirements
- **ESMFold**: 8GB RAM, 5GB disk
- **Local AlphaFold**: 16GB RAM, 200GB disk, GPU strongly recommended
- **Refinement**: 4GB RAM, 1GB disk

## Data Flow

### Input to AI Prediction
```
CcpNmr Project
  → Molecule/Chain
    → Sequence extraction
      → AI prediction
        → Structure import
          → Store in project
```

### Input to NMR Refinement
```
CcpNmr Project
  → AI-predicted structure
  → NMR constraint lists
    → Export to files
      → XPLOR/CNS refinement
        → Refined structure import
          → Store in project
```

### Validation Data Flow
```
CcpNmr Project
  → AI structure
  → NMR structure (optional)
  → NMR data (peaks, RDCs)
    → Calculate metrics
      → Generate report
        → Display in GUI
```

## Configuration Options

### Environment Variables
```bash
# AlphaFold installation
export ALPHAFOLD_DIR=/path/to/alphafold
export ALPHAFOLD_PYTHON=/path/to/python/with/alphafold

# XPLOR-NIH installation  
export XPLOR_DIR=/path/to/xplor-nih

# CNS installation
export CNS_DIR=/path/to/cns

# Temporary files
export CCPNMR_AI_TMPDIR=/tmp/ccpnmr_ai
```

### CcpNmr Preferences
```python
# Add to Analysis preferences
preferences = {
    'aiPredictionMethod': 'esmfold',  # 'esmfold', 'alphafold', 'colabfold'
    'refinementMethod': 'xplor',       # 'xplor', 'cns', 'amber'
    'confidenceThreshold': 70,         # pLDDT threshold
    'autoRefineLowConfidence': True,   # Automatic selective refinement
    'validateAgainstNMR': True,        # Auto-validate predictions
}
```

## Error Handling

### Common Issues & Solutions

**Issue**: AlphaFold not installed
```
Solution: Use ESMFold (pip install fair-esm) or ColabFold API
```

**Issue**: XPLOR-NIH not found
```
Solution: Set XPLOR_DIR environment variable or install from:
https://nmr.cit.nih.gov/xplor-nih/
```

**Issue**: Prediction fails for long sequence (>2700 residues)
```
Solution: Split into domains, predict separately, then assemble
```

**Issue**: Memory error during prediction
```
Solution: Use ColabFold API or reduce batch size
```

## Testing & Validation

### Unit Tests
```bash
# Test AI prediction
python -m pytest tests/test_alphafold_wrapper.py

# Test refinement
python -m pytest tests/test_refinement.py

# Test integration
python -m pytest tests/test_ccpnmr_integration.py
```

### Integration Tests
```bash
# Full workflow test with AF-NMR data
cd ~/nmr/AF-NMR
python scripts/test_ccpnmr_integration.py \
  --protein GmR137 \
  --ccpnmr ~/nmr/ccpnmr2.4
```

## Future Enhancements

### Phase 1 (Immediate)
- [x] AlphaFold/ESMFold wrapper
- [x] Basic NMR refinement
- [ ] GUI dialogs
- [ ] Integration testing

### Phase 2 (Short-term)
- [ ] RoseTTAFold integration
- [ ] Selective refinement by confidence
- [ ] Ensemble generation
- [ ] Automated validation reports

### Phase 3 (Medium-term)
- [ ] Multi-AI consensus modeling
- [ ] Chemical shift-guided refinement
- [ ] Real-time validation dashboard
- [ ] Batch processing

### Phase 4 (Long-term)
- [ ] ML model for predicting refinement benefit
- [ ] Automated experiment recommendation
- [ ] Cloud computing integration
- [ ] Drug discovery extensions

## Documentation for Users

### Quick Start Guide
```
1. Load your NMR project in CcpNmr Analysis
2. Go to: AI Tools → Predict Structure
3. Select chain to predict
4. Wait for prediction (~1-5 minutes)
5. View predicted structure with confidence colors
6. Optionally refine with your NMR data
```

### Best Practices
- Use ESMFold for quick initial models
- Use full AlphaFold for publication-quality structures
- Always validate against your NMR data
- Refine low-confidence regions with NMR restraints
- Compare multiple AI methods for important targets

### Troubleshooting
- Check log files in project directory
- Verify external tools are installed
- Check sequence has standard amino acids
- Ensure sufficient disk space for predictions

## Support & Community

### Getting Help
- CcpNmr forum: http://www.ccpn.ac.uk/forum
- GitHub issues: [repository URL]
- Email: [contact email]

### Contributing
- Report bugs via GitHub issues
- Suggest features on forum
- Submit pull requests for improvements
- Share successful workflows

## References

### AlphaFold
- Jumper et al. (2021) Nature 596:583-589
- https://github.com/deepmind/alphafold

### ESMFold  
- Lin et al. (2023) Science 379:1123-1130
- https://github.com/facebookresearch/esm

### CcpNmr
- Vranken et al. (2005) Proteins 59:687-696
- http://www.ccpn.ac.uk/

### NMR Refinement
- Schwieters et al. (2003) J Magn Reson 160:65-73
- https://nmr.cit.nih.gov/xplor-nih/

## License

Integration code follows CcpNmr license (CCPN.license).
External tools have their own licenses - check before distribution.
