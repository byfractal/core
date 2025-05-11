#!/usr/bin/env python
"""
Script to run all test scripts.
This script runs all the other test scripts in the tests directory.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def run_test_script(script_path):
    """Run a test script using subprocess."""
    print(f"\n{'='*80}")
    print(f"Running test: {script_path}")
    print(f"{'='*80}")
    
    subprocess.run([sys.executable, script_path], check=False)

def main():
    """Main function to run all tests."""
    tests_dir = Path(__file__).parent
    
    # Find all test scripts (excluding this one and __init__.py)
    test_scripts = [
        path for path in tests_dir.glob("*.py")
        if path.name != "run_all_tests.py" and path.name != "__init__.py"
    ]
    
    # Sort test scripts to ensure consistent order
    test_scripts.sort()
    
    # Run each test script
    for script in test_scripts:
        run_test_script(script)
    
    print(f"\n{'='*80}")
    print("All tests completed!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 