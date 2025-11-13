

import sys
import os
from typing import List, Optional
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from interpreter import Interpreter
from emitter import LLVMEmitter
import argparse

class Compiler:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.interpreter = Interpreter()
    
    def compile_file(self, filename: str) -> List[str]:
        """Compile a source file and return output"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                source = f.read()
            return self.compile_source(source)
        except FileNotFoundError:
            return [f"Error: File '{filename}' not found"]
        except Exception as e:
            return [f"Error reading file: {e}"]
    
    def compile_source(self, source: str) -> List[str]:
        """Compile source code and return output"""
        try:
            # Lexical analysis
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # Syntactic analysis
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Semantic analysis (create fresh instance to avoid state accumulation)
            semantic_analyzer = SemanticAnalyzer()
            errors = semantic_analyzer.analyze(ast)
            if errors:
                return [f"Semantic error: {error}" for error in errors]
            
            # If the user requested emission, produce LLVM IR instead of interpreting
            # For backward compatibility, default behaviour remains interpretation
            # The caller (main) decides when to write emitted IR to file.
            return ['OK']
            
        except Exception as e:
            return [f"Compilation error: {e}"]

def main():
    """Main entry point for the compiler"""
    parser = argparse.ArgumentParser(description='Compile Oberon-like source to LLVM IR or interpret')
    parser.add_argument('source', help='Source file')
    parser.add_argument('--interpret', dest='interpret', action='store_true', help='Interpret the source instead of emitting LLVM IR')
    args = parser.parse_args()

    filename = args.source
    compiler = Compiler()

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # parse and semantic-analyze
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser_ = Parser(tokens)
    ast = parser_.parse()
    semantic_analyzer = SemanticAnalyzer()
    errors = semantic_analyzer.analyze(ast)
    if errors:
        for err in errors:
            print(f"Semantic error: {err}")
        sys.exit(1)

    if args.interpret:
        # interpretation path
        interpreter = Interpreter()
        output = interpreter.interpret(ast)
        for line in output:
            print(line, end='')
    else:
        # default: emit LLVM IR
        emitter = LLVMEmitter()
        ll = emitter.emit_program(ast)
        outname = filename + '.ll'
        try:
            with open(outname, 'w', encoding='utf-8') as out:
                out.write(ll)
            print(f"Wrote LLVM IR to {outname}")
        except Exception as e:
            print(f"Error writing file: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
