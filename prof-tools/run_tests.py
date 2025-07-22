#!/usr/bin/env python
"""
Test runner script for Prof-Tools.

This script provides an easy way to run Prof-Tools tests with different options.

Usage:
    python run_tests.py [options]

Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --core             # Run only core tests
    python run_tests.py --ui               # Run only UI tests
    python run_tests.py --maya             # Run only Maya-dependent tests
    python run_tests.py --coverage         # Run with coverage reporting
"""

import sys
import os
import argparse
import subprocess

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run Prof-Tools tests')
    parser.add_argument('--core', action='store_true', help='Run only core tests')
    parser.add_argument('--ui', action='store_true', help='Run only UI tests')
    parser.add_argument('--maya', action='store_true', help='Run only Maya-dependent tests')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage reporting')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test path based on options
    if args.core:
        cmd.append('prof/tests/test_core/')
    elif args.ui:
        cmd.append('prof/tests/test_ui/')
    elif args.maya:
        cmd.extend(['-m', 'maya'])
    else:
        cmd.append('prof/tests/')
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(['--cov=prof', '--cov-report=html', '--cov-report=term-missing'])
    
    # Add verbose if requested
    if args.verbose:
        cmd.append('-v')
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest:")
        print("pip install pytest pytest-cov")
        return 1

if __name__ == '__main__':
    sys.exit(main())
