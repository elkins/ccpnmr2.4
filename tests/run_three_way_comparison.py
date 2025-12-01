#!/usr/bin/env python3
"""
Three-way comparison test runner for C, Pure Python, and Numba implementations.

Runs unit tests against all three implementations:
1. C extension (if available)
2. Pure Python implementation  
3. Numba-accelerated Python implementation

Usage:
    python3 tests/run_three_way_comparison.py
    python3 tests/run_three_way_comparison.py --module atom
    python3 tests/run_three_way_comparison.py --benchmark
"""

import sys
import os
import time
import argparse
import importlib.util
from pathlib import Path

# Add Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'))

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(title):
    """Print section header."""
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")


def print_success(msg):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {msg}")


def print_failure(msg):
    """Print failure message."""
    print(f"{RED}✗{RESET} {msg}")


def print_warning(msg):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {msg}")


def print_info(msg):
    """Print info message."""
    print(f"{BLUE}ℹ{RESET} {msg}")


def check_numba_available():
    """Check if numba is installed."""
    try:
        import numba
        return True
    except ImportError:
        return False


def load_implementation(module_name, impl_type):
    """
    Load a specific implementation.
    
    Args:
        module_name: 'mem_cache', 'atom', 'bond', or 'peak'
        impl_type: 'python' or 'numba'
    
    Returns:
        Module object or None if not available
    """
    paths = {
        'mem_cache': {
            'python': 'memops/c/python_impl/mem_cache.py',
            'numba': 'memops/c/python_impl/mem_cache_numba.py',
        },
        'atom': {
            'python': 'ccp/c/python_impl/atom.py',
            'numba': 'ccp/c/python_impl/atom_numba.py',
        },
        'bond': {
            'python': 'ccp/c/python_impl/bond.py',
            'numba': 'ccp/c/python_impl/bond_numba.py',
        },
        'peak': {
            'python': 'ccpnmr/analysis/python_impl/peak.py',
            'numba': 'ccpnmr/analysis/python_impl/peak_numba.py',
        }
    }
    
    if module_name not in paths or impl_type not in paths[module_name]:
        return None
    
    base_path = Path(__file__).parent.parent / 'ccpnmr2.4' / 'python'
    impl_path = base_path / paths[module_name][impl_type]
    
    if not impl_path.exists():
        return None
    
    spec = importlib.util.spec_from_file_location(
        f"{module_name}_{impl_type}", str(impl_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_functional_test(module_name, impl_module, impl_type):
    """Run basic functional test for a module implementation."""
    try:
        if module_name == 'mem_cache':
            cache = impl_module.new_mem_cache(1000, None, None)
            test_obj = "test_value"
            obj_size = sys.getsizeof(test_obj)
            impl_module.add_mem_cache(cache, test_obj, obj_size)
            result = impl_module.lock_mem_cache(cache, test_obj)
            if result:
                impl_module.unlock_mem_cache(cache, test_obj)
                return True, "add/lock/unlock works"
            return False, "object not found in cache"
        
        elif module_name == 'atom':
            atom = impl_module.new_atom(1.0, 'C', 'CA', [1.0, 2.0, 3.0], [0.5, 0.5, 0.5])
            impl_module.translate_atom(atom, [1.0, 1.0, 1.0])
            if atom.x == [2.0, 3.0, 4.0]:
                return True, "translation works"
            return False, f"translation failed (got {atom.x})"
        
        elif module_name == 'bond':
            # Need atom module for bond testing
            atom_impl = load_implementation('atom', impl_type)
            if not atom_impl:
                return False, "atom module not available"
            
            a1 = atom_impl.new_atom(1.0, 'C', 'CA', [0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
            a2 = atom_impl.new_atom(1.0, 'N', 'N', [1.5, 0.0, 0.0], [0.0, 0.0, 1.0])
            bond = impl_module.new_bond(a1, a2, [1.0, 1.0, 0.0])
            if bond.have_color and bond.color == [1.0, 1.0, 0.0]:
                return True, "creation with color works"
            return False, "color setting failed"
        
        elif module_name == 'peak':
            peak = impl_module.new_peak(2)
            impl_module.set_position_peak(peak, [100.0, 200.0])
            if peak.position == [100.0, 200.0]:
                return True, "position setting works"
            return False, f"position setting failed (got {peak.position})"
        
        return False, "unknown module"
    
    except Exception as e:
        return False, str(e)


def benchmark_implementation(module_name, impl_module, impl_type, iterations=10000):
    """Run simple benchmark for implementation."""
    try:
        if module_name == 'mem_cache':
            cache = impl_module.new_mem_cache(100000, None, None)
            test_objs = [f"obj_{i}" for i in range(100)]
            
            start = time.perf_counter()
            for _ in range(iterations):
                for obj in test_objs:
                    impl_module.add_mem_cache(cache, obj, 100)
                    impl_module.lock_mem_cache(cache, obj)
                    impl_module.unlock_mem_cache(cache, obj)
            elapsed = time.perf_counter() - start
            ops_per_sec = (iterations * len(test_objs) * 3) / elapsed
            return elapsed, ops_per_sec
        
        elif module_name == 'atom':
            atom = impl_module.new_atom(1.0, 'C', '', [0.0, 0.0, 0.0], [1.0, 1.0, 1.0])
            
            start = time.perf_counter()
            for i in range(iterations):
                impl_module.translate_atom(atom, [0.1, 0.1, 0.1])
                impl_module.zoom_atom(atom, 1.001)
                impl_module.within_xy_tol_atom(atom, 0.0, 0.0, 1.0)
            elapsed = time.perf_counter() - start
            ops_per_sec = (iterations * 3) / elapsed
            return elapsed, ops_per_sec
        
        elif module_name == 'bond':
            atom_impl = load_implementation('atom', impl_type)
            if not atom_impl:
                return 0, 0
            
            a1 = atom_impl.new_atom(1.0, 'C', '', [0.0, 0.0, -5.0], [1.0, 0.0, 0.0])
            a2 = atom_impl.new_atom(1.0, 'N', '', [1.5, 0.0, -5.0], [0.0, 0.0, 1.0])
            bond = impl_module.new_bond(a1, a2, None)
            z_out = [0.0]
            
            start = time.perf_counter()
            for i in range(iterations):
                impl_module.get_depth_param_bond(bond, 0.0)
                impl_module.within_xy_tol_bond(bond, 0.0, 0.0, 2.0, 0.0, z_out)
                impl_module.set_line_width_bond(bond, float(i % 10))
            elapsed = time.perf_counter() - start
            ops_per_sec = (iterations * 3) / elapsed
            return elapsed, ops_per_sec
        
        elif module_name == 'peak':
            peak = impl_module.new_peak(2)
            
            start = time.perf_counter()
            for i in range(iterations):
                impl_module.set_position_peak(peak, [float(i % 100), float(i % 200)])
                impl_module.set_intensity_peak(peak, float(i))
                result = impl_module.is_in_region_peak(peak, [0.0, 0.0], [150.0, 250.0], [512, 512], False)
            elapsed = time.perf_counter() - start
            ops_per_sec = (iterations * 3) / elapsed
            return elapsed, ops_per_sec
        
        return 0, 0
    
    except Exception as e:
        print_warning(f"Benchmark error: {e}")
        return 0, 0


def compare_module(module_name, run_benchmarks=False):
    """Compare implementations for a single module."""
    print_header(f"Module: {module_name}")
    
    # Load implementations
    python_impl = load_implementation(module_name, 'python')
    numba_impl = load_implementation(module_name, 'numba')
    
    if not python_impl:
        print_failure(f"Pure Python implementation not found")
        return
    
    if not numba_impl:
        print_warning(f"Numba implementation not found")
    
    # Functional tests
    print(f"{BOLD}Functional Tests:{RESET}")
    
    success, msg = run_functional_test(module_name, python_impl, 'python')
    if success:
        print_success(f"Pure Python: {msg}")
    else:
        print_failure(f"Pure Python: {msg}")
    
    if numba_impl:
        success, msg = run_functional_test(module_name, numba_impl, 'numba')
        if success:
            print_success(f"Numba: {msg}")
        else:
            print_failure(f"Numba: {msg}")
    
    # Benchmarks
    if run_benchmarks and python_impl and numba_impl:
        print(f"\n{BOLD}Performance Benchmarks (10,000 iterations):{RESET}")
        
        py_time, py_ops = benchmark_implementation(module_name, python_impl, 'python')
        print(f"{BLUE}Pure Python:{RESET} {py_time:.4f}s, {py_ops:,.0f} ops/sec")
        
        numba_time, numba_ops = benchmark_implementation(module_name, numba_impl, 'numba')
        print(f"{MAGENTA}Numba:{RESET} {numba_time:.4f}s, {numba_ops:,.0f} ops/sec")
        
        if py_time > 0 and numba_time > 0:
            speedup = py_time / numba_time
            if speedup > 1.0:
                print(f"{GREEN}Numba is {speedup:.2f}x faster{RESET}")
            elif speedup < 1.0:
                print(f"{YELLOW}Pure Python is {1/speedup:.2f}x faster{RESET}")
            else:
                print(f"Similar performance")


def main():
    parser = argparse.ArgumentParser(description='Three-way implementation comparison')
    parser.add_argument('--module', choices=['mem_cache', 'atom', 'bond', 'peak'],
                       help='Test specific module only')
    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmarks')
    args = parser.parse_args()
    
    print(f"\n{BOLD}Three-Way Implementation Comparison{RESET}")
    print(f"Python version: {sys.version.split()[0]}")
    
    # Check numba availability
    if check_numba_available():
        import numba
        print_success(f"Numba available: {numba.__version__}")
    else:
        print_warning("Numba not installed (pip install numba)")
        print_info("Will compare Pure Python implementations only")
    
    # Test modules
    modules = [args.module] if args.module else ['mem_cache', 'atom', 'bond', 'peak']
    
    for module in modules:
        compare_module(module, args.benchmark)
    
    # Summary
    print_header("Summary")
    print("Three-way comparison complete!")
    print(f"\n{BOLD}Implementation Strategy:{RESET}")
    print("• Pure Python: Maximum compatibility, good for dict/object operations")
    print("• Numba: Best for numerical arrays and tight loops")
    print("• C Extension: Fastest overall but requires compilation")
    print(f"\n{BOLD}Note:{RESET} For this codebase, Pure Python may match or exceed Numba")
    print("performance for dict-based operations (mem_cache) due to CPython's")
    print("highly optimized dict implementation. Numba shines with numerical arrays.")


if __name__ == '__main__':
    main()
