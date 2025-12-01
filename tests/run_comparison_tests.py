"""
Test runner for validating C vs Python implementations.

This script runs tests against both implementations (if available)
and compares their behavior to ensure equivalence.
"""

import sys
import os
import unittest
import importlib.util

# Add repo root to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)


def load_implementation(impl_type='python'):
    """
    Load specific implementation.
    
    Args:
        impl_type: 'python' or 'c'
        
    Returns:
        Module object or None if not available
    """
    if impl_type == 'python':
        # Load pure Python implementation directly
        impl_path = os.path.join(repo_root, 'mem_cache.py')
        try:
            spec = importlib.util.spec_from_file_location('mem_cache_python', impl_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            print(f"Could not load Python implementation: {e}")
            return None
    
    elif impl_type == 'c':
        # Try to load C extension directly
        try:
            # This would import the compiled C extension if available
            import memops.global.mem_cache as c_impl
            return c_impl
        except ImportError:
            print("C implementation not available (extension not compiled)")
            return None
    
    return None


def run_tests_for_implementation(impl_module, impl_name):
    """
    Run tests using specific implementation.
    
    Args:
        impl_module: Module containing implementation
        impl_name: Name for reporting (e.g., "Python", "C")
        
    Returns:
        TestResult object
    """
    print(f"\n{'='*70}")
    print(f"Testing {impl_name} implementation")
    print(f"{'='*70}\n")
    
    # Temporarily inject implementation into test module
    import tests.test_mem_cache as test_module
    
    # Create a wrapper module that matches expected interface
    class ImplWrapper:
        def __init__(self, impl):
            self._impl = impl
        
        def __getattr__(self, name):
            return getattr(self._impl, name)
    
    # Replace the module import
    original_module = test_module.py_mem_cache
    test_module.py_mem_cache = ImplWrapper(impl_module)
    
    try:
        # Load and run tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result
    finally:
        # Restore original
        test_module.py_mem_cache = original_module


def main():
    """Run comparison tests."""
    print("Memory Cache Implementation Comparison Test")
    print("=" * 70)
    
    # Try to load both implementations
    python_impl = load_implementation('python')
    c_impl = load_implementation('c')
    
    if not python_impl and not c_impl:
        print("\nERROR: No implementations available!")
        print("Please ensure mem_cache.py exists or C extension is compiled.")
        return 1
    
    results = {}
    
    # Test Python implementation
    if python_impl:
        results['Python'] = run_tests_for_implementation(python_impl, "Python")
    else:
        print("\nSkipping Python implementation (not available)")
    
    # Test C implementation
    if c_impl:
        results['C'] = run_tests_for_implementation(c_impl, "C")
    else:
        print("\nSkipping C implementation (not compiled)")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    all_passed = True
    for impl_name, result in results.items():
        status = "✓ PASSED" if result.wasSuccessful() else "✗ FAILED"
        print(f"{impl_name:15} {status:15} "
              f"({result.testsRun} tests, "
              f"{len(result.failures)} failures, "
              f"{len(result.errors)} errors)")
        if not result.wasSuccessful():
            all_passed = False
    
    # Equivalence check
    if len(results) == 2:
        py_result = results.get('Python')
        c_result = results.get('C')
        
        if py_result and c_result:
            if py_result.wasSuccessful() == c_result.wasSuccessful():
                print(f"\n✓ Both implementations show equivalent behavior")
            else:
                print(f"\n✗ WARNING: Implementations show different behavior!")
                all_passed = False
    
    print(f"{'='*70}\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
