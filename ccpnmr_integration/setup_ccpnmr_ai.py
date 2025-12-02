#!/usr/bin/env python
"""
setup_ccpnmr_ai.py

Installation script for AI integration into CcpNmr Analysis.

Usage:
    python setup_ccpnmr_ai.py --ccpnmr ~/nmr/ccpnmr2.4 [options]
    
Options:
    --install-deps      Install Python dependencies
    --test             Run integration tests
    --dry-run          Show what would be done without doing it
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Install AI integration for CcpNmr Analysis'
    )
    parser.add_argument(
        '--ccpnmr',
        required=True,
        help='Path to ccpnmr2.4 installation'
    )
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install Python dependencies'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run integration tests after installation'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without doing it'
    )
    
    args = parser.parse_args()
    
    ccpnmr_path = Path(args.ccpnmr).expanduser().resolve()
    
    if not ccpnmr_path.exists():
        print(f"Error: CcpNmr path does not exist: {ccpnmr_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("CcpNmr AI Integration Setup")
    print("=" * 70)
    print(f"CcpNmr location: {ccpnmr_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'INSTALL'}")
    print()
    
    # Installation steps
    steps = [
        ("Check CcpNmr structure", lambda: check_ccpnmr_structure(ccpnmr_path)),
        ("Copy wrapper files", lambda: copy_wrappers(ccpnmr_path, args.dry_run)),
        ("Copy popup files", lambda: copy_popups(ccpnmr_path, args.dry_run)),
        ("Modify AnalysisGui", lambda: modify_analysis_gui(ccpnmr_path, args.dry_run)),
    ]
    
    if args.install_deps:
        steps.append(
            ("Install dependencies", lambda: install_dependencies(ccpnmr_path, args.dry_run))
        )
    
    if args.test:
        steps.append(
            ("Run tests", lambda: run_tests(ccpnmr_path))
        )
    
    # Execute steps
    for i, (description, func) in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] {description}...")
        try:
            func()
            print(f"    ✓ Success\n")
        except Exception as e:
            print(f"    ✗ Failed: {e}\n")
            if not args.dry_run:
                sys.exit(1)
    
    print("=" * 70)
    if args.dry_run:
        print("Dry run complete. Re-run without --dry-run to install.")
    else:
        print("Installation complete!")
        print("\nNext steps:")
        print("1. Restart CcpNmr Analysis")
        print("2. Look for 'AI Tools' menu in main window")
        print("3. Try: AI Tools → Predict Structure")
        print("\nFor help: see ccpnmr_integration/INTEGRATION_GUIDE.md")
    print("=" * 70)


def check_ccpnmr_structure(ccpnmr_path):
    """Verify CcpNmr directory structure."""
    
    required_paths = [
        'ccpnmr2.4/python/ccpnmr/analysis',
        'ccpnmr2.4/python/ccpnmr/analysis/wrappers',
        'ccpnmr2.4/python/ccpnmr/analysis/popups',
        'ccpnmr2.4/python/ccpnmr/analysis/AnalysisGui.py',
    ]
    
    for rel_path in required_paths:
        full_path = ccpnmr_path / rel_path
        if not full_path.exists():
            raise FileNotFoundError(f"Required path not found: {rel_path}")
    
    print(f"    ✓ CcpNmr structure validated")


def copy_wrappers(ccpnmr_path, dry_run):
    """Copy wrapper files to CcpNmr installation."""
    
    src_dir = Path(__file__).parent / 'wrappers'
    dst_dir = ccpnmr_path / 'ccpnmr2.4/python/ccpnmr/analysis/wrappers'
    
    if not src_dir.exists():
        raise FileNotFoundError(f"Source wrappers directory not found: {src_dir}")
    
    wrapper_files = list(src_dir.glob('*.py'))
    
    if not wrapper_files:
        print(f"    ⚠ No wrapper files found in {src_dir}")
        return
    
    for src_file in wrapper_files:
        dst_file = dst_dir / src_file.name
        
        if dst_file.exists():
            print(f"    ⚠ {src_file.name} already exists, backing up...")
            if not dry_run:
                backup = dst_file.with_suffix('.py.backup')
                shutil.copy2(dst_file, backup)
        
        print(f"    → Copying {src_file.name}")
        if not dry_run:
            shutil.copy2(src_file, dst_file)


def copy_popups(ccpnmr_path, dry_run):
    """Copy popup dialog files to CcpNmr installation."""
    
    src_dir = Path(__file__).parent / 'popups'
    dst_dir = ccpnmr_path / 'ccpnmr2.4/python/ccpnmr/analysis/popups'
    
    if not src_dir.exists():
        print(f"    ⓘ Popup directory not found (optional): {src_dir}")
        print(f"    ⓘ Will use command-line interface for now")
        return
    
    popup_files = list(src_dir.glob('*.py'))
    
    for src_file in popup_files:
        dst_file = dst_dir / src_file.name
        print(f"    → Copying {src_file.name}")
        if not dry_run:
            shutil.copy2(src_file, dst_file)


def modify_analysis_gui(ccpnmr_path, dry_run):
    """Add AI menu to AnalysisGui.py"""
    
    gui_file = ccpnmr_path / 'ccpnmr2.4/python/ccpnmr/analysis/AnalysisGui.py'
    
    if not gui_file.exists():
        raise FileNotFoundError(f"AnalysisGui.py not found")
    
    with open(gui_file, 'r') as f:
        content = f.read()
    
    # Check if already modified
    if 'AI Tools' in content or 'AlphaFold' in content:
        print(f"    ⓘ AnalysisGui.py already appears to be modified")
        print(f"    ⓘ Skipping modification (manual review recommended)")
        return
    
    print(f"    ⚠ Automatic GUI modification not yet implemented")
    print(f"    ⓘ Manual step required:")
    print(f"    ⓘ 1. Open {gui_file}")
    print(f"    ⓘ 2. Add AI Tools menu (see INTEGRATION_GUIDE.md)")
    print(f"    ⓘ 3. Or wait for GUI popup implementation")


def install_dependencies(ccpnmr_path, dry_run):
    """Install Python dependencies."""
    
    venv_path = ccpnmr_path / 'venv'
    
    if not venv_path.exists():
        print(f"    ⚠ Virtual environment not found at {venv_path}")
        print(f"    ⓘ Using system Python instead")
        python = sys.executable
    else:
        python = str(venv_path / 'bin' / 'python')
    
    packages = [
        'fair-esm',      # ESMFold (lightweight AI prediction)
        'torch',         # Required for ESMFold
        'biopython',     # Structure manipulation
        'numpy',         # Numerical operations
        'scipy',         # Scientific computing
        'requests',      # For API calls
    ]
    
    print(f"    → Installing packages: {', '.join(packages)}")
    
    if not dry_run:
        import subprocess
        cmd = [python, '-m', 'pip', 'install'] + packages
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Dependency installation failed: {result.stderr}")


def run_tests(ccpnmr_path):
    """Run integration tests."""
    
    test_dir = Path(__file__).parent / 'tests'
    
    if not test_dir.exists():
        print(f"    ⓘ Test directory not found: {test_dir}")
        print(f"    ⓘ Skipping tests")
        return
    
    print(f"    → Running integration tests...")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', str(test_dir), '-v'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Tests failed")


if __name__ == '__main__':
    main()
