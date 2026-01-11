#!/usr/bin/env python3
"""
Oberon Compiler - Executable Wrapper
This script allows running Oberon source files directly
"""

import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python oberon.py <source_file> [options]")
        print()
        print("Options:")
        print("  -c         Compile to LLVM IR only (create .ll file)")
        print("  -h         Show this help message")
        print()
        print("Examples:")
        print("  python oberon.py hello_world.oberon")
        print("  python oberon.py hello_world.oberon -c")
        sys.exit(1)
    
    source_file = sys.argv[1]
    compile_only = '-c' in sys.argv
    
    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found")
        sys.exit(1)
    
    from compiler import Compiler
    
    compiler = Compiler()
    messages, exe_path = compiler.compile_file(source_file, build_native=not compile_only)
    
    for msg in messages:
        print(msg)
    
    if exe_path:
        print(f"\nExecutable created: {exe_path}")
        sys.exit(0)
    else:
        if compile_only:
            print("\nLLVM IR file created successfully")
            sys.exit(0)
        else:
            print("\nProgram executed in interpreter mode")
            sys.exit(0)

if __name__ == "__main__":
    main()
