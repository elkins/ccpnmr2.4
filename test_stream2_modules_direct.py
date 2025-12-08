#!/usr/bin/env python3
"""
Direct testing of Stream 2 Python implementations (avoiding module shadowing issues)

This tests each module by directly importing and running basic functionality tests.
"""

import sys
from pathlib import Path

# Setup path
script_dir = Path(__file__).parent
python_dir = script_dir / 'ccpnmr2.4' / 'python'
sys.path.insert(0, str(python_dir))

def test_list():
    """Test list.py implementation."""
    print("\n" + "="*80)
    print("Testing: list.py")
    print("="*80)

    try:
        from memops.c.python_impl.list import CcpnList, init_list, append_list

        # Test 1: Basic operations
        lst = CcpnList()
        assert lst.is_empty(), "New list should be empty"

        lst.append(1)
        lst.append(2)
        lst.append(3)
        assert len(lst) == 3, "List should have 3 elements"
        assert list(lst) == [1, 2, 3], "List contents should be [1, 2, 3]"

        # Test 2: Delete operations
        result = lst.delete_key(2)
        assert result is True, "Delete should return True for existing key"
        assert list(lst) == [1, 3], "List should be [1, 3] after deletion"

        # Test 3: C-compatible interface
        lst2 = init_list()
        append_list(lst2, 10)
        append_list(lst2, 20)
        assert len(lst2) == 2, "C interface list should have 2 elements"

        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_diag_dbl():
    """Test diag_dbl.py implementation."""
    print("\n" + "="*80)
    print("Testing: diag_dbl.py")
    print("="*80)

    try:
        import numpy as np
        from memops.c.python_impl.diag_dbl import diagonalize_symmetric

        # Test: 3x3 symmetric matrix
        matrix = np.array([
            [4.0, 1.0, 0.0],
            [1.0, 3.0, 1.0],
            [0.0, 1.0, 2.0]
        ], dtype=np.float64)

        eigenvalues, eigenvectors = diagonalize_symmetric(matrix)

        assert eigenvalues.shape == (3,), "Should return 3 eigenvalues"
        assert eigenvectors.shape == (3, 3), "Should return 3x3 eigenvector matrix"

        # Verify eigenvalues are sorted
        assert np.all(eigenvalues[:-1] <= eigenvalues[1:]), "Eigenvalues should be sorted"

        print(f"  ✓ Eigenvalues: {eigenvalues}")
        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_eigenvalue():
    """Test eigenvalue.py implementation."""
    print("\n" + "="*80)
    print("Testing: eigenvalue.py")
    print("="*80)

    try:
        import numpy as np
        from memops.c.python_impl.eigenvalue import compute_eigenvalues

        # Test: 3x3 symmetric matrix
        matrix = np.array([
            [2.0, 1.0, 0.0],
            [1.0, 3.0, 1.0],
            [0.0, 1.0, 2.0]
        ], dtype=np.float64)

        eigenvalues = compute_eigenvalues(matrix)

        assert eigenvalues.shape == (3,), "Should return 3 eigenvalues"
        assert np.all(np.isfinite(eigenvalues)), "All eigenvalues should be finite"

        print(f"  ✓ Eigenvalues: {eigenvalues}")
        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hash_list():
    """Test hash_list.py implementation."""
    print("\n" + "="*80)
    print("Testing: hash_list.py")
    print("="*80)

    try:
        from memops.c.python_impl.hash_list import HashList

        # Test: Basic hash list operations
        hash_list = HashList()

        # Add items
        hash_list.add("key1", "value1")
        hash_list.add("key2", "value2")
        hash_list.add("key3", "value3")

        # Retrieve items
        val = hash_list.get("key1")
        assert val == "value1", f"Expected 'value1', got {val}"

        val = hash_list.get("key2")
        assert val == "value2", f"Expected 'value2', got {val}"

        # Test non-existent key
        val = hash_list.get("nonexistent")
        assert val is None, "Non-existent key should return None"

        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gamma():
    """Test gamma.py implementation."""
    print("\n" + "="*80)
    print("Testing: gamma.py")
    print("="*80)

    try:
        from memops.c.python_impl.gamma import gamma_function, log_gamma

        # Test gamma function values
        # gamma(1) = 1
        val = gamma_function(1.0)
        assert abs(val - 1.0) < 1e-10, f"gamma(1) should be 1, got {val}"

        # gamma(2) = 1
        val = gamma_function(2.0)
        assert abs(val - 1.0) < 1e-10, f"gamma(2) should be 1, got {val}"

        # gamma(3) = 2
        val = gamma_function(3.0)
        assert abs(val - 2.0) < 1e-10, f"gamma(3) should be 2, got {val}"

        # Test log_gamma
        val = log_gamma(10.0)
        assert val > 0, "log_gamma(10) should be positive"

        print(f"  ✓ gamma(1) = {gamma_function(1.0)}")
        print(f"  ✓ gamma(3) = {gamma_function(3.0)}")
        print(f"  ✓ log_gamma(10) = {log_gamma(10.0)}")
        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fit1d():
    """Test fit1d.py implementation."""
    print("\n" + "="*80)
    print("Testing: fit1d.py")
    print("="*80)

    try:
        import numpy as np
        from memops.c.python_impl.fit1d import linear_fit

        # Test: Simple linear fit y = 2x + 3
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0], dtype=np.float64)
        y = np.array([3.0, 5.0, 7.0, 9.0, 11.0], dtype=np.float64)

        slope, intercept = linear_fit(x, y)

        assert abs(slope - 2.0) < 1e-10, f"Slope should be 2.0, got {slope}"
        assert abs(intercept - 3.0) < 1e-10, f"Intercept should be 3.0, got {intercept}"

        print(f"  ✓ Linear fit: y = {slope:.2f}x + {intercept:.2f}")
        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cpmg():
    """Test cpmg.py implementation."""
    print("\n" + "="*80)
    print("Testing: cpmg.py")
    print("="*80)

    try:
        import numpy as np
        from memops.c.python_impl.cpmg import calculate_cpmg

        # Test: CPMG calculation with simple parameters
        time_points = np.array([0.0, 0.01, 0.02, 0.03, 0.04], dtype=np.float64)
        r2_rate = 10.0  # Hz
        amplitude = 1.0

        intensities = calculate_cpmg(time_points, r2_rate, amplitude)

        assert intensities.shape == time_points.shape, "Output shape should match input"
        assert np.all(intensities >= 0), "All intensities should be non-negative"
        assert np.all(intensities <= amplitude), "Intensities should not exceed amplitude"

        # Check decay (later time points should have lower intensity)
        assert intensities[0] >= intensities[-1], "Signal should decay over time"

        print(f"  ✓ CPMG calculation: {len(time_points)} time points")
        print(f"  ✓ Intensities range: {intensities.min():.3f} to {intensities.max():.3f}")
        print("  ✓ All tests passed")
        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("STREAM 2: DIRECT MODULE TESTING")
    print("="*80)
    print("Testing Python implementations without pytest to avoid module shadowing\n")

    tests = [
        ("list", test_list),
        ("diag_dbl", test_diag_dbl),
        ("eigenvalue", test_eigenvalue),
        ("hash_list", test_hash_list),
        ("gamma", test_gamma),
        ("fit1d", test_fit1d),
        ("cpmg", test_cpmg),
    ]

    results = {}
    for name, test_func in tests:
        results[name] = test_func()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTotal modules: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {passed/total*100:.1f}%\n")

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
