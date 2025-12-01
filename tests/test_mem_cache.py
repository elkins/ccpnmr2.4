"""
Unit tests for mem_cache module.

These tests are implementation-agnostic - they work with both
the C extension and pure Python implementations.
"""

import unittest
import sys
import os
import threading
import time

# Add repo root to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo_root)

# Import through the wrapper (will use Python or C depending on availability)
# Use importlib to handle the "ccpnmr2.4" directory name
import importlib.util
wrapper_path = os.path.join(repo_root, 'ccpnmr2.4', 'c', 'memops', 'global', 'py_mem_cache.py')
spec = importlib.util.spec_from_file_location('py_mem_cache', wrapper_path)
if spec and spec.loader:
    py_mem_cache = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(py_mem_cache)
else:
    raise ImportError(f"Could not load py_mem_cache from {wrapper_path}")


class TestMemCacheBasics(unittest.TestCase):
    """Test basic cache operations."""
    
    def setUp(self):
        """Create a fresh cache for each test."""
        # 1 MB cache
        self.cache = py_mem_cache.new_mem_cache(1024 * 1024, None, None)
    
    def tearDown(self):
        """Clean up cache."""
        py_mem_cache.delete_mem_cache(self.cache)
    
    def test_cache_creation(self):
        """Test cache can be created."""
        self.assertIsNotNone(self.cache)
        stats = self.cache.get_stats()
        self.assertEqual(stats['current_size'], 0)
        self.assertEqual(stats['num_entries'], 0)
    
    def test_add_single_object(self):
        """Test adding a single object."""
        obj = "test_object"
        size = 100
        
        result = py_mem_cache.add_mem_cache(self.cache, obj, size, None, None)
        self.assertTrue(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['current_size'], size)
        self.assertEqual(stats['num_entries'], 1)
        # Object should be locked when added
        self.assertEqual(stats['locked_entries'], 1)
    
    def test_add_multiple_objects(self):
        """Test adding multiple objects."""
        objects = [f"object_{i}" for i in range(5)]
        size_per_obj = 100
        
        for obj in objects:
            result = py_mem_cache.add_mem_cache(self.cache, obj, size_per_obj, None, None)
            self.assertTrue(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['current_size'], size_per_obj * len(objects))
        self.assertEqual(stats['num_entries'], len(objects))
    
    def test_remove_object(self):
        """Test removing an object."""
        obj = "test_object"
        size = 100
        
        # Add and unlock
        py_mem_cache.add_mem_cache(self.cache, obj, size, None, None)
        py_mem_cache.unlock_mem_cache(self.cache, obj)
        
        # Remove
        result = py_mem_cache.remove_mem_cache(self.cache, obj)
        self.assertTrue(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['current_size'], 0)
        self.assertEqual(stats['num_entries'], 0)
    
    def test_cannot_remove_locked_object(self):
        """Test that locked objects cannot be removed."""
        obj = "locked_object"
        size = 100
        
        # Add (automatically locked)
        py_mem_cache.add_mem_cache(self.cache, obj, size, None, None)
        
        # Try to remove (should fail because it's locked)
        result = py_mem_cache.remove_mem_cache(self.cache, obj)
        self.assertFalse(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['num_entries'], 1)
    
    def test_lock_unlock(self):
        """Test lock/unlock operations."""
        obj = "test_object"
        size = 100
        
        # Add (automatically locked)
        py_mem_cache.add_mem_cache(self.cache, obj, size, None, None)
        
        # Unlock
        result = py_mem_cache.unlock_mem_cache(self.cache, obj)
        self.assertTrue(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['locked_entries'], 0)
        
        # Lock again
        result = py_mem_cache.lock_mem_cache(self.cache, obj)
        self.assertTrue(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['locked_entries'], 1)
    
    def test_clear_cache(self):
        """Test clearing entire cache."""
        # Add multiple objects
        for i in range(5):
            py_mem_cache.add_mem_cache(self.cache, f"obj_{i}", 100, None, None)
        
        # Clear
        py_mem_cache.clear_mem_cache(self.cache)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['current_size'], 0)
        self.assertEqual(stats['num_entries'], 0)


class TestMemCacheEviction(unittest.TestCase):
    """Test cache eviction behavior."""
    
    def setUp(self):
        """Create a small cache to test eviction."""
        # Small cache: 1000 bytes
        self.cache = py_mem_cache.new_mem_cache(1000, None, None)
    
    def tearDown(self):
        """Clean up cache."""
        py_mem_cache.delete_mem_cache(self.cache)
    
    def test_eviction_when_full(self):
        """Test that unlocked items are evicted when cache is full."""
        # Add objects totaling 1200 bytes (exceeds 1000)
        # First 3 objects: 300 bytes each, unlock them
        for i in range(3):
            obj = f"unlocked_{i}"
            py_mem_cache.add_mem_cache(self.cache, obj, 300, None, None)
            py_mem_cache.unlock_mem_cache(self.cache, obj)
        
        # Add one more object (300 bytes) - should trigger eviction
        # This one stays locked
        py_mem_cache.add_mem_cache(self.cache, "trigger", 300, None, None)
        
        stats = self.cache.get_stats()
        # Should evict until <= 70% of max (700 bytes)
        self.assertLessEqual(stats['current_size'], 700)
        # At least one object should have been evicted
        self.assertLess(stats['num_entries'], 4)
    
    def test_locked_objects_not_evicted(self):
        """Test that locked objects are not evicted."""
        # Add objects keeping them locked
        for i in range(5):
            py_mem_cache.add_mem_cache(self.cache, f"locked_{i}", 250, None, None)
        
        stats = self.cache.get_stats()
        # All should still be present despite exceeding cache size
        self.assertEqual(stats['num_entries'], 5)
        self.assertEqual(stats['locked_entries'], 5)
    
    def test_resize_cache(self):
        """Test resizing cache."""
        # Add objects
        for i in range(3):
            obj = f"obj_{i}"
            py_mem_cache.add_mem_cache(self.cache, obj, 200, None, None)
            py_mem_cache.unlock_mem_cache(self.cache, obj)
        
        # Resize to smaller (should trigger eviction)
        result = py_mem_cache.resize_mem_cache(self.cache, 400)
        self.assertTrue(result)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['max_size'], 400)
        # Should have evicted to fit new size
        self.assertLessEqual(stats['current_size'], 280)  # 70% of 400


