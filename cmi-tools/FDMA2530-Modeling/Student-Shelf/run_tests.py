#!/usr/bin/env python
"""
Simple test runner for FDMA2530 system tests
"""

if __name__ == "__main__":
    import unittest
    import sys
    import os
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import and run tests
    from tests.test_fdma2530_system import *
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules['tests.test_fdma2530_system'])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
