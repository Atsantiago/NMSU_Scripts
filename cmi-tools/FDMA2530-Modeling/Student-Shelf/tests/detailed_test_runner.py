#!/usr/bin/env python
"""
Detailed test runner for FDMA2530 system tests
"""

if __name__ == "__main__":
    import unittest
    import sys
    import os
    import traceback
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import and run tests
    try:
        from tests.test_fdma2530_system import *
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules['tests.test_fdma2530_system'])
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout, buffer=False)
        result = runner.run(suite)
        
        # Print detailed error information
        if result.errors:
            print("\n" + "="*50)
            print("DETAILED ERROR INFORMATION:")
            print("="*50)
            for test, error in result.errors:
                print(f"\nTest: {test}")
                print(f"Error: {error}")
                print("-" * 30)
        
        # Exit with appropriate code
        sys.exit(0 if result.wasSuccessful() else 1)
        
    except Exception as e:
        print(f"Failed to run tests: {e}")
        traceback.print_exc()
        sys.exit(1)
