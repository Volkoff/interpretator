

import sys
import os
import subprocess
import shutil
import argparse
from typing import List

from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from emitter import LLVMEmitter


class Compiler:
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()

    def compile_file(self, filename: str, build_native: bool = True) -> (List[str], str):
        """
        Compiles a source file to LLVM IR and optionally to a native executable.
        Returns a tuple containing:
        - A list of status/error messages.
        - The path to the final executable (or an empty string if build fails).
        """
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
        """
        Compiles source code to LLVM IR and optionally to a native executable.
        Returns a tuple containing:
        - A list of status/error messages.
        - The path to the final executable (or an empty string if build fails).
        """
        try:
            # --- Fáze 1: Frontend (Lexer, Parser, Sémantická analýza) ---
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            semantic = SemanticAnalyzer()
            errors = semantic.analyze(ast)
            if errors:
                return [f"Semantic error: {err}" for err in errors], ""

            # --- Fáze 2: Backend (Generování LLVM IR) ---
            emitter = LLVMEmitter()
            ll_code = emitter.emit_program(ast)
            ll_filename = source_filename + '.ll'
            try:
                with open(ll_filename, 'w', encoding='utf-8') as f:
                    f.write(ll_code)
            except Exception as e:
                return [f"Error writing LLVM IR file: {e}"], ""

            if not build_native:
                return [f"Wrote LLVM IR to {ll_filename}"], ""

            # --- Fáze 3: Generování nativního kódu pomocí Clang ---
            clang_path = shutil.which('clang') or shutil.which('clang.exe')
            if not clang_path:
                msg = f"Wrote LLVM IR to {ll_filename}. 'clang' not found in PATH. Cannot produce native executable."
                return [msg], ""

            exe_filename = source_filename + ('.exe' if os.name == 'nt' else '')
            try:
                proc = subprocess.run(
                    [clang_path, ll_filename, '-o', exe_filename],
                    capture_output=True, text=True, check=False
                )
                if proc.returncode != 0:
                    error_msg = f"Clang error: {proc.stderr.strip()}"
                    return [f"LLVM IR written to {ll_filename}", error_msg], ""
                
                success_msg = f"Successfully created executable: {exe_filename}"
                return [f"Wrote LLVM IR to {ll_filename}", success_msg], exe_filename

            except Exception as e:
                return [f"LLVM IR written to {ll_filename}", f"Error invoking clang: {e}"], ""

        except Exception as e:
            # Zachytí chyby z lexeru/parseru
            return [f"Compilation error: {e}"], ""


def main():
    """Main entry point for the command-line compiler."""
    parser = argparse.ArgumentParser(description='Compile Oberon source to a native executable.')
    parser.add_argument('source', help='Source file to compile.')
    parser.add_argument('-o', '--output', help='Output executable name.')
    args = parser.parse_args()

    compiler = Compiler()
    
    # Zkompiluje soubor a vytvoří nativní kód
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