class TestMemCacheDeleteFunction(unittest.TestCase):
    """Test cleanup/delete functions."""
    
    def setUp(self):
        """Create cache for testing."""
        self.cache = py_mem_cache.new_mem_cache(1024 * 1024, None, None)
        self.cleanup_called = []
    
    def tearDown(self):
        """Clean up cache."""
        py_mem_cache.delete_mem_cache(self.cache)
    
    def cleanup_function(self, obj, data):
        """Track cleanup calls."""
        self.cleanup_called.append((obj, data))
    
    def test_delete_function_on_remove(self):
        """Test delete function is called when object is removed."""
        obj = "test_object"
        delete_data = "cleanup_data"
        
        # Add with delete function
        py_mem_cache.add_mem_cache(self.cache, obj, 100, 
                                    self.cleanup_function, delete_data)
        py_mem_cache.unlock_mem_cache(self.cache, obj)
        
        # Remove
        py_mem_cache.remove_mem_cache(self.cache, obj)
        
        # Verify cleanup was called
        self.assertEqual(len(self.cleanup_called), 1)
        self.assertEqual(self.cleanup_called[0], (obj, delete_data))
    
    def test_delete_function_on_clear(self):
        """Test delete function is called when cache is cleared."""
        # Add multiple objects with delete functions
        for i in range(3):
            py_mem_cache.add_mem_cache(self.cache, f"obj_{i}", 100,
                                        self.cleanup_function, f"data_{i}")
        
        # Clear cache
        py_mem_cache.clear_mem_cache(self.cache)
        
        # Verify cleanup called for all objects
        self.assertEqual(len(self.cleanup_called), 3)


class TestMemCacheThreadSafety(unittest.TestCase):
    """Test thread safety of cache operations."""
    
    def setUp(self):
        """Create cache for threading tests."""
        self.cache = py_mem_cache.new_mem_cache(10000, None, None)
        self.errors = []
    
    def tearDown(self):
        """Clean up cache."""
        py_mem_cache.delete_mem_cache(self.cache)
    
    def test_concurrent_additions(self):
        """Test adding objects from multiple threads."""
        num_threads = 5
        objects_per_thread = 10
        
        def add_objects(thread_id):
            try:
                for i in range(objects_per_thread):
                    obj = f"thread_{thread_id}_obj_{i}"
                    py_mem_cache.add_mem_cache(self.cache, obj, 10, None, None)
            except Exception as e:
                self.errors.append(e)
        
        threads = [threading.Thread(target=add_objects, args=(i,)) 
                   for i in range(num_threads)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Check no errors occurred
        self.assertEqual(len(self.errors), 0)
        
        stats = self.cache.get_stats()
        # Should have added all objects
        self.assertEqual(stats['num_entries'], num_threads * objects_per_thread)
    
    def test_concurrent_lock_unlock(self):
        """Test locking/unlocking from multiple threads."""
        # Add an object
        obj = "shared_object"
        py_mem_cache.add_mem_cache(self.cache, obj, 100, None, None)
        
        def toggle_lock(iterations):
            try:
                for _ in range(iterations):
                    py_mem_cache.lock_mem_cache(self.cache, obj)
                    time.sleep(0.001)
                    py_mem_cache.unlock_mem_cache(self.cache, obj)
            except Exception as e:
                self.errors.append(e)
        
        threads = [threading.Thread(target=toggle_lock, args=(10,)) 
                   for _ in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Check no errors occurred
        self.assertEqual(len(self.errors), 0)


class TestMemCacheAPICompatibility(unittest.TestCase):
    """Test API matches C implementation expectations."""
    
    def test_c_style_api_functions_exist(self):
        """Verify all C-style API functions are available."""
        functions = [
            'new_mem_cache',
            'delete_mem_cache',
            'clear_mem_cache',
            'add_mem_cache',
            'remove_mem_cache',
            'lock_mem_cache',
            'unlock_mem_cache',
            'resize_mem_cache',
            'check_mem_cache',
        ]
        
        for func_name in functions:
            self.assertTrue(hasattr(py_mem_cache, func_name),
                           f"Missing function: {func_name}")
            self.assertTrue(callable(getattr(py_mem_cache, func_name)),
                           f"Not callable: {func_name}")
    
    def test_object_oriented_api_exists(self):
        """Verify object-oriented API is available."""
        cache = py_mem_cache.new_mem_cache(1000, None, None)
        
        methods = ['add', 'remove', 'lock', 'unlock', 'resize', 'clear', 'delete']
        
        for method_name in methods:
            self.assertTrue(hasattr(cache, method_name),
                           f"Missing method: {method_name}")
            self.assertTrue(callable(getattr(cache, method_name)),
                           f"Not callable: {method_name}")
        
        py_mem_cache.delete_mem_cache(cache)


def run_tests(verbosity=2):
    """Run all tests with specified verbosity."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
