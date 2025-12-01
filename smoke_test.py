#!/usr/bin/env python3
"""
Comprehensive smoke test for ccpnmr2.4 repository.

Tests:
1. Python implementation imports (mem_cache, atom, peak)
2. Wrapper imports (py_*.py files)
3. Unit test suite execution
4. Basic functionality of new implementations

Run with: python3 smoke_test.py
"""

import sys
import os
import subprocess
import traceback
from pathlib import Path

# ANSI color codes for prettier output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_section(title):
    """Print a section header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(msg):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {msg}")

def print_failure(msg):
    """Print failure message."""
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {msg}")

def test_python_implementations():
    """Test that pure Python implementations can be imported."""
    print_section("Testing Pure Python Implementations")
    
    results = {'passed': 0, 'failed': 0}
    
    # Add Python path
    sys.path.insert(0, str(Path(__file__).parent / 'ccpnmr2.4' / 'python'))
    
    tests = [
        ('memops.c.python_impl.mem_cache', 'MemCache', 'new_mem_cache'),
        ('ccp.c.python_impl.atom', 'Atom', 'new_atom'),
        ('ccpnmr.analysis.python_impl.peak', 'Peak', 'new_peak'),
    ]
    
    for module_name, class_name, func_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name, func_name])
            
            # Check class exists
            if not hasattr(module, class_name):
                print_failure(f"{module_name}: Missing class {class_name}")
                results['failed'] += 1
                continue
            
            # Check function exists
            if not hasattr(module, func_name):
                print_failure(f"{module_name}: Missing function {func_name}")
                results['failed'] += 1
                continue
            
            # Try to create an instance
            if module_name.endswith('mem_cache'):
                obj = module.new_mem_cache(100, None, None)
            elif module_name.endswith('atom'):
                obj = module.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
            elif module_name.endswith('peak'):
                obj = module.new_peak(2)
            
            print_success(f"{module_name}: OK (class {class_name}, function {func_name})")
            results['passed'] += 1
            
        except Exception as e:
            print_failure(f"{module_name}: {str(e)}")
            results['failed'] += 1
    
    return results

def test_wrapper_imports():
    """Test that wrapper files can be imported."""
    print_section("Testing Wrapper Imports")
    
    results = {'passed': 0, 'failed': 0}
    
    root = Path(__file__).parent
    
    # Test our three main wrappers
    wrappers = [
        root / 'ccpnmr2.4' / 'c' / 'memops' / 'global' / 'py_mem_cache.py',
        root / 'ccpnmr2.4' / 'c' / 'ccp' / 'structure' / 'py_atom.py',
        root / 'ccpnmr2.4' / 'c' / 'ccpnmr' / 'analysis' / 'py_peak.py',
    ]
    
    import importlib.util
    
    for wrapper_path in wrappers:
        if not wrapper_path.exists():
            print_warning(f"{wrapper_path.name}: File not found")
            continue
        
        try:
            spec = importlib.util.spec_from_file_location(wrapper_path.stem, str(wrapper_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                print_success(f"{wrapper_path.name}: OK")
                results['passed'] += 1
            else:
                print_failure(f"{wrapper_path.name}: Could not load spec")
                results['failed'] += 1
        except Exception as e:
            print_failure(f"{wrapper_path.name}: {str(e)}")
            results['failed'] += 1
    
    return results

def test_unit_tests():
    """Run the unit test suite."""
    print_section("Running Unit Tests")
    
    root = Path(__file__).parent
    tests_dir = root / 'tests'
    
    if not tests_dir.exists():
        print_warning("tests/ directory not found")
        return {'passed': 0, 'failed': 1}
    
    try:
        # Run unittest discovery
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', 'tests'],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse output
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            # Extract test count
            for line in output.split('\n'):
                if 'Ran' in line and 'test' in line:
                    print_success(f"Unit tests: {line.strip()}")
            print_success("All unit tests passed")
            return {'passed': 1, 'failed': 0}
        else:
            print_failure("Unit tests failed")
            # Show last few lines of output
            lines = output.split('\n')
            for line in lines[-10:]:
                if line.strip():
                    print(f"  {line}")
            return {'passed': 0, 'failed': 1}
            
    except subprocess.TimeoutExpired:
        print_failure("Unit tests timed out (>30s)")
        return {'passed': 0, 'failed': 1}
    except Exception as e:
        print_failure(f"Could not run unit tests: {str(e)}")
        return {'passed': 0, 'failed': 1}

def test_basic_functionality():
    """Test basic functionality of implementations."""
    print_section("Testing Basic Functionality")
    
    results = {'passed': 0, 'failed': 0}
    
    import sys as sys_module
    sys_module.path.insert(0, str(Path(__file__).parent / 'ccpnmr2.4' / 'python'))
    
    # Test mem_cache
    try:
        from memops.c.python_impl import mem_cache
        cache = mem_cache.new_mem_cache(1000, None, None)
        # Use a string as the cached object (must be hashable)
        test_obj = "test_value_123"
        obj_size = sys_module.getsizeof(test_obj)
        mem_cache.add_mem_cache(cache, test_obj, obj_size)
        # Check it's in cache by trying to lock it
        lock_result = mem_cache.lock_mem_cache(cache, test_obj)
        if lock_result:
            mem_cache.unlock_mem_cache(cache, test_obj)  # Unlock after checking
            print_success("mem_cache: add/lock/unlock works")
            results['passed'] += 1
        else:
            print_failure("mem_cache: object not found in cache")
            results['failed'] += 1
    except Exception as e:
        print_failure(f"mem_cache: {str(e)}")
        results['failed'] += 1
    
    # Test atom
    try:
        from ccp.c.python_impl import atom
        a = atom.new_atom(1.5, 'C', 'CA', [1.0, 2.0, 3.0], [0.5, 0.5, 0.5])
        atom.translate_atom(a, [1.0, 1.0, 1.0])
        if a.x == [2.0, 3.0, 4.0]:
            print_success("atom: translation works")
            results['passed'] += 1
        else:
            print_failure(f"atom: translation failed (got {a.x})")
            results['failed'] += 1
    except Exception as e:
        print_failure(f"atom: {str(e)}")
        results['failed'] += 1
    
    # Test peak
    try:
        from ccpnmr.analysis.python_impl import peak
        p = peak.new_peak(2)
        peak.set_position_peak(p, [100.0, 200.0])
        if p.position == [100.0, 200.0]:
            print_success("peak: position setting works")
            results['passed'] += 1
        else:
            print_failure(f"peak: position setting failed (got {p.position})")
            results['failed'] += 1
    except Exception as e:
        print_failure(f"peak: {str(e)}")
        results['failed'] += 1
    
    return results

def main():
    """Run all smoke tests."""
    print(f"\n{BOLD}CCPNMR 2.4 Smoke Test Suite{RESET}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Working directory: {Path(__file__).parent}")
    
    all_results = {
        'Python Implementations': test_python_implementations(),
        'Wrapper Imports': test_wrapper_imports(),
        'Unit Tests': test_unit_tests(),
        'Basic Functionality': test_basic_functionality(),
    }
    
    # Summary
    print_section("Summary")
    
    total_passed = 0
    total_failed = 0
    
    for test_name, results in all_results.items():
        passed = results['passed']
        failed = results['failed']
        total_passed += passed
        total_failed += failed
        
        status = f"{passed} passed, {failed} failed"
        if failed == 0:
            print_success(f"{test_name}: {status}")
        else:
            print_failure(f"{test_name}: {status}")
    
    print(f"\n{BOLD}Total: {total_passed} passed, {total_failed} failed{RESET}")
    
    if total_failed == 0:
        print(f"\n{GREEN}{BOLD}✓ All smoke tests passed!{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ Some smoke tests failed{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
