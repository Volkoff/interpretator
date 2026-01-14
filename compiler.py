

import sys
import os
import subprocess
import shutil
import argparse
from typing import List

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from c_emitter import CEmitter


class Compiler:
    def __init__(self, output_dir: str = 'output'):
        self.semantic_analyzer = SemanticAnalyzer()
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def compile_file(self, filename: str, build_native: bool = True) -> (List[str], str):
        """Kompiluje zdrojovy soubor na LLVM IR"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            base_path = os.path.splitext(filename)[0]
            return self.compile_source(source, source_filename=base_path, build_native=build_native)
        except FileNotFoundError:
            return [f"Error: File '{filename}' not found"], ""
        except Exception as e:
            return [f"Error reading file: {e}"], ""

    def compile_source(self, source: str, source_filename: str = 'program', build_native: bool = True) -> (List[str], str):
        """Compile Oberon source code to C, then to native executable using GCC"""
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            semantic = SemanticAnalyzer()
            errors = semantic.analyze(ast)
            if errors:
                return [f"Semantic error: {err}" for err in errors], ""

            # Emit C code
            emitter = CEmitter()
            c_code = emitter.emit_program(ast)
            c_filename = os.path.join(self.output_dir, source_filename + '.c')
            try:
                with open(c_filename, 'w', encoding='utf-8') as f:
                    f.write(c_code)
            except Exception as e:
                return [f"Error writing C file: {e}"], ""

            if not build_native:
                return [f"Wrote C code to {c_filename}"], ""

            # Find GCC (check multiple locations)
            gcc_path = shutil.which('gcc') or shutil.which('gcc.exe')
            
            # If not found in PATH, check MSYS2 installation
            if not gcc_path:
                msys2_paths = [
                    r"C:\msys64\mingw64\bin\gcc.exe",
                    r"C:\msys64\mingw32\bin\gcc.exe",
                    r"C:\msys32\mingw64\bin\gcc.exe",
                    r"C:\msys32\mingw32\bin\gcc.exe",
                ]
                for path in msys2_paths:
                    if os.path.exists(path):
                        gcc_path = path
                        break
            
            if not gcc_path:
                gcc_path = shutil.which('cc') or shutil.which('cc.exe')
            
            if not gcc_path:
                from interpreter import Interpreter
                try:
                    interpreter = Interpreter()
                    output = interpreter.interpret(ast)
                    return [f"C code written to {c_filename}", "'gcc' not found. Running in interpreter mode."] + output, ""
                except Exception as e:
                    return [f"C code written to {c_filename}", f"Interpreter error: {e}"], ""

            exe_filename = os.path.join(self.output_dir, source_filename + ('.exe' if os.name == 'nt' else ''))
            
            try:
                # Try to use wrapper first if available, fall back to direct gcc
                wrapper_path = os.path.join(os.path.dirname(__file__), 'compile_wrapper.bat')
                compiler_path = wrapper_path if os.path.exists(wrapper_path) else gcc_path
                
                # Compile C file to executable using GCC
                proc = subprocess.run(
                    [compiler_path, c_filename, '-o', exe_filename, '-Wall', '-Wextra'],
                    capture_output=True, text=True, check=False
                )
                
                # Check if compilation succeeded
                if proc.returncode == 0 and os.path.exists(exe_filename):
                    success_msg = f"Successfully created executable: {exe_filename}"
                    return [f"Wrote C code to {c_filename}", success_msg], exe_filename
                else:
                    # Compilation failed, show error and fall back to interpreter
                    error_msg = f"GCC error:\n{proc.stderr.strip()}" if proc.stderr else "GCC compilation failed"
                    
                    from interpreter import Interpreter
                    try:
                        interpreter = Interpreter()
                        output = interpreter.interpret(ast)
                        return [f"C code written to {c_filename}", error_msg, "Falling back to Python interpreter mode..."] + output, ""
                    except Exception as e:
                        return [f"C code written to {c_filename}", error_msg, f"Interpreter error: {e}"], ""

            except Exception as e:
                return [f"C code written to {c_filename}", f"Error during compilation: {e}"], ""

        except Exception as e:
            # Catch errors from lexer/parser
            return [f"Compilation error: {e}"], ""


def main():
    """Hlavni bod vstupu pro kompajler z prikazove radky"""
    parser = argparse.ArgumentParser(description='Compile Oberon source to a native executable.')
    parser.add_argument('source', help='Source file to compile.')
    parser.add_argument('-o', '--output', help='Output executable name.')
    args = parser.parse_args()

    compiler = Compiler()
    
    messages, exe_path = compiler.compile_file(args.source, build_native=True)

    for msg in messages:
        print(msg)

    if exe_path and args.output:
        try:
            shutil.move(exe_path, args.output)
            print(f"Renamed executable to {args.output}")
        except Exception as e:
            print(f"Error renaming executable: {e}")


if __name__ == "__main__":
    main()
