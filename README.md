# Oberon Subset Compiler

A compiler for a subset of the Oberon programming language, implemented in Python. This compiler demonstrates the key components of a compiler: lexical analysis, parsing, semantic analysis, and interpretation.

## Features

### Supported Language Features

- **Data Types**: INTEGER, REAL, STRING, and arrays
- **Variables**: Global and local variable declarations
- **Constants**: Constant declarations with values
- **Procedures and Functions**: User-defined procedures with parameters and return values
- **Control Structures**: IF-THEN-ELSE, WHILE loops, FOR loops
- **Expressions**: Arithmetic, relational, and logical operations
- **Arrays**: One-dimensional arrays with integer indexing
- **Built-in Procedures**: Write, WriteLn for output

### Compiler Components

1. **Lexer** (`lexer.py`): Tokenizes source code into tokens
2. **Parser** (`parser.py`): Builds Abstract Syntax Tree (AST) from tokens
3. **Semantic Analyzer** (`semantic_analyzer.py`): Performs type checking and variable validation
4. **Interpreter** (`interpreter.py`): Executes the AST and produces output
5. **Main Compiler** (`compiler.py`): Coordinates all components

## Grammar

The language follows this EBNF grammar (see `grammar.ebnf`):

```
program = "MODULE" identifier ";" { declaration } "BEGIN" { statement } "END" identifier "." ;
```

## Usage

### Running the Compiler

```bash
python compiler.py <source_file>
```

### Example Programs

The `examples/` directory contains several example programs:

1. **hello_world.oberon**: Basic "Hello, World!" program
2. **arithmetic.oberon**: Demonstrates arithmetic operations
3. **control_structures.oberon**: Shows IF, WHILE, and FOR statements
4. **procedures.oberon**: Demonstrates procedure definitions and calls
5. **arrays.oberon**: Shows array usage and procedures with arrays

### Running Examples

```bash
# Hello World
python compiler.py examples/hello_world.oberon

# Arithmetic operations
python compiler.py examples/arithmetic.oberon

# Control structures
python compiler.py examples/control_structures.oberon

# Procedures
python compiler.py examples/procedures.oberon

# Arrays
python compiler.py examples/arrays.oberon
```

## Language Syntax

### Program Structure
```oberon
MODULE ModuleName;
VAR variable: TYPE;
PROCEDURE ProcName(param: TYPE): RETURN_TYPE;
BEGIN
    statements;
END ProcName;
BEGIN
    statements;
END ModuleName.
```

### Data Types
- `INTEGER`: Integer numbers
- `REAL`: Floating-point numbers  
- `STRING`: String literals
- `ARRAY[size] OF type`: Arrays

### Control Structures
```oberon
IF condition THEN
    statement;
ELSE
    statement;
END;

WHILE condition DO
    statement;
END;

FOR variable := start TO end DO
    statement;
END;
```

### Procedures
```oberon
PROCEDURE ProcName(param1, param2: TYPE): RETURN_TYPE;
VAR localVar: TYPE;
BEGIN
    statements;
END ProcName;
```

## Implementation Details

### Lexical Analysis
- Tokenizes source code into tokens (keywords, identifiers, literals, operators)
- Handles whitespace and comments
- Supports integer, real, and string literals

### Syntactic Analysis
- Recursive descent parser
- Builds AST with proper operator precedence
- Handles nested structures and scoping

### Semantic Analysis
- Type checking for assignments and operations
- Variable existence validation
- Parameter type checking for procedure calls
- Array bounds checking

### Interpretation
- Executes AST nodes in order
- Maintains variable scopes
- Handles procedure calls with parameter passing
- Produces text output

## Requirements

- Python 3.6+
- No external dependencies (pure Python implementation)

## Limitations

This is a simplified implementation with the following limitations:

- No file I/O operations (except for reading source files)
- No input operations (Read procedures)
- Limited error recovery
- No optimization
- Simple interpreter (not a code generator)

## Future Enhancements

- Code generation (assembly or bytecode)
- More sophisticated error messages
- Additional built-in procedures
- File I/O support
- Better optimization
- More comprehensive type system

## Academic Context

This compiler was developed as part of a compiler construction course, demonstrating:

- Lexical analysis and tokenization
- Syntax analysis and AST construction
- Semantic analysis and type checking
- Code interpretation and execution
- EBNF grammar specification
- Complete compiler pipeline

The implementation follows compiler construction principles and provides a foundation for understanding how programming languages are processed and executed.
