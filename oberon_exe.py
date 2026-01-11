#!/usr/bin/env python3
"""
Oberon Compiler - Standalone Executable Entry Point
This is used by PyInstaller to create oberon.exe
"""

import sys
import os

def show_help():
    """Display comprehensive help information"""
    print("=" * 70)
    print("OBERON COMPILER - STANDALONE EXECUTABLE")
    print("=" * 70)
    print()
    print("USAGE:")
    print("  oberon.exe [command] [options]")
    print()
    print("COMMANDS:")
    print("  <program.oberon>    Run an Oberon program")
    print("  -g, --gui           Launch interactive GUI IDE (with code editor)")
    print("  -c, --compile       Compile to LLVM IR only (creates .ll file)")
    print("  -h, --help          Show this help message")
    print("  -v, --version       Show version information")
    print()
    print("EXAMPLES:")
    print("  oberon.exe hello_world.oberon       # Run a program")
    print("  oberon.exe program.oberon -c        # Compile to LLVM IR")
    print("  oberon.exe -g                       # Launch GUI IDE")
    print("  oberon.exe -h                       # Show help")
    print()
    print("FEATURES:")
    print("  ✓ Syntax highlighting in GUI")
    print("  ✓ Real-time compilation and execution")
    print("  ✓ Example programs included")
    print("  ✓ No Python installation needed")
    print("  ✓ Works on Windows 7 and later (64-bit)")
    print()
    print("=" * 70)

def show_version():
    """Display version information"""
    print("Oberon Compiler v1.0 (Standalone)")
    print("Self-contained Windows Executable")
    print("GUI IDE with Syntax Highlighting")
    print("No Python installation required")

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    source_file = sys.argv[1].lower()
    
    # Handle help and version commands
    if source_file in ['-h', '--help', '-help', '/?']:
        show_help()
        sys.exit(0)
    
    if source_file in ['-v', '--version', 'version']:
        show_version()
        sys.exit(0)
    
    # Handle GUI command
    if source_file in ['-g', '--gui', 'gui']:
        try:
            from gui import main as gui_main
            gui_main()
            sys.exit(0)
        except ImportError as e:
            print(f"Error: Could not load GUI module: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error launching GUI: {e}")
            print("Make sure tkinter is available on your system")
            sys.exit(1)
    
    # Handle file execution
    source_file = sys.argv[1]  # Use original case
    compile_only = '-c' in sys.argv or '--compile' in sys.argv
    
    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found")
        print(f"Current directory: {os.getcwd()}")
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
