#!/usr/bin/env python3
"""
Build script for Oberon subset compiler
Tests the compiler with example programs
"""

import os
import sys
import subprocess
from compiler import Compiler

def test_compiler():
    """Test the compiler with example programs"""
    compiler = Compiler()
    examples_dir = "examples"
    
    if not os.path.exists(examples_dir):
        print(f"Examples directory '{examples_dir}' not found")
        return False
    
    example_files = [
        "hello_world.oberon",
        "arithmetic.oberon", 
        "control_structures.oberon",
        "simple_procedures.oberon",
        "simple_arrays.oberon"
    ]
    
    print("Testing Oberon Subset Compiler")
    print("=" * 40)
    
    success_count = 0
    total_count = len(example_files)
    
    for example_file in example_files:
        filepath = os.path.join(examples_dir, example_file)
        if not os.path.exists(filepath):
            print(f"FAILED: {example_file}: File not found")
            continue
        
        print(f"\nTesting {example_file}...")
        print("-" * 30)
        
        try:
            output = compiler.compile_file(filepath)
            if output and not any("error" in line.lower() for line in output):
                print("SUCCESS: Compilation successful!")
                print("Output:")
                for line in output:
                    print(f"  {line}", end='')
                success_count += 1
            else:
                print("FAILED: Compilation failed!")
                for line in output:
                    print(f"  {line}")
        except Exception as e:
            print(f"ERROR: {e}")
    
    print(f"\n{'=' * 40}")
    print(f"Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed")
        return False

def main():
    """Main entry point"""
    print("Oberon Subset Compiler - Build Script")
    print("=====================================")
    
    # Check if we're in the right directory
    if not os.path.exists("compiler.py"):
        print("Error: compiler.py not found. Please run from the project root directory.")
        sys.exit(1)
    
    # Test the compiler
    success = test_compiler()
    
    if success:
        print("\nBuild completed successfully!")
        sys.exit(0)
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
