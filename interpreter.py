from typing import Dict, List, Optional, Union, Any
from ast import *
from semantic_analyzer import Scope, Symbol

class RuntimeValue:
    def __init__(self, value: Union[int, float, str, List[Any]], type_: DataType):
        self.value = value
        self.type = type_

class Interpreter:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.procedures: Dict[str, ProcedureDeclaration] = {}
        self.output: List[str] = []
    
    def interpret(self, program: Program) -> List[str]:
        """Interpret the program and return output"""
        self.output.clear()
        
        # Store procedures and initialize variables
        for declaration in program.declarations:
            if isinstance(declaration, ProcedureDeclaration):
                self.procedures[declaration.name] = declaration
            elif isinstance(declaration, VarDeclaration):
                # Initialize variable with default value
                if declaration.array_size is not None:
                    # Initialize array
                    if declaration.type == DataType.INTEGER:
                        array_values = [0] * declaration.array_size
                        default_value = RuntimeValue(array_values, DataType.ARRAY)
                    elif declaration.type == DataType.REAL:
                        array_values = [0.0] * declaration.array_size
                        default_value = RuntimeValue(array_values, DataType.ARRAY)
                    elif declaration.type == DataType.STRING:
                        array_values = [""] * declaration.array_size
                        default_value = RuntimeValue(array_values, DataType.ARRAY)
                    else:
                        array_values = [0] * declaration.array_size
                        default_value = RuntimeValue(array_values, DataType.ARRAY)
                else:
                    if declaration.type == DataType.INTEGER:
                        default_value = RuntimeValue(0, DataType.INTEGER)
                    elif declaration.type == DataType.REAL:
                        default_value = RuntimeValue(0.0, DataType.REAL)
                    elif declaration.type == DataType.STRING:
                        default_value = RuntimeValue("", DataType.STRING)
                    else:
                        default_value = RuntimeValue(0, DataType.INTEGER)
                
                symbol = Symbol(declaration.name, declaration.type, is_constant=False)
                symbol.runtime_value = default_value
                self.current_scope.define(symbol)
        
        for statement in program.statements:
            self.execute_statement(statement)
        
        return self.output
    
    def execute_statement(self, statement: Statement):
        if isinstance(statement, Assignment):
            self.execute_assignment(statement)
        elif isinstance(statement, ProcedureCall):
            self.execute_procedure_call(statement)
        elif isinstance(statement, IfStatement):
            self.execute_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.execute_while_statement(statement)
        elif isinstance(statement, ForStatement):
            self.execute_for_statement(statement)
        elif isinstance(statement, CompoundStatement):
            self.execute_compound_statement(statement)
    
    def execute_assignment(self, assignment: Assignment):
        value = self.evaluate_expression(assignment.expression)
        
        if isinstance(assignment.variable, str):
            # Simple variable assignment
            self.set_variable(assignment.variable, value)
        elif isinstance(assignment.variable, ArrayAccess):
            # Array element assignment
            self.set_array_element(assignment.variable, value)
        else:
            raise TypeError(f"Invalid assignment target: {type(assignment.variable)}")
    
    def execute_procedure_call(self, call: ProcedureCall):
        if call.name == "Write":
            self.execute_write_procedure(call)
        elif call.name == "WriteLn":
            self.execute_writeln_procedure(call)
        elif call.name in self.procedures:
            self.execute_user_procedure(call)
        else:
            raise NameError(f"Procedure '{call.name}' not defined")
    
    def execute_write_procedure(self, call: ProcedureCall):
        if not call.arguments:
            raise TypeError("Write requires at least one argument")
        
        for arg in call.arguments:
            value = self.evaluate_expression(arg)
            self.output.append(str(value.value))
    
    def execute_writeln_procedure(self, call: ProcedureCall):
        if call.arguments:
            for arg in call.arguments:
                value = self.evaluate_expression(arg)
                self.output.append(str(value.value))
        self.output.append("\n")
    
    def execute_user_procedure(self, call: ProcedureCall):
        procedure = self.procedures[call.name]
        
        # Create new scope for procedure
        old_scope = self.current_scope
        self.current_scope = Scope(old_scope)
        
        # Set up parameters
        for i, (arg, param) in enumerate(zip(call.arguments, procedure.parameters)):
            value = self.evaluate_expression(arg)
            symbol = Symbol(param.name, param.type, is_constant=False)
            self.current_scope.define(symbol)
            self.set_variable(param.name, value)
        
        # Execute procedure body
        for statement in procedure.statements:
            self.execute_statement(statement)
        
        # Restore scope
        self.current_scope = old_scope
    
    def execute_if_statement(self, statement: IfStatement):
        condition = self.evaluate_expression(statement.condition)
        if condition.value:
            self.execute_statement(statement.then_statement)
        elif statement.else_statement:
            self.execute_statement(statement.else_statement)
    
    def execute_while_statement(self, statement: WhileStatement):
        while True:
            condition = self.evaluate_expression(statement.condition)
            if not condition.value:
                break
            self.execute_statement(statement.statement)
    
    def execute_for_statement(self, statement: ForStatement):
        start = self.evaluate_expression(statement.start)
        end = self.evaluate_expression(statement.end)
        
        if not isinstance(start.value, int) or not isinstance(end.value, int):
            raise TypeError("For loop bounds must be integers")
        
        # Set loop variable
        self.set_variable(statement.variable, RuntimeValue(start.value, DataType.INTEGER))
        
        while True:
            current = self.get_variable(statement.variable)
            if current.value > end.value:
                break
            
            self.execute_statement(statement.statement)
            
            # Increment loop variable
            self.set_variable(statement.variable, RuntimeValue(current.value + 1, DataType.INTEGER))
    
    def execute_compound_statement(self, statement: CompoundStatement):
        """Execute a compound statement"""
        for stmt in statement.statements:
            self.execute_statement(stmt)
    
    def evaluate_expression(self, expression: Expression) -> RuntimeValue:
        """Evaluate an expression and return its runtime value"""
        if isinstance(expression, Literal):
            return RuntimeValue(expression.value, expression.type)
        
        elif isinstance(expression, Variable):
            return self.get_variable(expression.name)
        
        elif isinstance(expression, ArrayAccess):
            array = self.get_variable(expression.name)
            index = self.evaluate_expression(expression.index)
            
            if not isinstance(index.value, int):
                raise TypeError("Array index must be integer")
            
            if not isinstance(array.value, list):
                raise TypeError(f"'{expression.name}' is not an array")
            
            if index.value < 0 or index.value >= len(array.value):
                raise IndexError(f"Array index {index.value} out of bounds")
            
            return RuntimeValue(array.value[index.value], array.type)
        
        elif isinstance(expression, FunctionCall):
            if expression.name in self.procedures:
                procedure = self.procedures[expression.name]
                if not procedure.return_type:
                    raise TypeError(f"'{expression.name}' is a procedure, not a function")
                
                # Create new scope for function
                old_scope = self.current_scope
                self.current_scope = Scope(old_scope)
                
                # Set up parameters
                for i, (arg, param) in enumerate(zip(expression.arguments, procedure.parameters)):
                    value = self.evaluate_expression(arg)
                    symbol = Symbol(param.name, param.type, is_constant=False)
                    self.current_scope.define(symbol)
                    self.set_variable(param.name, value)
                
                # Execute function body and collect return value
                # For simplicity, we'll assume the last statement is a return
                # In a real implementation, you'd need proper return handling
                result = None
                for statement in procedure.statements:
                    if isinstance(statement, Assignment) and statement.variable == "result":
                        result = self.evaluate_expression(statement.expression)
                        break
                
                # Restore scope
                self.current_scope = old_scope
                
                if result is None:
                    raise RuntimeError(f"Function '{expression.name}' did not return a value")
                
                return result
            else:
                raise NameError(f"Function '{expression.name}' not defined")
        
        elif isinstance(expression, BinaryExpression):
            left = self.evaluate_expression(expression.left)
            right = self.evaluate_expression(expression.right)
            
            return self.evaluate_binary_operation(left, expression.operator, right)
        
        elif isinstance(expression, UnaryExpression):
            operand = self.evaluate_expression(expression.operand)
            return self.evaluate_unary_operation(expression.operator, operand)
        
        else:
            raise TypeError(f"Unknown expression type: {type(expression)}")
    
    def evaluate_binary_operation(self, left: RuntimeValue, operator: str, right: RuntimeValue) -> RuntimeValue:
        """Evaluate a binary operation"""
        if operator == '+':
            if left.type == DataType.STRING or right.type == DataType.STRING:
                return RuntimeValue(str(left.value) + str(right.value), DataType.STRING)
            elif left.type == DataType.REAL or right.type == DataType.REAL:
                return RuntimeValue(float(left.value) + float(right.value), DataType.REAL)
            else:
                return RuntimeValue(int(left.value) + int(right.value), DataType.INTEGER)
        
        elif operator == '-':
            if left.type == DataType.REAL or right.type == DataType.REAL:
                return RuntimeValue(float(left.value) - float(right.value), DataType.REAL)
            else:
                return RuntimeValue(int(left.value) - int(right.value), DataType.INTEGER)
        
        elif operator == '*':
            if left.type == DataType.REAL or right.type == DataType.REAL:
                return RuntimeValue(float(left.value) * float(right.value), DataType.REAL)
            else:
                return RuntimeValue(int(left.value) * int(right.value), DataType.INTEGER)
        
        elif operator == '/':
            return RuntimeValue(float(left.value) / float(right.value), DataType.REAL)
        
        elif operator == 'DIV':
            return RuntimeValue(int(left.value) // int(right.value), DataType.INTEGER)
        
        elif operator == 'MOD':
            return RuntimeValue(int(left.value) % int(right.value), DataType.INTEGER)
        
        elif operator == '=':
            return RuntimeValue(1 if left.value == right.value else 0, DataType.INTEGER)
        
        elif operator == '#':
            return RuntimeValue(1 if left.value != right.value else 0, DataType.INTEGER)
        
        elif operator == '<':
            return RuntimeValue(1 if left.value < right.value else 0, DataType.INTEGER)
        
        elif operator == '<=':
            return RuntimeValue(1 if left.value <= right.value else 0, DataType.INTEGER)
        
        elif operator == '>':
            return RuntimeValue(1 if left.value > right.value else 0, DataType.INTEGER)
        
        elif operator == '>=':
            return RuntimeValue(1 if left.value >= right.value else 0, DataType.INTEGER)
        
        elif operator == 'AND':
            return RuntimeValue(1 if left.value and right.value else 0, DataType.INTEGER)
        
        elif operator == 'OR':
            return RuntimeValue(1 if left.value or right.value else 0, DataType.INTEGER)
        
        else:
            raise TypeError(f"Unknown binary operator: {operator}")
    
    def evaluate_unary_operation(self, operator: str, operand: RuntimeValue) -> RuntimeValue:
        """Evaluate a unary operation"""
        if operator == '+':
            return operand
        elif operator == '-':
            if operand.type == DataType.REAL:
                return RuntimeValue(-float(operand.value), DataType.REAL)
            else:
                return RuntimeValue(-int(operand.value), DataType.INTEGER)
        else:
            raise TypeError(f"Unknown unary operator: {operator}")
    
    def get_variable(self, name: str) -> RuntimeValue:
        """Get a variable's value"""
        symbol = self.current_scope.lookup(name)
        if not symbol:
            raise NameError(f"Variable '{name}' not defined")
        
        # For simplicity, we'll store values directly in the symbol
        # In a real implementation, you'd have a separate value store
        if not hasattr(symbol, 'runtime_value'):
            raise RuntimeError(f"Variable '{name}' not initialized")
        
        return symbol.runtime_value
    
    def set_variable(self, name: str, value: RuntimeValue):
        """Set a variable's value"""
        symbol = self.current_scope.lookup(name)
        if not symbol:
            raise NameError(f"Variable '{name}' not defined")
        
        if symbol.is_constant:
            raise RuntimeError(f"Cannot assign to constant '{name}'")
        
        # Store the runtime value in the symbol
        symbol.runtime_value = value
    
    def set_array_element(self, array_access: ArrayAccess, value: RuntimeValue):
        """Set an array element's value"""
        array = self.get_variable(array_access.name)
        index = self.evaluate_expression(array_access.index)
        
        if not isinstance(index.value, int):
            raise TypeError("Array index must be integer")
        
        if not isinstance(array.value, list):
            raise TypeError(f"'{array_access.name}' is not an array")
        
        if index.value < 0 or index.value >= len(array.value):
            raise IndexError(f"Array index {index.value} out of bounds")
        
        # Update the array element
        array.value[index.value] = value.value

if __name__ == "__main__":
    # Test the interpreter
    from lexer import Lexer
    from parser import Parser
    from semantic_analyzer import SemanticAnalyzer
    
    test_code = """
    MODULE Test;
    VAR x: INTEGER;
    BEGIN
        x := 42;
        Write(x);
    END Test.
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)
    
    if not errors:
        interpreter = Interpreter()
        output = interpreter.interpret(ast)
        print("Output:", "".join(output))
    else:
        print("Semantic errors:", errors)
