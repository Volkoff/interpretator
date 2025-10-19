"""
Semantic analyzer for Oberon subset compiler
Performs type checking and variable validation
"""

from typing import Dict, List, Optional, Set
from ast import *
from lexer import TokenType

class Symbol:
    def __init__(self, name: str, type_: DataType, is_constant: bool = False, value: Optional[Union[int, float, str]] = None):
        self.name = name
        self.type = type_
        self.is_constant = is_constant
        self.value = value

class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
    
    def define(self, symbol: Symbol):
        """Define a symbol in this scope"""
        if symbol.name in self.symbols:
            raise NameError(f"Symbol '{symbol.name}' already defined in this scope")
        self.symbols[symbol.name] = symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope and parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.procedures: Dict[str, ProcedureDeclaration] = {}
        self.errors: List[str] = []
        self._add_builtin_procedures()
    
    def _add_builtin_procedures(self):
        """Add built-in procedures to the procedure table"""
        # Write procedure - takes any number of arguments
        write_proc = ProcedureDeclaration("Write", [], None, [], [])
        self.procedures["Write"] = write_proc
        
        # WriteLn procedure - no arguments
        writeln_proc = ProcedureDeclaration("WriteLn", [], None, [], [])
        self.procedures["WriteLn"] = writeln_proc
    
    def analyze(self, program: Program) -> List[str]:
        """Perform semantic analysis on the program"""
        # Reset state for each new analysis
        self.errors.clear()
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.procedures.clear()
        self._add_builtin_procedures()
        
        try:
            # Analyze declarations
            for declaration in program.declarations:
                self.analyze_declaration(declaration)
            
            # Analyze statements
            for statement in program.statements:
                self.analyze_statement(statement)
            
        except Exception as e:
            self.errors.append(f"Semantic error: {e}")
        
        return self.errors
    
    def analyze_declaration(self, declaration: Declaration):
        """Analyze a declaration"""
        if isinstance(declaration, ConstDeclaration):
            self.analyze_const_declaration(declaration)
        elif isinstance(declaration, VarDeclaration):
            self.analyze_var_declaration(declaration)
        elif isinstance(declaration, ProcedureDeclaration):
            self.analyze_procedure_declaration(declaration)
    
    def analyze_const_declaration(self, declaration: ConstDeclaration):
        """Analyze a constant declaration"""
        # Analyze the constant value
        value_type = self.analyze_expression(declaration.value)
        
        # Create symbol for the constant
        symbol = Symbol(declaration.name, value_type, is_constant=True)
        if isinstance(declaration.value, Literal):
            symbol.value = declaration.value.value
        
        self.current_scope.define(symbol)
    
    def analyze_var_declaration(self, declaration: VarDeclaration):
        """Analyze a variable declaration"""
        # Determine the actual type
        if declaration.array_size is not None:
            # This is an array declaration
            symbol_type = DataType.ARRAY
        else:
            # This is a simple variable
            symbol_type = declaration.type
        
        symbol = Symbol(declaration.name, symbol_type, is_constant=False)
        self.current_scope.define(symbol)
    
    def analyze_procedure_declaration(self, declaration: ProcedureDeclaration):
        """Analyze a procedure declaration"""
        # Store procedure for later analysis
        self.procedures[declaration.name] = declaration
        
        # Create new scope for procedure
        old_scope = self.current_scope
        self.current_scope = Scope(old_scope)
        
        # Analyze parameters
        for parameter in declaration.parameters:
            symbol = Symbol(parameter.name, parameter.type, is_constant=False)
            self.current_scope.define(symbol)
        
        # Analyze local declarations
        for local_declaration in declaration.declarations:
            self.analyze_declaration(local_declaration)
        
        # Analyze procedure body
        for statement in declaration.statements:
            self.analyze_statement(statement)
        
        # Restore scope
        self.current_scope = old_scope
    
    def analyze_statement(self, statement: Statement):
        """Analyze a statement"""
        if isinstance(statement, Assignment):
            self.analyze_assignment(statement)
        elif isinstance(statement, ProcedureCall):
            self.analyze_procedure_call(statement)
        elif isinstance(statement, IfStatement):
            self.analyze_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.analyze_while_statement(statement)
        elif isinstance(statement, ForStatement):
            self.analyze_for_statement(statement)
        elif isinstance(statement, CompoundStatement):
            self.analyze_compound_statement(statement)
    
    def analyze_assignment(self, assignment: Assignment):
        """Analyze an assignment statement"""
        if isinstance(assignment.variable, str):
            # Simple variable assignment
            symbol = self.current_scope.lookup(assignment.variable)
            if not symbol:
                # Try global scope
                symbol = self.global_scope.lookup(assignment.variable)
                if not symbol:
                    raise NameError(f"Variable '{assignment.variable}' not defined")
            
            if symbol.is_constant:
                raise NameError(f"Cannot assign to constant '{assignment.variable}'")
            
            # Analyze expression type
            expression_type = self.analyze_expression(assignment.expression)
            
            # Check type compatibility
            if not self.is_type_compatible(symbol.type, expression_type):
                raise TypeError(f"Cannot assign {expression_type.value} to {symbol.type.value} variable '{assignment.variable}'")
        
        elif isinstance(assignment.variable, ArrayAccess):
            # Array element assignment
            symbol = self.current_scope.lookup(assignment.variable.name)
            if not symbol:
                # Try global scope
                symbol = self.global_scope.lookup(assignment.variable.name)
                if not symbol:
                    raise NameError(f"Array '{assignment.variable.name}' not defined")
            
            if symbol.is_constant:
                raise NameError(f"Cannot assign to constant array '{assignment.variable.name}'")
            
            # Check that it's an array
            if symbol.type != DataType.ARRAY:
                raise TypeError(f"'{assignment.variable.name}' is not an array")
            
            # Analyze index expression
            index_type = self.analyze_expression(assignment.variable.index)
            if index_type != DataType.INTEGER:
                raise TypeError("Array index must be integer")
            
            # Analyze expression type
            expression_type = self.analyze_expression(assignment.expression)
            
            # Check type compatibility (for now, assume array elements can be assigned any type)
            # In a more sophisticated implementation, you'd track the array element type
        
        else:
            raise TypeError(f"Invalid assignment target: {type(assignment.variable)}")
    
    def analyze_procedure_call(self, call: ProcedureCall):
        """Analyze a procedure call"""
        if call.name not in self.procedures:
            raise NameError(f"Procedure '{call.name}' not defined")
        
        procedure = self.procedures[call.name]
        
        # For built-in procedures, skip argument checking
        if call.name in ["Write", "WriteLn"]:
            # Analyze argument expressions but don't check types
            for arg in call.arguments:
                self.analyze_expression(arg)
            return
        
        # Check argument count
        if len(call.arguments) != len(procedure.parameters):
            raise TypeError(f"Procedure '{call.name}' expects {len(procedure.parameters)} arguments, got {len(call.arguments)}")
        
        # Check argument types
        for i, (arg, param) in enumerate(zip(call.arguments, procedure.parameters)):
            arg_type = self.analyze_expression(arg)
            if not self.is_type_compatible(param.type, arg_type):
                raise TypeError(f"Argument {i+1} of procedure '{call.name}' expects {param.type.value}, got {arg_type.value}")
    
    def analyze_if_statement(self, statement: IfStatement):
        """Analyze an if statement"""
        condition_type = self.analyze_expression(statement.condition)
        if condition_type != DataType.INTEGER:
            raise TypeError("If condition must be integer (boolean)")
        
        self.analyze_statement(statement.then_statement)
        if statement.else_statement:
            self.analyze_statement(statement.else_statement)
    
    def analyze_while_statement(self, statement: WhileStatement):
        """Analyze a while statement"""
        condition_type = self.analyze_expression(statement.condition)
        if condition_type != DataType.INTEGER:
            raise TypeError("While condition must be integer (boolean)")
        
        self.analyze_statement(statement.statement)
    
    def analyze_for_statement(self, statement: ForStatement):
        """Analyze a for statement"""
        # Check if loop variable exists
        symbol = self.current_scope.lookup(statement.variable)
        if not symbol:
            # Try global scope
            symbol = self.global_scope.lookup(statement.variable)
            if not symbol:
                raise NameError(f"Loop variable '{statement.variable}' not defined")
        
        # Analyze start and end expressions
        start_type = self.analyze_expression(statement.start)
        end_type = self.analyze_expression(statement.end)
        
        if start_type != DataType.INTEGER or end_type != DataType.INTEGER:
            raise TypeError("For loop bounds must be integers")
        
        self.analyze_statement(statement.statement)
    
    def analyze_compound_statement(self, statement: CompoundStatement):
        """Analyze a compound statement"""
        for stmt in statement.statements:
            self.analyze_statement(stmt)
    
    def analyze_expression(self, expression: Expression) -> DataType:
        """Analyze an expression and return its type"""
        if isinstance(expression, Literal):
            return expression.type
        
        elif isinstance(expression, Variable):
            symbol = self.current_scope.lookup(expression.name)
            if not symbol:
                # Try global scope
                symbol = self.global_scope.lookup(expression.name)
                if not symbol:
                    raise NameError(f"Variable '{expression.name}' not defined")
            return symbol.type
        
        elif isinstance(expression, ArrayAccess):
            symbol = self.current_scope.lookup(expression.name)
            if not symbol:
                # Try global scope
                symbol = self.global_scope.lookup(expression.name)
                if not symbol:
                    raise NameError(f"Array '{expression.name}' not defined")
            
            index_type = self.analyze_expression(expression.index)
            if index_type != DataType.INTEGER:
                raise TypeError("Array index must be integer")
            
            return symbol.type
        
        elif isinstance(expression, FunctionCall):
            if expression.name not in self.procedures:
                raise NameError(f"Function '{expression.name}' not defined")
            
            procedure = self.procedures[expression.name]
            if not procedure.return_type:
                raise TypeError(f"'{expression.name}' is a procedure, not a function")
            
            # Check arguments
            if len(expression.arguments) != len(procedure.parameters):
                raise TypeError(f"Function '{expression.name}' expects {len(procedure.parameters)} arguments, got {len(expression.arguments)}")
            
            for i, (arg, param) in enumerate(zip(expression.arguments, procedure.parameters)):
                arg_type = self.analyze_expression(arg)
                if not self.is_type_compatible(param.type, arg_type):
                    raise TypeError(f"Argument {i+1} of function '{expression.name}' expects {param.type.value}, got {arg_type.value}")
            
            return procedure.return_type
        
        elif isinstance(expression, BinaryExpression):
            left_type = self.analyze_expression(expression.left)
            right_type = self.analyze_expression(expression.right)
            
            # Check type compatibility for binary operations
            if not self.is_type_compatible(left_type, right_type):
                raise TypeError(f"Type mismatch in binary operation: {left_type.value} {expression.operator} {right_type.value}")
            
            # Return type based on operation
            if expression.operator in ['+', '-', '*', '/', 'DIV', 'MOD']:
                if left_type == DataType.REAL or right_type == DataType.REAL:
                    return DataType.REAL
                else:
                    return DataType.INTEGER
            elif expression.operator in ['AND', 'OR']:
                return DataType.INTEGER  # Boolean as integer
            else:  # Comparison operators
                return DataType.INTEGER  # Boolean as integer
        
        elif isinstance(expression, UnaryExpression):
            operand_type = self.analyze_expression(expression.operand)
            
            if expression.operator in ['+', '-']:
                return operand_type
            else:
                raise TypeError(f"Invalid unary operator: {expression.operator}")
        
        else:
            raise TypeError(f"Unknown expression type: {type(expression)}")
    
    def is_type_compatible(self, target_type: DataType, source_type: DataType) -> bool:
        """Check if two types are compatible for assignment or operation"""
        if target_type == source_type:
            return True
        
        # Integer can be assigned to Real
        if target_type == DataType.REAL and source_type == DataType.INTEGER:
            return True
        
        return False

if __name__ == "__main__":
    # Test the semantic analyzer
    from lexer import Lexer
    from parser import Parser
    
    test_code = """
    MODULE Test;
    VAR x: INTEGER;
    BEGIN
        x := 42;
    END Test.
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)
    
    if errors:
        print("Semantic errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print("Semantic analysis passed!")
