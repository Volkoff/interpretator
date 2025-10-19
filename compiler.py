

import sys
import os
from typing import List, Optional
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from interpreter import Interpreter

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
            
            # Interpretation (create fresh instance to avoid state accumulation)
            interpreter = Interpreter()
            output = interpreter.interpret(ast)
            return output
            
        except Exception as e:
            return [f"Compilation error: {e}"]

def main():
    """Main entry point for the compiler"""
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <source_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    compiler = Compiler()
    output = compiler.compile_file(filename)
    
    for line in output:
        print(line, end='')

if __name__ == "__main__":
    main()
