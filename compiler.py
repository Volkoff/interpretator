

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
        """Kompiluje zdrojovy kod na LLVM IR a pripadne na nativni spustitelny kod"""
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            semantic = SemanticAnalyzer()
            errors = semantic.analyze(ast)
            if errors:
                return [f"Semantic error: {err}" for err in errors], ""

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

            clang_path = shutil.which('clang') or shutil.which('clang.exe')
            if not clang_path:
                msg = f"Wrote LLVM IR to {ll_filename}.\n'clang' not found in PATH.\nFalling back to Python interpreter mode."
                
                from interpreter import Interpreter
                try:
                    interpreter = Interpreter()
                    output = interpreter.interpret(ast)
                    return [msg, "Program executed successfully in interpreter mode"] + output, ""
                except Exception as e:
                    return [msg, f"Interpreter error: {e}"], ""

            exe_filename = source_filename + ('.exe' if os.name == 'nt' else '')
            try:
                proc = subprocess.run(
                    [clang_path, ll_filename, '-o', exe_filename],
                    capture_output=True, text=True, check=False
                )
                if proc.returncode != 0:
                    error_msg = f"Clang error: {proc.stderr.strip()}"
                    fallback_msg = "Falling back to Python interpreter mode..."
                    
                    from interpreter import Interpreter
                    try:
                        interpreter = Interpreter()
                        output = interpreter.interpret(ast)
                        return [f"LLVM IR written to {ll_filename}", error_msg, fallback_msg, "Program executed successfully in interpreter mode"] + output, ""
                    except Exception as e:
                        return [f"LLVM IR written to {ll_filename}", error_msg, fallback_msg, f"Interpreter error: {e}"], ""
                
                success_msg = f"Successfully created executable: {exe_filename}"
                return [f"Wrote LLVM IR to {ll_filename}", success_msg], exe_filename

            except Exception as e:
                return [f"LLVM IR written to {ll_filename}", f"Error invoking clang: {e}"], ""

        except Exception as e:
            # Zachytí chyby z lexeru/parseru
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
