# Oberon Compiler - User Guide

A complete compiler for a subset of the Oberon programming language, implemented in Python.

## Quick Start

### Running an Oberon Program

```bash
python oberon.py examples/hello_world.oberon
```

### Compiling to LLVM IR

```bash
python oberon.py examples/hello_world.oberon -c
```

This creates a `.ll` file (LLVM Intermediate Representation) in the same directory.

## Supported Features

### Data Types
- `INTEGER` - 32-bit signed integers
- `REAL` - Floating-point numbers
- `STRING` - Text strings
- `ARRAY` - One-dimensional and multi-dimensional arrays

### Program Structure
```oberon
MODULE ProgramName;
  VAR x: INTEGER;
BEGIN
  x := 42;
  Write(x);
END ProgramName.
```

### Variables and Constants
```oberon
MODULE Example;
  CONST MAX = 100;
  VAR count: INTEGER;
BEGIN
  count := MAX;
END Example.
```

### Procedures and Functions
```oberon
PROCEDURE Add(a, b: INTEGER): INTEGER;
BEGIN
  RETURN a + b;
END Add;
```

### Control Structures
- **IF-THEN-ELSE**
- **WHILE loops**
- **FOR loops**

### Arrays
```oberon
VAR arr: ARRAY 10 OF INTEGER;
BEGIN
  arr[0] := 42;
  Write(arr[0]);
END.
```

### Multi-dimensional Arrays
```oberon
VAR matrix: ARRAY 3, 3 OF INTEGER;
BEGIN
  matrix[0, 1] := 5;
END.
```

## Example Programs

All examples are in the `examples/` directory:

| File | Description |
|------|-------------|
| `hello_world.oberon` | Basic output program |
| `arithmetic.oberon` | Integer and real arithmetic |
| `control_structures.oberon` | IF, WHILE, FOR statements |
| `procedures.oberon` | Procedure definitions and calls |
| `simple_procedures.oberon` | Basic procedure example |
| `arrays.oberon` | Single-dimensional arrays |
| `arrays_2d.oberon` | Two-dimensional arrays |
| `multidimensional_arrays.oberon` | N-dimensional arrays |
| `simple_arrays.oberon` | Array basics |
| `types_conversions.oberon` | Type handling |
| `indirect_recursion.oberon` | Mutual recursion (even/odd) |
| `nested_procedures.oberon` | Procedures within procedures |

## Usage Examples

### Run hello_world.oberon
```bash
python oberon.py examples/hello_world.oberon
```

Output:
```
Hello, World!
```

### Compile arithmetic.oberon to LLVM IR
```bash
python oberon.py examples/arithmetic.oberon -c
```

Creates: `examples/arithmetic.ll`

### Run with your own Oberon file
```bash
python oberon.py my_program.oberon
```

## Compiler Architecture

### 1. Lexer (`lexer.py`)
Converts source code characters into tokens:
```
"x := 42;" → IDENTIFIER('x') ASSIGN INTEGER_LITERAL('42') SEMICOLON
```

### 2. Parser (`parser.py`)
Builds Abstract Syntax Tree (AST) from tokens using recursive descent parsing

### 3. Semantic Analyzer (`semantic_analyzer.py`)
- Validates variable declarations
- Checks types
- Manages symbol tables and scopes
- Ensures no undefined variables

### 4. Interpreter (`interpreter.py`)
Directly executes the AST to produce output

### 5. LLVM Emitter (`emitter.py`)
Generates LLVM Intermediate Representation for potential native compilation

## System Requirements

- **Python 3.10+**
- No external dependencies required for interpreter mode
- (Optional) **Clang** for native executable generation

## Command Reference

### oberon.py
```
Usage: python oberon.py <source_file> [options]

Options:
  -c         Compile to LLVM IR only (creates .ll file)
  -h         Show help message

Examples:
  python oberon.py program.oberon      # Run in interpreter mode
  python oberon.py program.oberon -c   # Compile to LLVM IR
```

## Language Syntax

### Program Structure
```oberon
MODULE ModuleName;
  CONST constant = value;
  VAR variable: TYPE;
  
  PROCEDURE SubroutineName;
  BEGIN
    (* procedure body *)
  END SubroutineName;
  
BEGIN
  (* main program *)
END ModuleName.
```

### Variables
```oberon
VAR x, y: INTEGER;
VAR name: STRING;
VAR values: ARRAY 5 OF INTEGER;
```

### Types
- `INTEGER` - whole numbers
- `REAL` - decimals
- `STRING` - text
- `ARRAY n OF TYPE` - arrays with n elements

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `DIV`, `MOD`
- Relational: `=`, `#` (not equal), `<`, `>`, `<=`, `>=`
- Logical: `AND`, `OR`

### Built-in Procedures
- `Write(value)` - Output a value
- `WriteLn()` - Output newline

## Example Programs

### Hello World
```oberon
MODULE HelloWorld;
BEGIN
  Write("Hello, World!");
  WriteLn();
END HelloWorld.
```

### Factorial (Recursive)
```oberon
MODULE Factorial;
  
  PROCEDURE Factorial(n: INTEGER): INTEGER;
  BEGIN
    IF n <= 1 THEN
      RETURN 1;
    ELSE
      RETURN n * Factorial(n - 1);
    END;
  END Factorial;
  
BEGIN
  Write(Factorial(5));
  WriteLn();
END Factorial.
```

### Loop Example
```oberon
MODULE Loops;
  VAR i: INTEGER;
BEGIN
  FOR i := 1 TO 10 DO
    Write(i);
    Write(" ");
  END;
  WriteLn();
END Loops.
```

### Array Example
```oberon
MODULE Arrays;
  VAR arr: ARRAY 5 OF INTEGER;
      i: INTEGER;
BEGIN
  FOR i := 0 TO 4 DO
    arr[i] := i * 2;
  END;
  
  FOR i := 0 TO 4 DO
    Write(arr[i]);
    Write(" ");
  END;
  WriteLn();
END Arrays.
```

## Project Files

- `oberon.py` - Main executable wrapper
- `compiler.py` - Compilation orchestrator
- `lexer.py` - Lexical analyzer
- `parser.py` - Parser
- `semantic_analyzer.py` - Type checker and validator
- `interpreter.py` - AST interpreter
- `emitter.py` - LLVM IR generator
- `oberon_ast.py` - AST node definitions
- `gui.py` - GUI IDE (optional)
- `grammar.ebnf` - Formal language grammar
- `examples/` - Sample programs

## Execution Flow

```
Source Code (.oberon)
        ↓
    Lexer
        ↓
   Tokens
        ↓
    Parser
        ↓
      AST
        ↓
Semantic Analyzer
        ↓
   Validated AST
        ↓
   Interpreter / Emitter
        ↓
  Output / LLVM IR
```

## Testing

All 12 example programs pass comprehensive testing:
- ✅ hello_world.oberon
- ✅ arithmetic.oberon
- ✅ arrays.oberon
- ✅ arrays_2d.oberon
- ✅ control_structures.oberon
- ✅ indirect_recursion.oberon
- ✅ multidimensional_arrays.oberon
- ✅ nested_procedures.oberon
- ✅ procedures.oberon
- ✅ simple_arrays.oberon
- ✅ simple_procedures.oberon
- ✅ types_conversions.oberon

## GUI IDE

Run the graphical IDE:
```bash
python gui.py
```

Features:
- Syntax highlighting
- Real-time compilation
- Output display
- File management

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
